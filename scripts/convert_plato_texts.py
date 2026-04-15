#!/usr/bin/env python3
"""
Convert plato-texts GLTP format to base-text TSV format.

Reads: plato-texts/text/euthyphro.txt (GLTP: NNN.SS TEXT with {Xa} markers)
Writes: base-texts/tlg0059/tlg0059.tlg001.plato-texts.base.tsv

The Stephanus section (e.g. 2a, 2b) is used as the ref.
Speaker labels (.00 lines) and editorial markup ({del}, {q}, etc.) are stripped.
"""

import re
from pathlib import Path

REPO_DIR = Path(__file__).parent.parent
PLATO_TEXTS_DIR = (REPO_DIR / "../../Greek/plato-texts/text").resolve()


def convert(input_path: Path, output_path: Path) -> None:
    """Convert a plato-texts file to base-text TSV."""
    current_section = None
    current_text: list[str] = []

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as out:
        for line in open(input_path):
            line = line.rstrip("\n")
            if not line:
                continue

            # Parse GLTP format: NNN.SS TEXT
            ref_part, text = line.split(" ", 1)

            # Skip .00 lines (speaker labels) but extract Stephanus refs
            if ref_part.endswith(".00"):
                # Extract Stephanus section if present: {2a}, {5b}, etc.
                m = re.search(r"\{(\d+[a-e])\}", text)
                if m:
                    new_section = m.group(1)
                    if current_section and current_text:
                        print(current_section, " ".join(current_text), sep="\t", file=out)
                        current_text = []
                    current_section = new_section
                continue

            # Check for inline Stephanus refs: {2c}, {3a}, etc.
            # These can appear mid-sentence and mark section transitions
            parts = re.split(r"\{(\d+[a-e])\}", text)
            for i, part in enumerate(parts):
                if i % 2 == 1:
                    # This is a Stephanus ref — flush and start new section
                    if current_section and current_text:
                        print(current_section, " ".join(current_text), sep="\t", file=out)
                        current_text = []
                    current_section = part
                else:
                    # This is text — clean and accumulate
                    cleaned = clean_text(part)
                    if cleaned:
                        if current_section is None:
                            current_section = "1"  # fallback
                        current_text.append(cleaned)

        # Flush final section
        if current_section and current_text:
            print(current_section, " ".join(current_text), sep="\t", file=out)


def clean_text(text: str) -> str:
    """Strip editorial markup from text and normalize apostrophes."""
    # Remove {del}...{/del}, {q}, {/q} and other editorial tags
    text = re.sub(r"\{/?(?:del|q|add)\}", "", text)
    # Normalize elision apostrophe variants to U+2019 (RIGHT SINGLE QUOTATION MARK)
    for apos in ("\u02BC", "\u02BD", "\u1FBD", "\u0027"):
        text = text.replace(apos, "\u2019")
    # Strip opening quotation marks (not elision)
    text = text.replace("\u2018", "")
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


PLATO_WORKS = {
    "euthyphro": "tlg001",
    "apology": "tlg002",
    "crito": "tlg003",
    "symposium": "tlg011",
    "republic": "tlg030",
}


if __name__ == "__main__":
    for name, work_id in PLATO_WORKS.items():
        input_path = PLATO_TEXTS_DIR / f"{name}.txt"
        output_path = REPO_DIR / "base-texts" / "tlg0059" / f"tlg0059.{work_id}.plato-texts.base.tsv"
        convert(input_path, output_path)
        print(f"Converted {name}.txt → tlg0059.{work_id}.plato-texts.base.tsv")
