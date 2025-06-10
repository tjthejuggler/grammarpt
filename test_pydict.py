from PyDictionary import PyDictionary

dictionary = PyDictionary()
words_to_test = ["keyboard", "hello", "house", "ubiquitous", "example"]

for word in words_to_test:
    print(f"--- Looking up: {word} ---")
    meaning = dictionary.meaning(word)
    if meaning:
        print(meaning)
        # For prettier output:
        # for part_of_speech, defs in meaning.items():
        #     print(f"  {part_of_speech}:")
        #     for d in defs:
        #         print(f"    - {d}")
    else:
        print(f"No definitions found for '{word}'.")
    print("-" * 30)