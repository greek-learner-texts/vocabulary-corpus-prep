#!/usr/bin/env python3
"""
Tokenise ONE-format section texts into ONE-format token files.

Reads:  one/{work_id}/section.tsv
Writes: one/{work_id}/token.tsv          (token_id, text)
        one/{work_id}/token_section.tsv   (section_ref, token_id)

Tokenisation rules:
- Split on whitespace
- Separate leading punctuation: ( [ ' 〈
- Separate trailing punctuation: . , · ; ) ] 〉
- Split negation compounds: οὐδέ → οὐ + δέ, μηδέ → μη + δέ, etc.
- Split crasis: κἀγώ → κ + ἀγώ, τἀληθῆ → τ + ἀληθῆ, etc.
"""

import re
from pathlib import Path

REPO_DIR = Path(__file__).parent.parent
ONE_DIR = REPO_DIR / "one"

LEADING_PUNCT = set("(['〈\"")
TRAILING_PUNCT = set(".,·;)]〉\"")

# Negation/conjunction compounds to split at position 2
SPLIT_AT_2 = {
    "οὔτε", "οὐδ'", "οὐδὲ", "οὐδέ", "οὔθ'", "οὔτ'",
    "μηδέ", "μηδὲ", "μήτε", "μηδ'", "μήθ'", "μήτ'",
    "εἴτε",
}

# Crasis prefixes: single character that splits off
CRASIS_K = ("κἀ", "κἂ", "κᾆ", "κἄ")
CRASIS_T = ("τἀ", "τἆ", "ταὐ", "τοὐ", "τοὔ", "τἄ")


def tokenize_section(text: str):
    """
    Yield tokens from a section's text.
    Each token is a string (word or punctuation).
    """
    # Ensure punctuation is separated from words
    text = re.sub(r"(\w+)\.(\w+)", r"\1. \2", text)
    text = re.sub(r"(\w+),(\w+)", r"\1, \2", text)

    for raw in text.split():
        # Separate leading punctuation
        while raw and raw[0] in LEADING_PUNCT:
            yield raw[0]
            raw = raw[1:]

        if not raw:
            continue

        # Separate trailing punctuation
        tail = []
        while raw and raw[-1] in TRAILING_PUNCT:
            tail.insert(0, raw[-1])
            raw = raw[:-1]

        if raw:
            # Check for compound splits
            if raw in SPLIT_AT_2:
                yield raw[:2]
                yield raw[2:]
            elif any(raw.startswith(p) for p in CRASIS_K):
                yield "κ"
                yield raw[1:]
            elif any(raw.startswith(p) for p in CRASIS_T):
                yield "τ"
                yield raw[1:]
            else:
                yield raw

        for p in tail:
            yield p


def tokenize_work(work_id: str) -> tuple[int, int]:
    """
    Tokenise a work's sections into token.tsv and token_section.tsv.
    Returns (num_sections, num_tokens).
    """
    section_path = ONE_DIR / work_id / "section.tsv"
    token_path = ONE_DIR / work_id / "token.tsv"
    token_section_path = ONE_DIR / work_id / "token_section.tsv"

    token_idx = 0
    num_sections = 0

    with open(token_path, "w") as tok_f, open(token_section_path, "w") as map_f:
        tok_f.write("token_id\ttext\n")
        map_f.write("section_ref\ttoken_id\n")

        for line in open(section_path):
            if line.startswith("section_id\t"):
                continue
            line = line.rstrip("\n")
            if "\t" not in line:
                continue

            section_id, text = line.split("\t", 1)
            num_sections += 1

            for token_text in tokenize_section(text):
                token_idx += 1
                tok_f.write(f"{token_idx}\t{token_text}\n")
                map_f.write(f"{section_id}\t{token_idx}\n")

    return num_sections, token_idx


def main():
    works_path = ONE_DIR / "works.tsv"
    total_tokens = 0
    total_sections = 0

    for line in open(works_path):
        if line.startswith("work_id\t"):
            continue
        work_id = line.split("\t")[0]

        sections, tokens = tokenize_work(work_id)
        total_sections += sections
        total_tokens += tokens
        print(f"  {work_id}: {tokens:,} tokens ({sections} sections)")

    print(f"\n  Total: {total_tokens:,} tokens ({total_sections} sections)")


if __name__ == "__main__":
    main()
