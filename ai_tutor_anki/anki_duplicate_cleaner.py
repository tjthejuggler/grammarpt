#!/usr/bin/env python3
"""
Anki Duplicate Cleaner
Finds and removes "ghost" duplicate cards that exist in Anki's duplicate detection
but aren't actually in your deck, allowing you to re-add them properly.
"""

import sys
import json
import requests
from anki_utils import ensure_anki_running

def find_notes_by_content(front_text, deck_name="...IBAC25"):
    """Find notes in Anki that match the front text content."""
    try:
        # Search for notes with matching front field content
        response = requests.post('http://localhost:8765', json={
            'action': 'findNotes',
            'version': 6,
            'params': {
                'query': f'deck:"{deck_name}" Front:"{front_text}"'
            }
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get('error'):
                print(f"Error searching for notes: {result.get('error')}")
                return []
            return result.get('result', [])
        else:
            print(f"HTTP error searching for notes: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Exception searching for notes: {e}")
        return []

def get_notes_info(note_ids):
    """Get detailed information about specific notes."""
    try:
        response = requests.post('http://localhost:8765', json={
            'action': 'notesInfo',
            'version': 6,
            'params': {
                'notes': note_ids
            }
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get('error'):
                print(f"Error getting notes info: {result.get('error')}")
                return []
            return result.get('result', [])
        else:
            print(f"HTTP error getting notes info: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Exception getting notes info: {e}")
        return []

def delete_notes(note_ids):
    """Delete specific notes from Anki."""
    try:
        response = requests.post('http://localhost:8765', json={
            'action': 'deleteNotes',
            'version': 6,
            'params': {
                'notes': note_ids
            }
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get('error'):
                print(f"Error deleting notes: {result.get('error')}")
                return False
            return True
        else:
            print(f"HTTP error deleting notes: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Exception deleting notes: {e}")
        return False

def find_and_clean_duplicates(cards, deck_name="...IBAC25", dry_run=True):
    """Find and optionally clean duplicate cards."""
    print(f"Searching for duplicate cards in deck: {deck_name}")
    print(f"Mode: {'DRY RUN (no changes will be made)' if dry_run else 'LIVE MODE (cards will be deleted)'}")
    print("-" * 60)
    
    found_duplicates = []
    
    for i, card in enumerate(cards, 1):
        front = card["front"]
        print(f"Checking card {i}/{len(cards)}: {front[:50]}...")
        
        # Search for existing notes with this front text
        note_ids = find_notes_by_content(front, deck_name)
        
        if note_ids:
            print(f"  Found {len(note_ids)} existing note(s) with matching front text")
            
            # Get detailed info about these notes
            notes_info = get_notes_info(note_ids)
            
            for note_info in notes_info:
                note_id = note_info.get('noteId')
                fields = note_info.get('fields', {})
                front_field = fields.get('Front', {}).get('value', '')
                back_field = fields.get('Back', {}).get('value', '')
                
                print(f"    Note ID: {note_id}")
                print(f"    Front: {front_field[:50]}...")
                print(f"    Back: {back_field[:50]}...")
                
                found_duplicates.append({
                    'note_id': note_id,
                    'front': front_field,
                    'back': back_field,
                    'original_card': card
                })
        else:
            print(f"  No existing notes found (this is unexpected if you're getting duplicate errors)")
    
    print(f"\nSummary:")
    print(f"  Total cards checked: {len(cards)}")
    print(f"  Duplicate notes found: {len(found_duplicates)}")
    
    if found_duplicates and not dry_run:
        print(f"\nDeleting {len(found_duplicates)} duplicate notes...")
        note_ids_to_delete = [dup['note_id'] for dup in found_duplicates]
        
        if delete_notes(note_ids_to_delete):
            print(f"✓ Successfully deleted {len(found_duplicates)} duplicate notes")
            return True
        else:
            print(f"✗ Failed to delete duplicate notes")
            return False
    elif found_duplicates and dry_run:
        print(f"\nDRY RUN: Would delete {len(found_duplicates)} duplicate notes")
        print("Run with --live to actually delete them")
        return True
    else:
        print(f"\nNo duplicate notes found to clean up")
        return True

def load_json_cards(json_path):
    """Load cards from JSON file (simplified version)."""
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Validate cards have required fields
        cards = []
        for item in data:
            if "front" in item and "back" in item:
                cards.append(item)
            else:
                print(f"Warning: Skipping invalid card (missing front/back): {item}")
        
        return cards
        
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return None

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python anki_duplicate_cleaner.py <json_file_path> [deck_name] [--live]")
        print("Example: python anki_duplicate_cleaner.py IBAC25cards.json")
        print("Example: python anki_duplicate_cleaner.py IBAC25cards.json '...IBAC25' --live")
        print("\nBy default, runs in DRY RUN mode. Use --live to actually delete duplicates.")
        sys.exit(1)
    
    json_path = sys.argv[1]
    deck_name = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else "...IBAC25"
    dry_run = '--live' not in sys.argv
    
    print(f"Anki Duplicate Cleaner")
    print(f"JSON file: {json_path}")
    print(f"Target deck: {deck_name}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print("-" * 50)
    
    # Ensure Anki is running
    print(f"Ensuring Anki is running...")
    if not ensure_anki_running():
        print("Error: Could not start or connect to Anki. Please start Anki manually.", file=sys.stderr)
        sys.exit(1)
    
    # Load cards from JSON
    cards = load_json_cards(json_path)
    if cards is None:
        sys.exit(1)
    
    print(f"Loaded {len(cards)} cards from JSON file.")
    
    # Find and clean duplicates
    success = find_and_clean_duplicates(cards, deck_name, dry_run)
    
    if success:
        if dry_run:
            print(f"\n✓ Dry run completed successfully")
            print(f"Run with --live flag to actually delete the duplicate notes")
        else:
            print(f"\n🎉 Duplicate cleanup completed successfully!")
            print(f"You should now be able to add your cards using the original script")
    else:
        print(f"\n⚠️ Duplicate cleanup failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()