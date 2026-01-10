#!/usr/bin/env python3
"""
Calculate entropy for passphrase patterns based on current word lists
"""

import os
import math

WORDS_DIR = "words"

def load_word_count(filename):
    """Load and count words from a file"""
    filepath = os.path.join(WORDS_DIR, filename)
    if not os.path.exists(filepath):
        print(f"Warning: {filename} not found")
        return 0
    with open(filepath, 'r') as f:
        return len([line for line in f if line.strip()])

def main():
    # Load word counts
    adj_curated = load_word_count("adjectives.txt")
    adv_curated = load_word_count("adverbs.txt")
    noun_curated = load_word_count("medium_nouns.txt")
    verb_curated = load_word_count("verbs.txt")

    adj_large = load_word_count("adjectives_large.txt")
    adv_large = load_word_count("adverbs_large.txt")
    noun_large = load_word_count("nouns_large.txt")
    verb_large = load_word_count("verbs_large.txt")

    prep_count = load_word_count("prepositions.txt")

    print("\nPASSPHRASE ENTROPY CALCULATOR")
    print("=" * 60)
    print("\nWORD LIST SIZES:")
    print(f"  Adjectives:  {adj_curated:4d} curated + {adj_large:4d} large")
    print(f"  Adverbs:     {adv_curated:4d} curated + {adv_large:4d} large")
    print(f"  Nouns:       {noun_curated:4d} curated + {noun_large:4d} large")
    print(f"  Verbs:       {verb_curated:4d} curated + {verb_large:4d} large")
    print(f"  Prepositions: {prep_count:4d}")

    # Calculate pools for different orig_chance values
    print("\n" + "=" * 60)
    print("ENTROPY BY CURATED/LARGE MIX:")
    print("=" * 60)

    for orig_chance in [0, 30, 50, 70, 100]:
        adj_pool = (adj_curated * (orig_chance/100)) + (adj_large * ((100-orig_chance)/100))
        adv_pool = (adv_curated * (orig_chance/100)) + (adv_large * ((100-orig_chance)/100))
        noun_pool = (noun_curated * (orig_chance/100)) + (noun_large * ((100-orig_chance)/100))
        verb_pool = (verb_curated * (orig_chance/100)) + (verb_large * ((100-orig_chance)/100))

        print(f"\n{orig_chance}% Curated / {100-orig_chance}% Large:")
        print(f"  Pool sizes: {adj_pool:.0f} adj, {adv_pool:.0f} adv, {verb_pool:.0f} verb, {noun_pool:.0f} noun")

        # Common patterns
        patterns = {
            "adj-noun": [adj_pool, noun_pool],
            "adj-noun-verb-noun": [adj_pool, noun_pool, verb_pool, noun_pool],
            "adj-adv-verb-noun": [adj_pool, adv_pool, verb_pool, noun_pool],
            "noun-verb-prep-noun": [noun_pool, verb_pool, prep_count, noun_pool],
            "adj-noun-verb-adv-noun": [adj_pool, noun_pool, verb_pool, adv_pool, noun_pool],
        }

        for pattern_name, pools in patterns.items():
            entropy = sum(math.log2(p) for p in pools if p > 0)
            combinations = int(2 ** entropy)
            print(f"    {pattern_name:25s}: {entropy:5.1f} bits ({combinations:,} combinations)")

    # Strength guide
    print("\n" + "=" * 60)
    print("ENTROPY STRENGTH GUIDE:")
    print("=" * 60)
    print("  < 35 bits: Moderate (billions of combinations)")
    print("  35-50 bits: Strong (trillions to quadrillions)")
    print("  50-65 bits: Very Strong (quintillions)")
    print("  65-75 bits: Extremely Strong")
    print("  > 75 bits: Virtually Uncrackable")
    print("\nNote: These assume cryptographically secure random selection.")
    print("Adding numbers, symbols, or mixed case increases entropy further.")

if __name__ == "__main__":
    main()
