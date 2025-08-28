# GrammarPT - Anki Integration Tools

A collection of tools for integrating various content sources with Anki flashcards.

## Scripts

### AI Tutor JSON to Anki (`ai_tutor_json_to_anki.py`)

**Added: 2025-08-25**

Automatically converts JSON flashcards to Anki cards and adds them to a specified deck.

#### Features
- Automatically creates the target deck if it doesn't exist
- Processes JSON files with `front`, `back`, and optional `source` fields
- Adds source information to the back of cards with "Source: " label
- Handles markdown code blocks (```json ... ```)
- Provides detailed progress feedback
- Validates card data before processing

#### Usage

**Python script:**
```bash
python3 ai_tutor_json_to_anki.py <json_file> [deck_name]
```

**Shell wrapper:**
```bash
./ai_tutor_json_to_anki.sh <json_file> [deck_name]
```

#### Examples

```bash
# Add cards to default ...IBAC25 deck
python3 ai_tutor_json_to_anki.py my_cards.json

# Add cards to custom deck
python3 ai_tutor_json_to_anki.py my_cards.json "My Study Deck"

# Using shell wrapper
./ai_tutor_json_to_anki.sh my_cards.json
```

#### JSON Format

The script expects JSON files in the following format:

```json
[
  {
    "front": "Question or prompt text",
    "back": "Answer or explanation text",
    "source": "Optional source reference"
  },
  {
    "front": "Another question",
    "back": "Another answer",
    "source": "Another source"
  }
]
```

#### Requirements
- Anki must be installed and AnkiConnect addon enabled
- Python 3 with `requests` library
- The script will automatically start Anki if not running

### Other Tools

- [`AnkiConnector.py`](AnkiConnector.py) - Core Anki integration class
- [`json_to_anki.py`](json_to_anki.py) - Interactive JSON card reviewer
- [`clipboard_to_anki.py`](clipboard_to_anki.py) - Clipboard content to Anki
- [`anki_utils.py`](anki_utils.py) - Anki utility functions

## Installation

1. Install Anki and the AnkiConnect addon
2. Ensure Python 3 is installed with the `requests` library
3. Make scripts executable: `chmod +x *.py *.sh`

## Last Updated
2025-08-25 - Added AI Tutor JSON to Anki script