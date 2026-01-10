#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verify that words in *_large.txt files match their intended part of speech using WordNet
"""

import os

try:
    from nltk.corpus import wordnet as wn
except ImportError:
    print("Error: NLTK required. Install with: pip install nltk")
    print("Then run: python -c 'import nltk; nltk.download(\"wordnet\")'")
    exit(1)

words_dir = "words"

# Map file names to expected POS
files = {
    'adjectives_large.txt': {'a', 's'},  # adjective and adjective satellite
    'adverbs_large.txt': {'r'},          # adverb
    'nouns_large.txt': {'n'},            # noun
    'verbs_large.txt': {'v'}             # verb
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
        print(f"⚠️  {filename} not found")
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
    multi_pos = []  # Words that can be multiple POS

    for word in words:
        pos_tags = get_word_pos_tags(word)

        if not pos_tags:
            not_in_wordnet.append(word)
        elif expected_pos.intersection(pos_tags):
            correct.append(word)
            # Check if it's also other POS
            if len(pos_tags) > 1:
                multi_pos.append((word, pos_tags))
        else:
            incorrect.append((word, pos_tags))

    # Print summary
    print(f"✓ Correct: {len(correct)} ({len(correct)/len(words)*100:.1f}%)")
    print(f"✗ Incorrect: {len(incorrect)} ({len(incorrect)/len(words)*100:.1f}%)")
    print(f"? Not in WordNet: {len(not_in_wordnet)} ({len(not_in_wordnet)/len(words)*100:.1f}%)")
    print(f"⚡ Multi-POS: {len(multi_pos)} ({len(multi_pos)/len(words)*100:.1f}%)")

    # Show details
    if incorrect:
        print(f"\n❌ INCORRECT WORDS (showing first 20):")
        for word, pos_tags in incorrect[:20]:
            pos_names = {
                'n': 'noun', 'v': 'verb',
                'a': 'adjective', 's': 'adjective',
                'r': 'adverb'
            }
            actual = ', '.join(pos_names.get(p, p) for p in pos_tags)
            print(f"  • {word:20s} → actually: {actual}")
        if len(incorrect) > 20:
            print(f"  ... and {len(incorrect) - 20} more")

    if not_in_wordnet:
        print(f"\n⚠️  NOT IN WORDNET (showing first 15):")
        for word in not_in_wordnet[:15]:
            print(f"  • {word}")
        if len(not_in_wordnet) > 15:
            print(f"  ... and {len(not_in_wordnet) - 15} more")

    return {
        'total': len(words),
        'correct': len(correct),
        'incorrect': len(incorrect),
        'not_in_wordnet': len(not_in_wordnet),
        'multi_pos': len(multi_pos)
    }

def main():
    print("\n🔍 PART OF SPEECH VERIFICATION")
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
    print(f"✓ Verified correct: {total_correct} ({total_correct/total_words*100:.1f}%)")
    print(f"✗ Incorrect POS: {total_incorrect} ({total_incorrect/total_words*100:.1f}%)")
    print(f"? Not in WordNet: {total_unknown} ({total_unknown/total_words*100:.1f}%)")

    print("\n💡 Note: Words not in WordNet may still be correct.")
    print("   Multi-POS words (like 'light' = noun/verb/adj) are marked correct.")

if __name__ == "__main__":
    main()
