"""
Expand data/base_200.csv into lipogram experiment patterns.

For each base sentence, apply multiple banned character sets
and create one record per (sentence, banned_set) that actually appears
in the surface text.

Uses the agreed banned sets:
- easy: "い", "さ", "ら"
- medium: "あ,い,う,え,お", "か,き,く,け,こ"

Limits to at most 3 banned sets per base sentence to avoid
over-representing a single sentence.

Output:
- data/dev_500.csv (id, text, banned_chars, constraint_type, genre, source_id)
"""

import csv
from pathlib import Path


BANNED_SETS = [
    ("easy", "い"),
    ("easy", "さ"),
    ("easy", "ら"),
    ("medium", "あ,い,う,え,お"),
    ("medium", "か,き,く,け,こ"),
]

MAX_SETS_PER_SENTENCE = 3


def main():
    data_dir = Path("data")
    src = data_dir / "base_200.csv"
    out = data_dir / "dev_500.csv"

    with src.open(encoding="utf-8") as fin:
        reader = csv.DictReader(fin)
        base_rows = list(reader)

    records = []
    new_id = 0
    for row in base_rows:
        text = row["text"].strip()
        genre = row.get("genre", "tatoeba")
        source_id = row.get("source_id", "")

        used_sets = 0
        for constraint_type, banned_str in BANNED_SETS:
            chars = [c.strip() for c in banned_str.split(",")]
            if any(c in text for c in chars):
                records.append(
                    {
                        "id": new_id,
                        "text": text,
                        "banned_chars": banned_str,
                        "constraint_type": constraint_type,
                        "genre": genre,
                        "source_id": source_id,
                    }
                )
                new_id += 1
                used_sets += 1
                if used_sets >= MAX_SETS_PER_SENTENCE:
                    break

    with out.open("w", newline="", encoding="utf-8") as fout:
        fieldnames = ["id", "text", "banned_chars", "constraint_type", "genre", "source_id"]
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"written {out} rows={len(records)} (base_sentences={len(base_rows)})")


if __name__ == "__main__":
    main()

