import os
from textblob import TextBlob

# Paths
EFF_LIST = "eff_large_wordlist.txt"
WORDS_DIR = "words"


def sieve_eff():
    if not os.path.exists(EFF_LIST):
        print(f"Error: {EFF_LIST} not found.")
        return

    print("Analyzing EFF list... this takes a moment.")

    # 1. Load the EFF list words
    eff_words = []
    with open(EFF_LIST, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if parts:
                eff_words.append(parts[-1].lower())

    # 2. Tag them in chunks (TextBlob is faster this way)
    blob = TextBlob(" ".join(eff_words))

    # Storage for found words
    found = {
        "JJ": set(),  # Adjectives
        "RB": set(),  # Adverbs
        "NN": set(),  # Nouns
        "VB": set()  # Verbs
    }

    for word, pos in blob.tags:
        if not word.isalpha(): continue
        # Map tags
        if pos.startswith('JJ'):
            found["JJ"].add(word)
        elif pos.startswith('RB'):
            found["RB"].add(word)
        elif pos.startswith('NN'):
            found["NN"].add(word)
        elif pos.startswith('VB'):
            found["VB"].add(word)

    # 3. Mapping to your files
    mapping = {
        "adjectives": ("adjectives.txt", "JJ"),
        "adverbs": ("adverbs.txt", "RB"),
        "nouns": ("medium_nouns.txt", "NN"),
        "verbs": ("verbs.txt", "VB")
    }

    # 4. Merge and overwrite _large files
    for label, (filename, tag) in mapping.items():
        path = os.path.join(WORDS_DIR, filename)

        # Load your existing hand-picked words
        existing = set()
        if os.path.exists(path):
            with open(path, 'r') as f:
                existing = {line.strip().lower() for line in f if line.strip()}

        # Combine your curated words with the new discoveries from EFF
        combined = sorted(list(existing.union(found[tag])))

        output_name = f"{label}_large.txt"
        with open(os.path.join(WORDS_DIR, output_name), 'w') as f:
            f.write('\n'.join(combined))

        print(f"Updated {label}: {len(existing)} -> {len(combined)} words")


if __name__ == "__main__":
    sieve_eff()