#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remove incorrectly categorized words from *_large.txt files using WordNet verification
"""

import os

try:
    from nltk.corpus import wordnet as wn
except ImportError:
    print("Error: NLTK required. Install with: pip install nltk")
    exit(1)

WORDS_DIR = "words"

FILES = {
    'adjectives_large.txt': {'a', 's'},
    'adverbs_large.txt': {'r'},
    'nouns_large.txt': {'n'},
    'verbs_large.txt': {'v'}
}

def get_word_pos_tags(word):
    """Get all POS tags for a word from WordNet"""
    synsets = wn.synsets(word)
    if not synsets:
        return set()
    return {syn.pos() for syn in synsets}

def cleanup_file(filename, expected_pos):
    """Remove words that don't match expected POS"""
    filepath = os.path.join(WORDS_DIR, filename)

    if not os.path.exists(filepath):
        print(f"⚠️  {filename} not found")
        return

    print(f"\nProcessing: {filename}")

    with open(filepath, 'r') as f:
        words = [line.strip() for line in f if line.strip()]

    # Separate correct and incorrect words
    correct = []
    removed = []

    for word in words:
        pos_tags = get_word_pos_tags(word)

        # Keep words that:
        # 1. Match expected POS
        # 2. Not in WordNet (can't verify, keep them)
        if not pos_tags or expected_pos.intersection(pos_tags):
            correct.append(word)
        else:
            removed.append((word, pos_tags))

    # Write back only correct words
    with open(filepath, 'w') as f:
        f.write('\n'.join(correct))

    # Report
    print(f"  Kept: {len(correct)} words")
    print(f"  Removed: {len(removed)} words")

    if removed:
        print(f"  Removed words:")
        pos_names = {'n': 'noun', 'v': 'verb', 'a': 'adjective', 's': 'adjective', 'r': 'adverb'}
        for word, pos_tags in removed:
            actual = ', '.join(pos_names.get(p, p) for p in pos_tags)
            print(f"    • {word:20s} → {actual}")

    return len(removed)

def main():
    print("🧹 CLEANING UP INCORRECT WORDS")
    print("Removing words that don't match their file's POS category\n")

    total_removed = 0

    for filename, expected_pos in FILES.items():
        removed = cleanup_file(filename, expected_pos)
        if removed:
            total_removed += removed

    print(f"\n{'='*60}")
    print(f"TOTAL REMOVED: {total_removed} words")
    print(f"{'='*60}")
    print("\n✓ Cleanup complete! Run verify_pos.py to confirm.")

if __name__ == "__main__":
    main()
