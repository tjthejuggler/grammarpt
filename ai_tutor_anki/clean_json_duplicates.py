#!/usr/bin/env python3
"""
Clean JSON Duplicates Script
Removes duplicate cards from a JSON file, keeping only the first occurrence of each unique front text.
"""

import sys
import json
import os
from collections import OrderedDict

def clean_json_duplicates(input_file, output_file=None):
    """Remove duplicates from JSON file, keeping first occurrence of each unique front text."""
    
    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        return False
    
    try:
        # Load the JSON file
        with open(input_file, 'r', encoding='utf-8') as f:
            cards = json.load(f)
        
        print(f"Original file: {len(cards)} cards")
        
        # Use OrderedDict to preserve order while removing duplicates
        seen_fronts = OrderedDict()
        duplicates_found = []
        
        for i, card in enumerate(cards):
            if 'front' not in card:
                print(f"Warning: Card {i+1} missing 'front' field, skipping")
                continue
                
            front_text = card['front'].strip()
            
            if front_text in seen_fronts:
                # This is a duplicate
                duplicates_found.append({
                    'index': i + 1,
                    'front': front_text[:60] + '...' if len(front_text) > 60 else front_text
                })
            else:
                # First occurrence, keep it
                seen_fronts[front_text] = card
        
        # Convert back to list
        unique_cards = list(seen_fronts.values())
        
        print(f"After deduplication: {len(unique_cards)} unique cards")
        print(f"Removed {len(duplicates_found)} duplicate cards")
        
        if duplicates_found:
            print("\nDuplicates removed:")
            for dup in duplicates_found:
                print(f"  Card {dup['index']}: {dup['front']}")
        
        # Determine output file
        if output_file is None:
            # Create backup of original
            backup_file = input_file.replace('.json', '_backup.json')
            os.rename(input_file, backup_file)
            output_file = input_file
            print(f"\nBackup created: {backup_file}")
        
        # Write cleaned JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(unique_cards, f, indent=2, ensure_ascii=False)
        
        print(f"Cleaned file saved: {output_file}")
        return True
        
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file: {e}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python clean_json_duplicates.py <input_json_file> [output_json_file]")
        print("Example: python clean_json_duplicates.py IBAC25cards.json")
        print("Example: python clean_json_duplicates.py IBAC25cards.json IBAC25cards_clean.json")
        print("\nIf no output file is specified, the input file will be overwritten (with backup)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    print(f"Clean JSON Duplicates Script")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file or input_file + ' (with backup)'}")
    print("-" * 50)
    
    success = clean_json_duplicates(input_file, output_file)
    
    if success:
        print(f"\n🎉 JSON file cleaned successfully!")
    else:
        print(f"\n⚠️ Failed to clean JSON file.")
        sys.exit(1)

if __name__ == "__main__":
    main()