#!/usr/bin/env python3
"""
Build ONE-format base texts from extracted base texts.

Reads: base-texts/*/*.base.tsv (with XML tags)
Writes: one/{work_id}/section.tsv (clean text, ONE format)
Also: one/verse_dialect.tsv (stand-off annotations)
Also: one/manifest.toml (corpus metadata)

This is the canonical output for downstream corpus work.
"""

import re
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib

REPO_DIR = Path(__file__).parent.parent
BASE_TEXTS_DIR = REPO_DIR / "base-texts"
ANNOTATIONS_FILE = REPO_DIR / "annotations" / "verse_dialect.toml"
ONE_DIR = REPO_DIR / "one"


def strip_xml(text: str) -> str:
    """Remove all XML tags from text, preserving content."""
    return re.sub(r"<[^>]+>", "", text).strip()


def clean_section(text: str) -> str:
    """Clean a section's text for ONE format output."""
    # Strip XML tags
    text = strip_xml(text)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def build_section_file(base_tsv: Path, out_dir: Path) -> int:
    """
    Convert a base text TSV to ONE-format section.tsv.
    Returns number of sections written.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "section.tsv"

    count = 0
    with open(out_path, "w") as out:
        out.write("section_id\ttext\n")
        for line in open(base_tsv):
            line = line.rstrip("\n")
            if "\t" not in line:
                continue
            ref, text = line.split("\t", 1)
            cleaned = clean_section(text)
            if cleaned:
                out.write(f"{ref}\t{cleaned}\n")
                count += 1

    return count


def build_verse_dialect_tsv(annotations_path: Path, out_dir: Path) -> int:
    """
    Convert verse_dialect.toml to ONE-format stand-off TSV.
    Returns number of annotations written.
    """
    if not annotations_path.exists():
        return 0

    with open(annotations_path, "rb") as f:
        data = tomllib.load(f)

    out_path = out_dir / "verse_dialect.tsv"
    count = 0

    with open(out_path, "w") as out:
        out.write("work_id\tsection_ref\tcategory\n")
        for text_id, sections in sorted(data.items()):
            for category in ("verse", "dialect", "oracle", "inscription"):
                for ref in sections.get(category, []):
                    out.write(f"{text_id}\t{ref}\t{category}\n")
                    count += 1

    return count


def main():
    ONE_DIR.mkdir(parents=True, exist_ok=True)

    work_stats = {}
    total_sections = 0

    for base_tsv in sorted(BASE_TEXTS_DIR.rglob("*.base.tsv")):
        work_id = base_tsv.stem.replace(".base", "")
        out_dir = ONE_DIR / work_id.rsplit(".", 1)[0]  # e.g. tlg0003.tlg001

        # Derive work_id without source suffix for directory
        # tlg0003.tlg001.perseus-grc2 → tlg0003.tlg001
        parts = work_id.split(".")
        if len(parts) >= 3:
            dir_id = f"{parts[0]}.{parts[1]}"
        else:
            dir_id = work_id

        out_dir = ONE_DIR / dir_id
        count = build_section_file(base_tsv, out_dir)
        work_stats[dir_id] = count
        total_sections += count
        print(f"  {dir_id}: {count} sections")

    # Build stand-off annotations
    ann_count = build_verse_dialect_tsv(ANNOTATIONS_FILE, ONE_DIR)
    print(f"\n  verse_dialect.tsv: {ann_count} annotations")

    print(f"\n  {len(work_stats)} works, {total_sections} sections total")


if __name__ == "__main__":
    main()
