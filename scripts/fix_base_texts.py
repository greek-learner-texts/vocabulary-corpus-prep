#!/usr/bin/env python3
"""
Post-extraction base text cleanup.

Applies documented fixes to extracted base texts. This handles:
1. Unfixable XML structure issues (smooshed words from Perseus source)
2. Residual markup patterns that extraction missed
3. Known source errors in Perseus texts

Each fix is logged with before/after context.
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Fix:
    """A single base text fix."""
    pattern: str
    replacement: str
    description: str
    count: int = 0


# Documented fixes - these are genuine Perseus source issues
# or residual patterns that the XML extraction couldn't handle
FIXES = [
    # Smooshed words from Perseus source (missing spaces in original XML)
    Fix(
        pattern=r"τοῦΦιλίππου",
        replacement="τοῦ Φιλίππου",
        description="Missing space: 'of Philip' (Demosthenes 18.76)"
    ),
    Fix(
        pattern=r"τοῦΛεύκωνος",
        replacement="τοῦ Λεύκωνος",
        description="Missing space: 'of Leucon' (Demosthenes 20.35)"
    ),
    Fix(
        pattern=r"αὐτῷπατρίδα",
        replacement="αὐτῷ πατρίδα",
        description="Missing space: 'to him a country' (Lysias 12.69)"
    ),
    Fix(
        pattern=r"αὐτῷἐδόκει",
        replacement="αὐτῷ ἐδόκει",
        description="Missing space: 'it seemed to him' (Lysias 13.41)"
    ),
    Fix(
        pattern=r"αὐτῶνἀνάγκης",
        replacement="αὐτῶν ἀνάγκης",
        description="Missing space: 'of them of necessity' (Lysias 13.31)"
    ),

    # Accent errors in Perseus source
    Fix(
        pattern=r"μέ φατε",
        replacement="μέ φατέ",
        description="Missing accent on φημί 2pl enclitic φατέ (Xenophon Oec. 4.10)"
    ),

    # ᾄδω breathing errors in plato-texts (rough→smooth on all forms)
    Fix(
        pattern=r"ᾁσαιμεν",
        replacement="ᾄσαιμεν",
        description="Wrong breathing on ᾄδω optative (Xenophon Oec. 7.1)"
    ),
    Fix(
        pattern=r"ᾁσαντας",
        replacement="ᾄσαντας",
        description="Wrong breathing on ᾄδω aorist participle (Plato Symp. 176a)"
    ),
    Fix(
        pattern=r"ᾁδειν",
        replacement="ᾄδειν",
        description="Wrong breathing on ᾄδω infinitive (Plato Symp. 181a)"
    ),
    Fix(
        pattern=r"ᾁδομεν",
        replacement="ᾄδομεν",
        description="Wrong breathing on ᾄδω 1pl (Plato Symp. 214b)"
    ),

    # plato-texts editorial markers
    Fix(
        pattern=r"\+",
        replacement="",
        description="Strip + editorial variant markers from plato-texts source"
    ),
    Fix(
        pattern=r"\{p\} ?",
        replacement="",
        description="Strip {p} paragraph markers from plato-texts source"
    ),
    Fix(
        pattern=r"\{/?quote\} ?",
        replacement="",
        description="Strip {quote}/{/quote} verse markers from plato-texts source"
    ),

    # Grave-on-wrong-syllable errors in Perseus (encoding corruption)
    Fix(
        pattern=r"βαρβὰρους",
        replacement="βαρβάρους",
        description="Grave on wrong syllable: βαρβάρους (Isocrates Evag. 67)"
    ),
    Fix(
        pattern=r"ἳνα",
        replacement="ἵνα",
        description="Grave on wrong syllable: ἵνα (Isocrates Busiris 159)"
    ),
    Fix(
        pattern=r"τοὺτους",
        replacement="τούτους",
        description="Grave on wrong syllable: τούτους (Isocrates Areopag. 49)"
    ),
    Fix(
        pattern=r"οὐδὲνα",
        replacement="οὐδένα",
        description="Grave on wrong syllable: οὐδένα (Isocrates Areopag. 262)"
    ),
    Fix(
        pattern=r"παιδεὶας",
        replacement="παιδείας",
        description="Grave on wrong syllable: παιδείας (Isocrates Antidosis 19)"
    ),
    Fix(
        pattern=r"ἀντιλὲγειν",
        replacement="ἀντιλέγειν",
        description="Grave on wrong syllable: ἀντιλέγειν (Isocrates Antidosis 108)"
    ),
    Fix(
        pattern=r"δὶα",
        replacement="διὰ",
        description="Grave on wrong syllable: διά (Lysias 4.5)"
    ),

    # Smooshed words in plato-texts
    Fix(
        pattern=r"δἄν",
        replacement="δ\u2019 ἄν",
        description="Missing elision/space: δ' ἄν (Plato Symp. 199b)"
    ),

    # Wrong-accent source errors in Perseus
    Fix(
        pattern=r"Λακεδαιμονίῶν",
        replacement="Λακεδαιμονίων",
        description="Spurious circumflex: Λακεδαιμονίων (Isocrates Antid. 68)"
    ),
    Fix(
        pattern=r"πάντῶν",
        replacement="πάντων",
        description="Spurious circumflex: πάντων (Lysias 18.17)"
    ),
    Fix(
        pattern=r"τούτῷ",
        replacement="τούτῳ",
        description="Spurious circumflex: τούτῳ (Lysias 4.20)"
    ),
]


_APOSTROPHE_MAP = str.maketrans({
    "\u02BC": "\u2019",  # MODIFIER LETTER APOSTROPHE
    "\u02BD": "\u2019",  # MODIFIER LETTER REVERSED COMMA
    "\u1FBD": "\u2019",  # GREEK KORONIS
    "\u2018": "\u2019",  # LEFT SINGLE QUOTATION MARK
    "\u0027": "\u2019",  # ASCII APOSTROPHE
})


def fix_base_text(text: str) -> tuple[str, list[str]]:
    """
    Apply all fixes to a base text.
    Returns: (fixed_text, list of fix descriptions applied)
    """
    changes = []

    # Normalize apostrophes to U+2019
    fixed = text.translate(_APOSTROPHE_MAP)
    if fixed != text:
        n = sum(1 for a, b in zip(text, fixed) if a != b)
        changes.append(f"{n}× apostrophe normalized to U+2019")

    for fix in FIXES:
        if re.search(fix.pattern, fixed):
            # Count occurrences
            matches = re.findall(fix.pattern, fixed)
            fix.count += len(matches)

            # Apply fix
            fixed = re.sub(fix.pattern, fix.replacement, fixed)

            # Log change
            changes.append(f"{len(matches)}× {fix.description}")

    return fixed, changes


def main():
    base_texts_dir = Path("/Users/jtauber/Development/Greek/vocabulary-corpus-prep/base-texts")
    logs_dir = Path("/Users/jtauber/Development/Greek/vocabulary-corpus-prep/fix-logs")
    logs_dir.mkdir(exist_ok=True)

    total_fixes = 0
    log_entries = []

    for tsv_path in sorted(base_texts_dir.rglob("*.base.tsv")):
        rel_path = tsv_path.relative_to(base_texts_dir)
        lines = tsv_path.read_text().splitlines()
        fixed_lines = []
        file_changes = []

        for line in lines:
            if "\t" not in line:
                fixed_lines.append(line)
                continue

            ref, text = line.split("\t", 1)
            fixed_text, changes = fix_base_text(text)

            if changes:
                fixed_lines.append(f"{ref}\t{fixed_text}")
                file_changes.extend(changes)

                # Log the change with context
                for c in changes:
                    log_entries.append(f"{rel_path} {ref}: {c}")
            else:
                fixed_lines.append(line)

        # Only rewrite if changes were made
        if file_changes:
            tsv_path.write_text("\n".join(fixed_lines) + "\n")
            total_fixes += len(file_changes)
            print(f"{rel_path}: {len(file_changes)} fix(es)")

    # Write fix log
    if log_entries:
        log_path = logs_dir / "fixes.log"
        with log_path.open("a") as f:
            from datetime import datetime
            f.write(f"\n=== {datetime.now().isoformat()} ===\n")
            for entry in log_entries:
                f.write(f"{entry}\n")

    print(f"\nTotal fixes applied: {total_fixes}")

    # Summary of fix patterns
    print("\nFix pattern usage:")
    for fix in FIXES:
        if fix.count > 0:
            print(f"  {fix.count:3d}× {fix.description}")


if __name__ == "__main__":
    main()
