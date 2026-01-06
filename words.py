from nltk.corpus import wordnet as wn
from pathlib import Path

OUT_DIR = Path("words")
OUT_DIR.mkdir(exist_ok=True)

POS_MAP = {
    'nouns': wn.NOUN,
    'verbs': wn.VERB,
    'adjectives': wn.ADJ,
    'adverbs': wn.ADV
}

for label, pos in POS_MAP.items():
    words = set()
    for syn in wn.all_synsets(pos):
        for lemma in syn.lemmas():
            w = lemma.name().replace("_", " ").lower()
            if w.isalpha() and 2 <= len(w) <= 12:
                words.add(w)
    with open(OUT_DIR / f"{label}.txt", "w", encoding="utf-8") as f:
        for w in sorted(words):
            f.write(w + "\n")
    print(f"{label}: {len(words)} words exported")
