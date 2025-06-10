import nltk

try:
    print("Checking for WordNet...")
    nltk.data.find('corpora/wordnet.zip')
    print("WordNet already downloaded.")
except LookupError:
    print("WordNet not found. Downloading...")
    nltk.download('wordnet')
    print("WordNet downloaded.")
except Exception as e:
    print(f"An error occurred: {e}")
    print("Trying to download 'omw-1.4' as well, which is often needed with WordNet.")

try:
    print("Checking for OMW (Open Multilingual Wordnet)...")
    nltk.data.find('corpora/omw-1.4.zip')
    print("OMW 1.4 already downloaded.")
except LookupError:
    print("OMW 1.4 not found. Downloading...")
    nltk.download('omw-1.4') # Open Multilingual Wordnet, often good to have with wordnet
    print("OMW 1.4 downloaded.")
except Exception as e:
    print(f"An error occurred while checking/downloading OMW: {e}")

print("Setup complete.")