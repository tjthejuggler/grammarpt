# AI Tutor Anki Integration

This directory contains all scripts and files related to converting AI-generated study cards to Anki flashcards.

## Files Overview

### Core Scripts
- **`ai_tutor_json_to_anki.py`** - Main script to convert JSON flashcards to Anki cards
- **`ai_tutor_json_to_anki.sh`** - Shell wrapper for the main script

### Utility Scripts
- **`AnkiConnector.py`** - Core Anki connection and card creation functionality
- **`anki_utils.py`** - Anki connection utilities (start Anki, check if running)

### Problem Resolution Scripts
- **`fix_duplicate_cards.py`** - Bypasses duplicate detection to add cards (use when needed)
- **`remove_duplicate_cards.py`** - Removes duplicate cards from Anki deck
- **`anki_duplicate_cleaner.py`** - Alternative duplicate detection approach
- **`clean_json_duplicates.py`** - Removes duplicates from JSON files

### Data Files
- **`IBAC25cards.json`** - Clean bioacoustics study cards (78 unique cards)
- **`IBAC25cards_backup.json`** - Backup of original file with duplicates (91 cards)

## Usage

### Basic Usage
```bash
# Add cards from JSON to Anki
python ai_tutor_json_to_anki.py IBAC25cards.json

# Or use the shell wrapper
./ai_tutor_json_to_anki.sh IBAC25cards.json
```

### Problem Resolution
```bash
# If you get duplicate errors, use the fix script
python fix_duplicate_cards.py IBAC25cards.json

# Then clean up any actual duplicates created
python remove_duplicate_cards.py "...IBAC25" --live

# Clean duplicates from JSON files
python clean_json_duplicates.py input.json
```

## Troubleshooting

### "Cannot create note because it is a duplicate" Error
This happens when Anki's duplicate detection system has registered cards that weren't actually added to your deck.

**Solution:**
1. Use `fix_duplicate_cards.py` to bypass duplicate detection
2. Use `remove_duplicate_cards.py` to clean up any actual duplicates created

### JSON File Has Duplicates
Use `clean_json_duplicates.py` to remove duplicate cards from your JSON file while preserving the first occurrence of each unique card.

## File History
- **2025-08-28**: Resolved duplicate card issues and organized files
- **2025-08-28**: Cleaned IBAC25cards.json (91 → 78 unique cards)
- **2025-08-28**: Created comprehensive duplicate resolution toolkit

## Dependencies
- Python 3.x
- `requests` library
- Anki with AnkiConnect add-on installed
- AnkiConnect running on localhost:8765