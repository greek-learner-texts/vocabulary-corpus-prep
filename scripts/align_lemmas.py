#!/usr/bin/env python3
"""
Align OGA and Glaux tagging against ONE-format tokens to produce lemmatisation.

Reads:
  one/{work_id}/token.tsv (our canonical tokens)
  OGA CoNLL-U files
  Glaux treebank XML files

Writes:
  one/{work_id}/lemma.tsv (token_ref, lemma, postag, sources, notes)
"""

import unicodedata
from pathlib import Path

from lxml import etree

REPO_DIR = Path(__file__).parent.parent
ONE_DIR = REPO_DIR / "one"
OGA_DIR = (
    REPO_DIR
    / "../../Scaife/giuseppe"
    / "downloads/opera_graeca_adnotata_v0.2.0/workspace/conllu"
).resolve()
GLAUX_DIR = (REPO_DIR / "../glaux/xml").resolve()


def norm(s: str) -> str:
    """Normalise a form for comparison."""
    s = unicodedata.normalize("NFC", s)
    for apos in ("\u02BC", "\u02BD", "\u1FBD", "\u0027"):
        s = s.replace(apos, "\u2019")
    s = s.replace(":", "\u00b7")
    return s


def fold(s: str) -> str:
    """Fold a form for fuzzy comparison (strip accents, lowercase)."""
    if s and s[-1].isdigit():
        s = s[:-1]
    return unicodedata.normalize(
        "NFC",
        "".join(
            ch
            for ch in unicodedata.normalize("NFD", s.lower())
            if unicodedata.category(ch)[0] != "M"
        ),
    )


PUNCT = set(".,;·()[]〈〉—\"'\u2019")


def is_punct(s: str) -> bool:
    return len(s) == 1 and s in PUNCT


def read_our_tokens(work_id: str) -> list[tuple[int, str]]:
    """Read our token.tsv."""
    tokens = []
    for line in open(ONE_DIR / work_id / "token.tsv"):
        if line.startswith("token_id\t"):
            continue
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 2:
            tokens.append((int(parts[0]), parts[1]))
    return tokens


def read_oga(group_id: str, work_id_short: str) -> list[dict]:
    """Read OGA CoNLL-U file."""
    for suffix in ("grc2", "grc1"):
        pattern = f"tlg{group_id}.tlg{work_id_short}.perseus-{suffix}.tok01_sentence-seg01_annotated_lemma.conllu"
        path = OGA_DIR / pattern
        if path.exists():
            break
    else:
        return []

    tokens = []
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 10:
            continue
        if "-" in parts[0]:
            continue
        tokens.append({
            "form": parts[1],
            "lemma": parts[2],
            "postag": parts[4],
        })
    return tokens


def read_glaux(group_id: str, work_id_short: str) -> list[dict]:
    """Read Glaux treebank XML. Returns flat list."""
    return _read_glaux_flat(group_id, work_id_short)


def read_glaux_by_section(group_id: str, work_id_short: str) -> dict[str, list[dict]]:
    """Read Glaux treebank XML grouped by section ref."""
    path = GLAUX_DIR / f"{group_id}-{work_id_short}.xml"
    if not path.exists():
        return {}

    sections: dict[str, list[dict]] = {}
    root = etree.parse(str(path)).getroot()
    for word in root.iter("word"):
        form = word.get("form")
        if not form:
            continue
        if form in ("E", '"'):
            continue
        form_orig = word.get("form_original", "")
        if form_orig.startswith("[") or form_orig.endswith("]"):
            continue

        ref = word.get("div_section") or word.get("div_stephanus_section") or ""
        sections.setdefault(ref, []).append({
            "form": form,
            "lemma": word.get("lemma"),
            "postag": word.get("postag"),
        })
    return sections


def _read_glaux_flat(group_id: str, work_id_short: str) -> list[dict]:
    """Read Glaux as flat token list."""
    path = GLAUX_DIR / f"{group_id}-{work_id_short}.xml"
    if not path.exists():
        return []

    tokens = []
    root = etree.parse(str(path)).getroot()
    for word in root.iter("word"):
        form = word.get("form")
        if not form:
            continue
        if form in ("E", '"'):
            continue
        form_orig = word.get("form_original", "")
        if form_orig.startswith("[") or form_orig.endswith("]"):
            continue
        tokens.append({
            "form": form,
            "lemma": word.get("lemma"),
            "postag": word.get("postag"),
        })
    return tokens


def align_tokens(
    our_tokens: list[tuple[int, str]],
    source_tokens: list[dict],
) -> dict[int, dict]:
    """
    Align source tokens against our tokens.
    Returns: {our_token_id: {lemma, postag}}
    """
    result = {}
    si = 0

    for token_id, our_form in our_tokens:
        if si >= len(source_tokens):
            break

        our_n = norm(our_form)
        src = source_tokens[si]
        src_n = norm(src["form"])

        # Direct match
        if our_n == src_n or fold(our_n) == fold(src_n):
            result[token_id] = {"lemma": src["lemma"], "postag": src["postag"]}
            si += 1
            continue

        # Our token is punctuation, source doesn't have it — skip ours
        if is_punct(our_form):
            continue

        # Source token is punctuation, we don't have it — skip source
        while si < len(source_tokens) and is_punct(source_tokens[si]["form"]):
            si += 1
        if si < len(source_tokens):
            src = source_tokens[si]
            src_n = norm(src["form"])
            if our_n == src_n or fold(our_n) == fold(src_n):
                result[token_id] = {"lemma": src["lemma"], "postag": src["postag"]}
                si += 1
                continue

        # Source has hyphenated crasis parts (-τε, κα-, etc.)
        if si < len(source_tokens) and (
            source_tokens[si]["form"].startswith("-")
            or source_tokens[si]["form"].endswith("-")
        ):
            si += 1
            if si < len(source_tokens):
                src = source_tokens[si]
                src_n = norm(src["form"])
                if our_n == src_n or fold(our_n) == fold(src_n):
                    result[token_id] = {"lemma": src["lemma"], "postag": src["postag"]}
                    si += 1
                    continue

        # Look ahead in source (max 3)
        found = False
        for la in range(1, 4):
            if si + la < len(source_tokens):
                ahead = source_tokens[si + la]
                ahead_n = norm(ahead["form"])
                if our_n == ahead_n or fold(our_n) == fold(ahead_n):
                    si = si + la
                    result[token_id] = {"lemma": ahead["lemma"], "postag": ahead["postag"]}
                    si += 1
                    found = True
                    break
        if found:
            continue

        # No match — advance source
        si += 1

    return result


def work_id_parts(work_id: str) -> tuple[str, str]:
    """Split 'tlg0003.tlg001' into ('0003', '001')."""
    parts = work_id.split(".")
    return parts[0].replace("tlg", ""), parts[1].replace("tlg", "")


def read_our_tokens_by_section(work_id: str) -> dict[str, list[tuple[int, str]]]:
    """Read our tokens grouped by section."""
    sections: dict[str, list[tuple[int, str]]] = {}
    section_path = ONE_DIR / work_id / "token_section.tsv"
    token_path = ONE_DIR / work_id / "token.tsv"

    # Build token_id → text map
    token_text = {}
    for line in open(token_path):
        if line.startswith("token_id\t"):
            continue
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 2:
            token_text[int(parts[0])] = parts[1]

    # Group by section
    for line in open(section_path):
        if line.startswith("section_ref\t"):
            continue
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 2:
            section_ref = parts[0]
            token_id = int(parts[1])
            text = token_text.get(token_id, "")
            sections.setdefault(section_ref, []).append((token_id, text))

    return sections


def align_work(work_id: str) -> dict:
    """Align sources and produce lemma.tsv."""
    group_id, work_short = work_id_parts(work_id)

    our_tokens = read_our_tokens(work_id)

    # OGA: global alignment (same base text as ours)
    oga_tokens = read_oga(group_id, work_short)
    oga_aligned = align_tokens(our_tokens, oga_tokens) if oga_tokens else {}

    # Glaux: per-section alignment (different base text, use section refs to stay in sync)
    glaux_by_section = read_glaux_by_section(group_id, work_short)
    our_by_section = read_our_tokens_by_section(work_id)

    glaux_aligned = {}
    if glaux_by_section:
        for section_ref, our_section_tokens in our_by_section.items():
            glaux_section = glaux_by_section.get(section_ref, [])
            if glaux_section:
                section_result = align_tokens(our_section_tokens, glaux_section)
                glaux_aligned.update(section_result)

    out_path = ONE_DIR / work_id / "lemma.tsv"
    agree = 0
    disagree = 0
    oga_only = 0
    glaux_only = 0
    neither = 0

    with open(out_path, "w") as f:
        f.write("token_ref\tlemma\tpostag\toga_lemma\tglaux_lemma\toga_postag\tglaux_postag\tnotes\n")

        for token_id, token_text in our_tokens:
            oga = oga_aligned.get(token_id)
            glaux = glaux_aligned.get(token_id)

            oga_lemma = oga["lemma"] if oga else ""
            glaux_lemma = glaux["lemma"] if glaux else ""
            oga_postag = oga["postag"] if oga else ""
            glaux_postag = glaux["postag"] if glaux else ""

            notes = ""
            if oga_lemma and glaux_lemma:
                if fold(oga_lemma) == fold(glaux_lemma):
                    lemma = glaux_lemma
                    postag = glaux_postag if glaux_postag else oga_postag
                    agree += 1
                else:
                    lemma = glaux_lemma
                    postag = glaux_postag
                    notes = "DISAGREE"
                    disagree += 1
            elif glaux_lemma:
                lemma = glaux_lemma
                postag = glaux_postag
                notes = "glaux_only"
                glaux_only += 1
            elif oga_lemma:
                lemma = oga_lemma
                postag = oga_postag
                notes = "oga_only"
                oga_only += 1
            else:
                lemma = ""
                postag = ""
                notes = "unmatched"
                neither += 1

            f.write(
                f"{token_id}\t{lemma}\t{postag}"
                f"\t{oga_lemma}\t{glaux_lemma}"
                f"\t{oga_postag}\t{glaux_postag}"
                f"\t{notes}\n"
            )

    return {
        "tokens": len(our_tokens),
        "agree": agree,
        "disagree": disagree,
        "oga_only": oga_only,
        "glaux_only": glaux_only,
        "unmatched": neither,
        "oga_coverage": len(oga_aligned),
        "glaux_coverage": len(glaux_aligned),
    }


def main():
    works_path = ONE_DIR / "works.tsv"
    total = {"tokens": 0, "agree": 0, "disagree": 0, "oga_only": 0, "glaux_only": 0, "unmatched": 0}

    for line in open(works_path):
        if line.startswith("work_id\t"):
            continue
        work_id = line.split("\t")[0]
        stats = align_work(work_id)

        covered = stats["agree"] + stats["disagree"]
        pct = covered / stats["tokens"] * 100 if stats["tokens"] else 0
        agr = stats["agree"] / covered * 100 if covered else 0

        print(
            f"  {work_id}: {stats['tokens']:,} tok, "
            f"{pct:.0f}% covered, "
            f"{agr:.0f}% agree, "
            f"{stats['disagree']} disagree, "
            f"{stats['unmatched']} unmatched"
        )

        for k in total:
            total[k] += stats[k]

    print()
    covered = total["agree"] + total["disagree"]
    print(f"  Total: {total['tokens']:,} tokens")
    print(f"  Both sources: {covered:,} ({covered/total['tokens']*100:.1f}%)")
    if covered:
        print(f"  Agreement: {total['agree']:,} ({total['agree']/covered*100:.1f}%)")
        print(f"  Disagreement: {total['disagree']:,} ({total['disagree']/covered*100:.1f}%)")
    print(f"  Unmatched: {total['unmatched']:,} ({total['unmatched']/total['tokens']*100:.1f}%)")


if __name__ == "__main__":
    main()
