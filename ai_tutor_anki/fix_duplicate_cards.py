#!/usr/bin/env python3
"""
Fix Duplicate Cards Script
Temporarily allows duplicates to add cards that are stuck in Anki's duplicate detection.
"""

import sys
import json
import os
import requests
from AnkiConnector import AnkiConnector
from anki_utils import ensure_anki_running

def load_json_cards(json_path):
    """Load and parse JSON cards from file (simplified version)."""
    if not os.path.exists(json_path):
        print(f"Error: File '{json_path}' not found.", file=sys.stderr)
        return None
    
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
        
        if not cards:
            print("Error: No valid cards found in JSON.", file=sys.stderr)
            return None
            
        return cards
        
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse JSON: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: Failed to load JSON file: {e}", file=sys.stderr)
        return None

def create_deck_if_not_exists(deck_name):
    """Create the deck if it doesn't exist."""
    try:
        # Check if deck exists
        response = requests.post('http://localhost:8765', json={
            'action': 'deckNames',
            'version': 6
        })
        
        if response.status_code == 200:
            deck_names = response.json().get('result', [])
            if deck_name not in deck_names:
                print(f"Deck '{deck_name}' not found. Creating it...")
                # Create the deck
                create_response = requests.post('http://localhost:8765', json={
                    'action': 'createDeck',
                    'version': 6,
                    'params': {
                        'deck': deck_name
                    }
                })
                
                if create_response.status_code == 200:
                    result = create_response.json()
                    if result.get('error'):
                        print(f"Error creating deck: {result.get('error')}")
                        return False
                    else:
                        print(f"Successfully created deck '{deck_name}'")
                        return True
                else:
                    print(f"Failed to create deck. HTTP status: {create_response.status_code}")
                    return False
            else:
                print(f"Deck '{deck_name}' already exists.")
                return True
        else:
            print(f"Failed to check existing decks. HTTP status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error checking/creating deck: {e}")
        return False

def add_cards_with_duplicates_allowed(cards, deck_name="...IBAC25"):
    """Add all cards to the specified Anki deck with duplicates allowed."""
    print(f"Ensuring Anki is running...")
    if not ensure_anki_running():
        print("Error: Could not start or connect to Anki. Please start Anki manually.", file=sys.stderr)
        return False
    
    # Create deck if it doesn't exist
    if not create_deck_if_not_exists(deck_name):
        print(f"Error: Could not create or access deck '{deck_name}'", file=sys.stderr)
        return False
    
    print(f"Connecting to Anki deck: {deck_name}")
    print(f"IMPORTANT: Using allow_duplicate=True to bypass duplicate detection")
    
    # Use AnkiConnector with allow_duplicate=True
    connector = AnkiConnector(deck_name=deck_name, note_type="Basic", allow_duplicate=True)
    
    success_count = 0
    failed_count = 0
    
    for i, card in enumerate(cards, 1):
        front = card["front"]
        back = card["back"]
        source = card.get("source", "")
        
        print(f"Adding card {i}/{len(cards)}: {front[:50]}...")
        
        try:
            success = connector.add_card(front, back, source)
            if success:
                success_count += 1
                print(f"  ✓ Successfully added card {i}")
            else:
                failed_count += 1
                print(f"  ✗ Failed to add card {i}")
        except Exception as e:
            failed_count += 1
            print(f"  ✗ Error adding card {i}: {e}")
    
    print(f"\nResults:")
    print(f"  Successfully added: {success_count} cards")
    print(f"  Failed to add: {failed_count} cards")
    print(f"  Total processed: {len(cards)} cards")
    
    if success_count > 0:
        print(f"\n🎉 Successfully added {success_count} cards to Anki deck '{deck_name}'!")
        print(f"Note: These cards were added with duplicate detection disabled.")
        print(f"Future cards will use normal duplicate detection unless you modify the script.")
    
    return failed_count == 0

def main():
    """Main function to process JSON file and add cards to Anki with duplicates allowed."""
    if len(sys.argv) < 2:
        print("Usage: python fix_duplicate_cards.py <json_file_path> [deck_name]")
        print("Example: python fix_duplicate_cards.py IBAC25cards.json")
        print("Example: python fix_duplicate_cards.py IBAC25cards.json MyCustomDeck")
        print("\nThis script temporarily allows duplicates to bypass the duplicate detection issue.")
        sys.exit(1)
    
    json_path = sys.argv[1]
    deck_name = sys.argv[2] if len(sys.argv) > 2 else "...IBAC25"
    
    print(f"Fix Duplicate Cards Script")
    print(f"JSON file: {json_path}")
    print(f"Target deck: {deck_name}")
    print(f"Mode: ALLOW DUPLICATES (bypasses duplicate detection)")
    print("-" * 50)
    
    # Load cards from JSON
    cards = load_json_cards(json_path)
    if cards is None:
        sys.exit(1)
    
    print(f"Loaded {len(cards)} valid cards from JSON file.")
    
    # Add cards to Anki with duplicates allowed
    success = add_cards_with_duplicates_allowed(cards, deck_name)
    
    if success:
        print(f"\n🎉 All cards successfully added to Anki deck '{deck_name}'!")
        sys.exit(0)
    else:
        print(f"\n⚠️  Some cards failed to be added. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()