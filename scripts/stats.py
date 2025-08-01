#!/usr/bin/env python3

from pathlib import Path

REPO_DIR = Path(__file__).parent.parent
TAGGED_TEXTS_DIR = REPO_DIR / "tagged-texts"


with open(REPO_DIR / "counts.tsv", "w") as counts_file:
    print(f"AUTHOR\tWORK\tTAGGED\tOGA\tGORMAN", file=counts_file)

    for author_dir in sorted(TAGGED_TEXTS_DIR.iterdir()):
        for work_dir in sorted(author_dir.iterdir()):
            tagged = 0
            oga = 0
            gorman = 0
            for version_path in work_dir.glob("*.tsv"):
                author, work, version = version_path.stem.split(".")
                tokens = version_path.read_text().splitlines()
                if version == "tagged":
                    tagged = len(tokens)
                elif version == "oga":
                    oga = len(tokens)
                elif version == "gorman":
                    gorman = len(tokens)
            print(f"{author_dir.name.split("_")[0]}\t{work_dir.name}\t{tagged}\t{oga}\t{gorman}", file=counts_file)

