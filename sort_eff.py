#!/usr/bin/env python3
"""
Sort EFF wordlist by part of speech using suffix patterns + WordNet
Creates _large.txt files by combining existing curated words with categorized EFF words
"""

import os
from collections import defaultdict

# Paths
EFF_LIST = "eff_large_wordlist.txt"
WORDS_DIR = "words"

# Strong suffix patterns (highly reliable)
SUFFIX_RULES = {
    'noun': [
        'ness', 'ment', 'tion', 'sion', 'ance', 'ence', 'ship', 'hood',
        'ity', 'ty', 'ism', 'ist', 'ery', 'ary', 'age', 'dom'
    ],
    'verb': [
        'ify', 'ize', 'ise', 'ate'
    ],
    'adjective': [
        'able', 'ible', 'ful', 'less', 'ous', 'ious', 'eous', 'ive',
        'al', 'ic', 'ical', 'ish', 'like', 'some'
    ],
    'adverb': [
        'ly'
    ]
}

def get_pos_by_suffix(word):
    """Return POS based on suffix, or None if no clear match"""
    word_lower = word.lower()

    # Check noun suffixes first (most reliable)
    for suffix in SUFFIX_RULES['noun']:
        if word_lower.endswith(suffix) and len(word) > len(suffix) + 2:
            return 'noun'

    # Check adverb -ly (but not words like "holy", "ugly" etc)
    if word_lower.endswith('ly') and len(word) > 4:
        # Exclude adjectives that happen to end in -ly
        base = word_lower[:-2]
        if not any(base.endswith(s) for s in ['ug', 'hol', 'jol', 'ear', 'oil', 'dai']):
            return 'adverb'

    # Check adjective suffixes
    for suffix in SUFFIX_RULES['adjective']:
        if word_lower.endswith(suffix) and len(word) > len(suffix) + 2:
            return 'adjective'

    # Check verb suffixes (least reliable, many conflicts)
    for suffix in SUFFIX_RULES['verb']:
        if word_lower.endswith(suffix) and len(word) > len(suffix) + 2:
            return 'verb'

    return None

def categorize_with_wordnet(words):
    """Use WordNet to categorize words that don't have clear suffixes"""
    try:
        from nltk.corpus import wordnet as wn
    except:
        print("  WordNet not available, skipping unknown words")
        return None

    categorized = {
        'noun': set(),
        'verb': set(),
        'adjective': set(),
        'adverb': set(),
        'still_unknown': set()
    }

    pos_map = {
        'n': 'noun',
        'v': 'verb',
        'a': 'adjective',
        's': 'adjective',  # adjective satellite
        'r': 'adverb'
    }

    print(f"  Using WordNet to categorize {len(words)} unknown words...")

    for word in words:
        synsets = wn.synsets(word)
        if not synsets:
            categorized['still_unknown'].add(word)
            continue

        # Get primary POS (most common usage)
        pos_counts = {}
        for syn in synsets:
            pos = syn.pos()
            pos_counts[pos] = pos_counts.get(pos, 0) + 1

        # Use the most common POS
        primary_pos = max(pos_counts.items(), key=lambda x: x[1])[0]
        category = pos_map.get(primary_pos, 'still_unknown')
        categorized[category].add(word)

    return categorized

def sieve_eff():
    """Sort EFF wordlist and create _large.txt files"""
    if not os.path.exists(EFF_LIST):
        print(f"Error: {EFF_LIST} not found.")
        return

    print("Analyzing EFF list using suffix patterns + WordNet...\n")

    # 1. Load the EFF list words
    eff_words = []
    with open(EFF_LIST, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if parts:
                word = parts[-1].lower()
                if word.isalpha():  # Only alphabetic words
                    eff_words.append(word)

    print(f"Loaded {len(eff_words)} words from EFF list\n")

    # 2. Categorize by suffix first
    categorized = {
        'adjective': set(),
        'adverb': set(),
        'noun': set(),
        'verb': set(),
    }
    unknown_words = []

    print("Step 1: Categorizing by suffix patterns...")
    for word in eff_words:
        pos = get_pos_by_suffix(word)
        if pos:
            categorized[pos].add(word)
        else:
            unknown_words.append(word)

    print(f"  Adjectives: {len(categorized['adjective'])}")
    print(f"  Adverbs: {len(categorized['adverb'])}")
    print(f"  Nouns: {len(categorized['noun'])}")
    print(f"  Verbs: {len(categorized['verb'])}")
    print(f"  Unknown: {len(unknown_words)}")

    # 3. Try WordNet for unknown words
    if unknown_words:
        print(f"\nStep 2: Categorizing unknown words with WordNet...")
        wordnet_results = categorize_with_wordnet(unknown_words)

        if wordnet_results:
            for pos in ['adjective', 'adverb', 'noun', 'verb']:
                categorized[pos].update(wordnet_results[pos])
                print(f"  Added {len(wordnet_results[pos])} {pos}s from WordNet")

            # Save truly unknown words
            if wordnet_results['still_unknown']:
                unknown_file = os.path.join(WORDS_DIR, 'unknown_words.txt')
                with open(unknown_file, 'w') as f:
                    f.write('\n'.join(sorted(wordnet_results['still_unknown'])))
                print(f"\n  {len(wordnet_results['still_unknown'])} words still unknown, saved to {unknown_file}")

    # 4. Mapping to files
    mapping = {
        'adjective': ('adjectives.txt', 'adjectives_large.txt'),
        'adverb': ('adverbs.txt', 'adverbs_large.txt'),
        'noun': ('medium_nouns.txt', 'nouns_large.txt'),
        'verb': ('verbs.txt', 'verbs_large.txt')
    }

    # 5. Merge and create _large files
    print("\nStep 3: Creating _large files...")
    for pos, (base_file, large_file) in mapping.items():
        base_path = os.path.join(WORDS_DIR, base_file)
        large_path = os.path.join(WORDS_DIR, large_file)

        # Load existing curated words
        existing = set()
        if os.path.exists(base_path):
            with open(base_path, 'r') as f:
                existing = {line.strip().lower() for line in f if line.strip()}

        # Combine curated words with EFF words
        combined = sorted(list(existing.union(categorized[pos])))

        # Write _large file
        with open(large_path, 'w') as f:
            f.write('\n'.join(combined))

        new_from_eff = len(categorized[pos] - existing)
        print(f"  {pos}s: {len(existing)} curated + {new_from_eff} new EFF = {len(combined)} total")

    print("\nDone! Created all _large files.")

if __name__ == "__main__":
    sieve_eff()
