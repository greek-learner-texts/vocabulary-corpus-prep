#!/usr/bin/env python3
"""
Run greek-check levels 1–3 (encoding, graphotactics, accentuation) on all
base texts in the corpus.

Produces per-file HTML reports in reports/ and a summary to stdout.
"""

import subprocess
import sys
from pathlib import Path

REPO_DIR = Path(__file__).parent.parent
BASE_TEXTS_DIR = REPO_DIR / "base-texts"
REPORTS_DIR = REPO_DIR / "reports"

GREEK_CHECK_DIR = (REPO_DIR / "../../AI/greek-check").resolve()
CONFIG = GREEK_CHECK_DIR / "configs" / "attic_prose.toml"

LEVELS = "encoding,graphotactics,accentuation"

# All base text files in the corpus
BASE_TEXT_FILES = sorted(BASE_TEXTS_DIR.rglob("*.base.tsv"))


def run_check(base_text_path: Path) -> tuple[str, int]:
    """Run greek-check on a single base text file. Returns (name, returncode)."""
    name = base_text_path.stem.replace(".base", "")
    report_path = REPORTS_DIR / f"{name}.html"

    result = subprocess.run(
        [
            "uv", "run", "python", "run_all_checks.py",
            str(base_text_path.resolve()),
            str(CONFIG),
            "--levels", LEVELS,
            "--html", str(report_path.resolve()),
            "--hide-clean",
        ],
        cwd=str(GREEK_CHECK_DIR),
        capture_output=True,
        text=True,
    )

    return name, result.returncode, result.stderr


def main():
    if not GREEK_CHECK_DIR.exists():
        print(f"Error: greek-check not found at {GREEK_CHECK_DIR}", file=sys.stderr)
        sys.exit(1)

    if not CONFIG.exists():
        print(f"Error: config not found at {CONFIG}", file=sys.stderr)
        sys.exit(1)

    REPORTS_DIR.mkdir(exist_ok=True)

    print(f"Running greek-check levels [{LEVELS}] on {len(BASE_TEXT_FILES)} files...")
    print(f"Reports will be written to {REPORTS_DIR}/")
    print()

    for path in BASE_TEXT_FILES:
        name, returncode, stderr = run_check(path)

        # Extract summary line from stderr
        lines = stderr.strip().split("\n")
        summary_lines = []
        capture = False
        for line in lines:
            if "No errors found" in line or "Found " in line:
                capture = True
            if capture:
                summary_lines.append(line)

        summary = "\n".join(summary_lines) if summary_lines else "(no summary)"
        status = "OK" if returncode == 0 else f"EXIT {returncode}"

        print(f"{name}: {summary.strip()}")

    print()
    print(f"HTML reports written to {REPORTS_DIR}/")


if __name__ == "__main__":
    main()
