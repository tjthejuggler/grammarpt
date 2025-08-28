#!/usr/bin/env python3
"""
Remove Duplicate Cards Script
Finds and removes duplicate cards from an Anki deck, keeping only the most recent copy of each.
"""

import sys
import requests
from collections import defaultdict
from anki_utils import ensure_anki_running

def get_all_notes_in_deck(deck_name):
    """Get all note IDs in the specified deck."""
    try:
        response = requests.post('http://localhost:8765', json={
            'action': 'findNotes',
            'version': 6,
            'params': {
                'query': f'deck:"{deck_name}"'
            }
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get('error'):
                print(f"Error finding notes: {result.get('error')}")
                return []
            return result.get('result', [])
        else:
            print(f"HTTP error finding notes: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"Exception finding notes: {e}")
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

def find_and_remove_duplicates(deck_name, dry_run=True):
    """Find and remove duplicate cards, keeping the most recent copy."""
    print(f"Searching for duplicate cards in deck: {deck_name}")
    print(f"Mode: {'DRY RUN (no changes will be made)' if dry_run else 'LIVE MODE (duplicates will be deleted)'}")
    print("-" * 60)
    
    # Get all notes in the deck
    note_ids = get_all_notes_in_deck(deck_name)
    if not note_ids:
        print("No notes found in the deck.")
        return True
    
    print(f"Found {len(note_ids)} total notes in deck")
    
    # Get detailed info for all notes
    print("Retrieving note details...")
    notes_info = get_notes_info(note_ids)
    if not notes_info:
        print("Could not retrieve note information.")
        return False
    
    # Group notes by front field content to identify duplicates
    front_to_notes = defaultdict(list)
    
    for note_info in notes_info:
        note_id = note_info.get('noteId')
        fields = note_info.get('fields', {})
        front_field = fields.get('Front', {}).get('value', '').strip()
        mod_time = note_info.get('mod', 0)  # Modification time
        
        if front_field:  # Only process notes with non-empty front fields
            front_to_notes[front_field].append({
                'note_id': note_id,
                'mod_time': mod_time,
                'note_info': note_info
            })
    
    # Find duplicates
    duplicates_to_delete = []
    unique_fronts = 0
    duplicate_groups = 0
    
    for front_text, notes_list in front_to_notes.items():
        unique_fronts += 1
        if len(notes_list) > 1:
            duplicate_groups += 1
            # Sort by modification time (newest first)
            notes_list.sort(key=lambda x: x['mod_time'], reverse=True)
            
            # Keep the newest, mark others for deletion
            keep_note = notes_list[0]
            delete_notes_list = notes_list[1:]
            
            print(f"\nDuplicate group found: {front_text[:50]}...")
            print(f"  Total copies: {len(notes_list)}")
            print(f"  Keeping newest: Note ID {keep_note['note_id']} (mod: {keep_note['mod_time']})")
            
            for delete_note in delete_notes_list:
                print(f"  Will delete: Note ID {delete_note['note_id']} (mod: {delete_note['mod_time']})")
                duplicates_to_delete.append(delete_note['note_id'])
    
    print(f"\nSummary:")
    print(f"  Total notes in deck: {len(notes_info)}")
    print(f"  Unique front texts: {unique_fronts}")
    print(f"  Duplicate groups found: {duplicate_groups}")
    print(f"  Duplicate notes to delete: {len(duplicates_to_delete)}")
    
    if duplicates_to_delete and not dry_run:
        print(f"\nDeleting {len(duplicates_to_delete)} duplicate notes...")
        if delete_notes(duplicates_to_delete):
            print(f"✓ Successfully deleted {len(duplicates_to_delete)} duplicate notes")
            print(f"✓ Your deck now has {len(notes_info) - len(duplicates_to_delete)} unique cards")
            return True
        else:
            print(f"✗ Failed to delete duplicate notes")
            return False
    elif duplicates_to_delete and dry_run:
        print(f"\nDRY RUN: Would delete {len(duplicates_to_delete)} duplicate notes")
        print("Run with --live to actually delete them")
        return True
    else:
        print(f"\nNo duplicate notes found to clean up")
        return True

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python remove_duplicate_cards.py <deck_name> [--live]")
        print("Example: python remove_duplicate_cards.py '...IBAC25'")
        print("Example: python remove_duplicate_cards.py '...IBAC25' --live")
        print("\nBy default, runs in DRY RUN mode. Use --live to actually delete duplicates.")
        sys.exit(1)
    
    deck_name = sys.argv[1]
    dry_run = '--live' not in sys.argv
    
    print(f"Remove Duplicate Cards Script")
    print(f"Target deck: {deck_name}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print("-" * 50)
    
    # Ensure Anki is running
    print(f"Ensuring Anki is running...")
    if not ensure_anki_running():
        print("Error: Could not start or connect to Anki. Please start Anki manually.", file=sys.stderr)
        sys.exit(1)
    
    # Find and remove duplicates
    success = find_and_remove_duplicates(deck_name, dry_run)
    
    if success:
        if dry_run:
            print(f"\n✓ Dry run completed successfully")
            print(f"Run with --live flag to actually delete the duplicate notes")
        else:
            print(f"\n🎉 Duplicate cleanup completed successfully!")
            print(f"Your deck now contains only unique cards")
    else:
        print(f"\n⚠️ Duplicate cleanup failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()