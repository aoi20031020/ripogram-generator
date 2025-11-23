"""
Generate a base set of ~200 Japanese sentences from data/jpn_sentences.csv.

Filters:
- length between 20 and 60 characters
- contains at least one Japanese character (hiragana or kanji)

Output:
- data/base_200.csv with columns:
  base_id, text, genre, source_id
"""

import csv
import random
import re
from pathlib import Path


def has_japanese(text: str) -> bool:
    return bool(re.search(r"[ぁ-ん一-龥]", text))


def main():
    data_dir = Path("data")
    src = data_dir / "jpn_sentences.csv"
    out = data_dir / "base_200.csv"

    random.seed(42)

    with src.open(encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        candidates = []
        for row in reader:
            text = row["text"].strip()
            if not (20 <= len(text) <= 60):
                continue
            if not has_japanese(text):
                continue
            candidates.append((row["id"], text))

    # sample up to 200 sentences
    if len(candidates) > 200:
        candidates = random.sample(candidates, 200)

    with out.open("w", newline="", encoding="utf-8") as fout:
        writer = csv.writer(fout)
        writer.writerow(["base_id", "text", "genre", "source_id"])
        for i, (orig_id, text) in enumerate(candidates):
            writer.writerow([i, text, "tatoeba", f"tatoeba:{orig_id}"])

    print(f"written {out} rows={len(candidates)}")


if __name__ == "__main__":
    main()

