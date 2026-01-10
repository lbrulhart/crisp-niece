#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify that words in curated (non-large) files match their intended part of speech using WordNet
"""

import os

try:
    from nltk.corpus import wordnet as wn
except ImportError:
    print("Error: NLTK required. Install with: pip install nltk")
    exit(1)

words_dir = "words"

# Map file names to expected POS
files = {
    'adjectives.txt': {'a', 's'},
    'adverbs.txt': {'r'},
    'medium_nouns.txt': {'n'},
    'verbs.txt': {'v'}
}

def get_word_pos_tags(word):
    """Get all POS tags for a word from WordNet"""
    synsets = wn.synsets(word)
    if not synsets:
        return set()
    return {syn.pos() for syn in synsets}

def verify_file(filename, expected_pos):
    """Verify words in file match expected POS"""
    filepath = os.path.join(words_dir, filename)

    if not os.path.exists(filepath):
        print(f"WARNING: {filename} not found")
        return

    print(f"\n{'='*60}")
    print(f"Verifying: {filename}")
    print(f"Expected POS: {expected_pos}")
    print(f"{'='*60}")

    with open(filepath, 'r') as f:
        words = [line.strip() for line in f if line.strip()]

    print(f"Total words: {len(words)}\n")

    # Track results
    correct = []
    incorrect = []
    not_in_wordnet = []
    multi_pos = []

    for word in words:
        pos_tags = get_word_pos_tags(word)

        if not pos_tags:
            not_in_wordnet.append(word)
        elif expected_pos.intersection(pos_tags):
            correct.append(word)
            if len(pos_tags) > 1:
                multi_pos.append((word, pos_tags))
        else:
            incorrect.append((word, pos_tags))

    # Print summary
    print(f"CORRECT: {len(correct)} ({len(correct)/len(words)*100:.1f}%)")
    print(f"INCORRECT: {len(incorrect)} ({len(incorrect)/len(words)*100:.1f}%)")
    print(f"NOT IN WORDNET: {len(not_in_wordnet)} ({len(not_in_wordnet)/len(words)*100:.1f}%)")
    print(f"MULTI-POS: {len(multi_pos)} ({len(multi_pos)/len(words)*100:.1f}%)")

    # Show details
    if incorrect:
        print(f"\nINCORRECT WORDS:")
        for word, pos_tags in incorrect:
            pos_names = {
                'n': 'noun', 'v': 'verb',
                'a': 'adjective', 's': 'adjective',
                'r': 'adverb'
            }
            actual = ', '.join(pos_names.get(p, p) for p in pos_tags)
            print(f"  {word:20s} -> {actual}")

    if not_in_wordnet:
        print(f"\nNOT IN WORDNET:")
        for word in not_in_wordnet:
            print(f"  {word}")

    return {
        'total': len(words),
        'correct': len(correct),
        'incorrect': len(incorrect),
        'not_in_wordnet': len(not_in_wordnet),
        'multi_pos': len(multi_pos)
    }

def main():
    print("\nVERIFYING CURATED (NON-LARGE) FILES")
    print("Using NLTK WordNet for validation\n")

    results = {}
    for filename, expected_pos in files.items():
        results[filename] = verify_file(filename, expected_pos)

    # Overall summary
    print(f"\n{'='*60}")
    print("OVERALL SUMMARY")
    print(f"{'='*60}")

    total_words = sum(r['total'] for r in results.values())
    total_correct = sum(r['correct'] for r in results.values())
    total_incorrect = sum(r['incorrect'] for r in results.values())
    total_unknown = sum(r['not_in_wordnet'] for r in results.values())

    print(f"Total words checked: {total_words}")
    print(f"VERIFIED CORRECT: {total_correct} ({total_correct/total_words*100:.1f}%)")
    print(f"INCORRECT POS: {total_incorrect} ({total_incorrect/total_words*100:.1f}%)")
    print(f"NOT IN WORDNET: {total_unknown} ({total_unknown/total_words*100:.1f}%)")

if __name__ == "__main__":
    main()
