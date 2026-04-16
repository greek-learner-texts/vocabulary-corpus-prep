#!/usr/bin/env python3
"""
Generate HTML discrepancy reports for lemma alignment.

Reads: one/{work_id}/lemma.tsv, token.tsv, token_section.tsv
Writes: reports/lemma/{work_id}.html
"""

import html
from pathlib import Path
from collections import Counter

REPO_DIR = Path(__file__).parent.parent
ONE_DIR = REPO_DIR / "one"
REPORT_DIR = REPO_DIR / "reports" / "lemma"


def load_work(work_id: str) -> dict:
    """Load all data for a work."""
    # Tokens
    tokens = {}
    for line in open(ONE_DIR / work_id / "token.tsv"):
        if line.startswith("token_id\t"):
            continue
        parts = line.rstrip("\n").split("\t")
        tokens[parts[0]] = parts[1]

    # Token → section mapping
    token_section = {}
    for line in open(ONE_DIR / work_id / "token_section.tsv"):
        if line.startswith("section_ref\t"):
            continue
        parts = line.rstrip("\n").split("\t")
        token_section[parts[1]] = parts[0]

    # Lemmas
    lemmas = []
    for line in open(ONE_DIR / work_id / "lemma.tsv"):
        if line.startswith("token_ref\t"):
            continue
        parts = line.rstrip("\n").split("\t")
        while len(parts) < 8:
            parts.append("")
        lemmas.append({
            "token_id": parts[0],
            "lemma": parts[1],
            "postag": parts[2],
            "oga_lemma": parts[3],
            "glaux_lemma": parts[4],
            "oga_postag": parts[5],
            "glaux_postag": parts[6],
            "notes": parts[7],
            "form": tokens.get(parts[0], ""),
            "section": token_section.get(parts[0], ""),
        })

    return {"tokens": tokens, "lemmas": lemmas}


def generate_report(work_id: str, work_title: str, *, prev_id: str | None = None, next_id: str | None = None, type_slugs: dict | None = None) -> None:
    """Generate an HTML discrepancy report."""
    data = load_work(work_id)
    lemmas = data["lemmas"]
    if type_slugs is None:
        type_slugs = {}

    total = len(lemmas)
    disagree = [l for l in lemmas if l["notes"] == "DISAGREE"]
    unmatched = [l for l in lemmas if l["notes"] == "unmatched"]
    oga_only = [l for l in lemmas if l["notes"] == "oga_only"]
    glaux_only = [l for l in lemmas if l["notes"] == "glaux_only"]
    agree = total - len(disagree) - len(unmatched) - len(oga_only) - len(glaux_only)

    # Count distinct mismatch types
    disagree_type_set = set()
    for d in disagree:
        disagree_type_set.add((d["oga_lemma"], d["glaux_lemma"]))
    n_types = len(disagree_type_set)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORT_DIR / f"{work_id}.html"

    with open(out_path, "w") as f:
        f.write(f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>Lemma Report: {html.escape(work_title)}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;600&display=swap');
body {{ max-width: 1000px; margin: 2rem auto; font-family: 'Noto Sans', sans-serif;
    font-size: 15px; line-height: 1.6; color: #222; background: #fafafa; }}
h1 {{ font-size: 1.4rem; color: #333; border-bottom: 2px solid #333; padding-bottom: 0.5rem; }}
h2 {{ font-size: 1.1rem; color: #555; margin-top: 2rem; }}
.summary {{ background: #fff; border: 1px solid #ddd; padding: 1.5rem; border-radius: 4px; margin-bottom: 2rem; }}
.summary td, .summary th {{ padding: 4px 12px; text-align: left; }}
.bar {{ display: inline-block; height: 16px; border-radius: 2px; }}
.bar-agree {{ background: #4caf50; }}
.bar-disagree {{ background: #e64a19; }}
.bar-single {{ background: #2196f3; }}
.bar-unmatched {{ background: #bbb; }}
table.disc {{ border-collapse: collapse; width: 100%; margin-bottom: 1.5rem; }}
table.disc th {{ background: #f5f5f5; font-weight: 600; text-align: left; padding: 6px 10px; border-bottom: 2px solid #ddd; }}
table.disc td {{ padding: 5px 10px; border-bottom: 1px solid #eee; }}
table.disc tr:hover {{ background: #fff8e1; }}
.form {{ font-weight: 600; }}
.ref {{ color: #999; font-size: 0.85rem; }}
.mismatch {{ color: #e64a19; font-weight: 600; }}
a {{ color: #1565c0; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
.nav {{ font-size: 0.9rem; margin-bottom: 1rem; }}
@media (prefers-color-scheme: dark) {{
    body {{ color: #ddd; background: #1a1a1a; }}
    h1 {{ color: #eee; border-bottom-color: #555; }}
    h2 {{ color: #bbb; }}
    .summary {{ background: #252525; border-color: #444; }}
    table.disc th {{ background: #2a2a2a; border-bottom-color: #444; }}
    table.disc td {{ border-bottom-color: #333; }}
    table.disc tr:hover {{ background: #2a2510; }}
    .ref {{ color: #777; }}
    a {{ color: #7bb8e0; }}
}}
</style>
</head><body>
<h1>{html.escape(work_title)} — Lemma Report</h1>
""")

        # Top navigation
        nav = '<div class="nav"><a href="index.html">← Index</a>'
        if prev_id:
            nav += f' · <a href="{prev_id}.html">← Prev</a>'
        if next_id:
            nav += f' · <a href="{next_id}.html">Next →</a>'
        nav += '</div>\n'
        f.write(nav)

        # Summary bar
        w = 600
        agree_w = int(agree / total * w) if total else 0
        disagree_w = int(len(disagree) / total * w) if total else 0
        single_w = int((len(oga_only) + len(glaux_only)) / total * w) if total else 0
        unmatched_w = w - agree_w - disagree_w - single_w

        f.write(f"""<div class="summary">
<p><strong>{total:,}</strong> tokens</p>
<div>
<span class="bar bar-agree" style="width:{agree_w}px" title="Agree: {agree:,}"></span><!--
--><span class="bar bar-disagree" style="width:{disagree_w}px" title="Disagree: {len(disagree):,}"></span><!--
--><span class="bar bar-single" style="width:{single_w}px" title="One source: {len(oga_only)+len(glaux_only):,}"></span><!--
--><span class="bar bar-unmatched" style="width:{unmatched_w}px" title="Unmatched: {len(unmatched):,}"></span>
</div>
<table>
<tr><td>🟢 Both agree</td><td><strong>{agree:,}</strong> ({agree/total*100:.1f}%)</td></tr>
<tr><td>🔴 Disagree</td><td><strong>{len(disagree):,}</strong> tokens ({len(disagree)/total*100:.1f}%) — <strong>{n_types}</strong> distinct types</td></tr>
<tr><td>🔵 One source only</td><td><strong>{len(oga_only)+len(glaux_only):,}</strong> (OGA: {len(oga_only):,}, Glaux: {len(glaux_only):,})</td></tr>
<tr><td>⚪ Unmatched</td><td><strong>{len(unmatched):,}</strong> ({len(unmatched)/total*100:.1f}%)</td></tr>
</table>
</div>
""")

        # Disagreements table
        if disagree:
            f.write(f"<h2>Disagreements ({len(disagree):,} tokens, {n_types} types)</h2>\n")
            f.write('<table class="disc">\n')
            f.write("<tr><th>Ref</th><th>Form</th><th>OGA lemma</th><th>OGA POS</th><th>Glaux lemma</th><th>Glaux POS</th><th></th></tr>\n")
            for d in disagree:
                key = (d["oga_lemma"], d["glaux_lemma"])
                slug = type_slugs.get(key, "")
                link_cell = f'<a href="mismatches/{slug}.html">all</a>' if slug else ""
                f.write(
                    f'<tr>'
                    f'<td class="ref">{html.escape(d["section"])}</td>'
                    f'<td class="form">{html.escape(d["form"])}</td>'
                    f'<td class="mismatch">{html.escape(d["oga_lemma"])}</td>'
                    f'<td>{html.escape(d["oga_postag"])}</td>'
                    f'<td class="mismatch">{html.escape(d["glaux_lemma"])}</td>'
                    f'<td>{html.escape(d["glaux_postag"])}</td>'
                    f'<td>{link_cell}</td>'
                    f'</tr>\n'
                )
            f.write("</table>\n")

        # Unmatched tokens (first 100)
        if unmatched:
            f.write(f"<h2>Unmatched ({len(unmatched):,})</h2>\n")
            shown = unmatched[:100]
            f.write('<table class="disc">\n')
            f.write("<tr><th>Ref</th><th>Form</th></tr>\n")
            for u in shown:
                f.write(
                    f'<tr><td class="ref">{html.escape(u["section"])}</td>'
                    f'<td>{html.escape(u["form"])}</td></tr>\n'
                )
            if len(unmatched) > 100:
                f.write(f'<tr><td colspan="2">... and {len(unmatched)-100} more</td></tr>\n')
            f.write("</table>\n")

        # Bottom navigation
        f.write('<div class="nav" style="margin-top:2rem;padding-top:1rem;border-top:1px solid #ddd;">')
        f.write(nav.replace('<div class="nav">', '').replace('</div>', ''))
        f.write('</div>\n')

        f.write("</body></html>\n")


def generate_index(work_stats: list[dict]) -> None:
    """Generate index.html with summary table."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORT_DIR / "index.html"

    total_tokens = sum(s["total"] for s in work_stats)
    total_agree = sum(s["agree"] for s in work_stats)
    total_disagree = sum(s["disagree"] for s in work_stats)
    total_unmatched = sum(s["unmatched"] for s in work_stats)

    with open(out_path, "w") as f:
        f.write(f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>Lemma Alignment — Index</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;600&display=swap');
body {{ max-width: 1100px; margin: 2rem auto; font-family: 'Noto Sans', sans-serif;
    font-size: 15px; line-height: 1.6; color: #222; background: #fafafa; }}
h1 {{ font-size: 1.4rem; color: #333; border-bottom: 2px solid #333; padding-bottom: 0.5rem; }}
.totals {{ background: #fff; border: 1px solid #ddd; padding: 1rem 1.5rem; border-radius: 4px; margin-bottom: 2rem; }}
table {{ border-collapse: collapse; width: 100%; }}
th {{ background: #f5f5f5; font-weight: 600; text-align: left; padding: 6px 10px; border-bottom: 2px solid #ddd; }}
td {{ padding: 5px 10px; border-bottom: 1px solid #eee; }}
tr:hover {{ background: #fff8e1; }}
.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
.pct {{ text-align: right; color: #888; font-size: 0.85rem; }}
.bar {{ display: inline-block; height: 12px; border-radius: 2px; }}
.bar-agree {{ background: #4caf50; }}
.bar-disagree {{ background: #e64a19; }}
.bar-unmatched {{ background: #bbb; }}
a {{ color: #1565c0; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
@media (prefers-color-scheme: dark) {{
    body {{ color: #ddd; background: #1a1a1a; }}
    h1 {{ color: #eee; border-bottom-color: #555; }}
    .totals {{ background: #252525; border-color: #444; }}
    th {{ background: #2a2a2a; border-bottom-color: #444; }}
    td {{ border-bottom-color: #333; }}
    tr:hover {{ background: #2a2510; }}
    a {{ color: #7bb8e0; }}
}}
</style>
</head><body>
<h1>Lemma Alignment — Index</h1>
<div class="totals">
<strong>{total_tokens:,}</strong> tokens ·
<strong>{total_agree:,}</strong> agree ({total_agree/total_tokens*100:.1f}%) ·
<strong>{total_disagree:,}</strong> disagree ·
<strong>{total_unmatched:,}</strong> unmatched ({total_unmatched/total_tokens*100:.1f}%)
<br><a href="mismatches/index.html">View disagreements by type →</a>
</div>
<table>
<tr><th>Work</th><th>Author</th><th class="num">Tokens</th><th>Coverage</th><th class="num">Disagree</th><th class="num">Unmatched</th></tr>
""")

        for s in work_stats:
            bar_w = 120
            agree_w = int(s["agree"] / s["total"] * bar_w) if s["total"] else 0
            disagree_w = int(s["disagree"] / s["total"] * bar_w) if s["total"] else 0
            unmatched_w = bar_w - agree_w - disagree_w

            f.write(
                f'<tr>'
                f'<td><a href="{s["work_id"]}.html">{html.escape(s["title"])}</a></td>'
                f'<td>{html.escape(s["author"])}</td>'
                f'<td class="num">{s["total"]:,}</td>'
                f'<td>'
                f'<span class="bar bar-agree" style="width:{agree_w}px"></span>'
                f'<span class="bar bar-disagree" style="width:{disagree_w}px"></span>'
                f'<span class="bar bar-unmatched" style="width:{unmatched_w}px"></span>'
                f'</td>'
                f'<td class="num">{s["disagree"]:,}</td>'
                f'<td class="num">{s["unmatched"]:,}</td>'
                f'</tr>\n'
            )

        f.write("</table>\n</body></html>\n")


def generate_mismatch_index(all_mismatches: list[dict]) -> None:
    """Generate mismatch type index and per-type pages."""
    from collections import defaultdict

    # Group by (oga_lemma, glaux_lemma)
    by_type: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for m in all_mismatches:
        key = (m["oga_lemma"], m["glaux_lemma"])
        by_type[key].append(m)

    # Sort by frequency
    sorted_types = sorted(by_type.items(), key=lambda x: -len(x[1]))

    MISMATCH_DIR = REPORT_DIR / "mismatches"
    MISMATCH_DIR.mkdir(parents=True, exist_ok=True)

    # Index page
    with open(MISMATCH_DIR / "index.html", "w") as f:
        f.write(f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>Lemma Mismatches — By Type</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;600&display=swap');
body {{ max-width: 900px; margin: 2rem auto; font-family: 'Noto Sans', sans-serif;
    font-size: 15px; line-height: 1.6; color: #222; background: #fafafa; }}
h1 {{ font-size: 1.4rem; color: #333; border-bottom: 2px solid #333; padding-bottom: 0.5rem; }}
.nav {{ font-size: 0.9rem; margin-bottom: 1rem; }}
table {{ border-collapse: collapse; width: 100%; }}
th {{ background: #f5f5f5; font-weight: 600; text-align: left; padding: 6px 10px; border-bottom: 2px solid #ddd; }}
td {{ padding: 5px 10px; border-bottom: 1px solid #eee; }}
tr:hover {{ background: #fff8e1; }}
.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
a {{ color: #1565c0; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
@media (prefers-color-scheme: dark) {{
    body {{ color: #ddd; background: #1a1a1a; }}
    h1 {{ color: #eee; border-bottom-color: #555; }}
    th {{ background: #2a2a2a; border-bottom-color: #444; }}
    td {{ border-bottom-color: #333; }}
    tr:hover {{ background: #2a2510; }}
    a {{ color: #7bb8e0; }}
}}
</style>
</head><body>
<h1>Lemma Mismatches — By Type</h1>
<div class="nav"><a href="../index.html">← Lemma Index</a></div>
<p><strong>{len(sorted_types):,}</strong> mismatch types, <strong>{len(all_mismatches):,}</strong> total tokens</p>
<table>
<tr><th class="num">Count</th><th>OGA lemma</th><th>Glaux lemma</th><th>Sample forms</th></tr>
""")
        for i, ((oga, glaux), instances) in enumerate(sorted_types):
            slug = f"m{i:04d}"
            forms = sorted(set(m["form"] for m in instances))[:5]
            form_str = ", ".join(forms)
            f.write(
                f'<tr>'
                f'<td class="num"><a href="{slug}.html">{len(instances)}</a></td>'
                f'<td>{html.escape(oga)}</td>'
                f'<td>{html.escape(glaux)}</td>'
                f'<td style="font-size:0.85rem;color:#777">{html.escape(form_str)}</td>'
                f'</tr>\n'
            )
        f.write("</table>\n</body></html>\n")

    # Per-type pages
    for i, ((oga, glaux), instances) in enumerate(sorted_types):
        slug = f"m{i:04d}"
        with open(MISMATCH_DIR / f"{slug}.html", "w") as f:
            f.write(f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<title>{html.escape(oga)} vs {html.escape(glaux)}</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans:wght@400;600&display=swap');
body {{ max-width: 900px; margin: 2rem auto; font-family: 'Noto Sans', sans-serif;
    font-size: 15px; line-height: 1.6; color: #222; background: #fafafa; }}
h1 {{ font-size: 1.3rem; color: #333; }}
.nav {{ font-size: 0.9rem; margin-bottom: 1rem; }}
table {{ border-collapse: collapse; width: 100%; }}
th {{ background: #f5f5f5; font-weight: 600; text-align: left; padding: 6px 10px; border-bottom: 2px solid #ddd; }}
td {{ padding: 5px 10px; border-bottom: 1px solid #eee; }}
.form {{ font-weight: 600; }}
.ref {{ color: #999; font-size: 0.85rem; }}
a {{ color: #1565c0; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
@media (prefers-color-scheme: dark) {{
    body {{ color: #ddd; background: #1a1a1a; }}
    h1 {{ color: #eee; }}
    th {{ background: #2a2a2a; border-bottom-color: #444; }}
    td {{ border-bottom-color: #333; }}
    .ref {{ color: #777; }}
    a {{ color: #7bb8e0; }}
}}
</style>
</head><body>
<h1>OGA: <em>{html.escape(oga)}</em> vs Glaux: <em>{html.escape(glaux)}</em></h1>
<div class="nav"><a href="index.html">← Mismatch Index</a></div>
<p><strong>{len(instances)}</strong> occurrences</p>
<table>
<tr><th>Work</th><th>Section</th><th>Form</th><th>OGA POS</th><th>Glaux POS</th></tr>
""")
            for m in instances:
                f.write(
                    f'<tr>'
                    f'<td><a href="../{m["work_id"]}.html">{html.escape(m["work_id"])}</a></td>'
                    f'<td class="ref">{html.escape(m["section"])}</td>'
                    f'<td class="form">{html.escape(m["form"])}</td>'
                    f'<td>{html.escape(m["oga_postag"])}</td>'
                    f'<td>{html.escape(m["glaux_postag"])}</td>'
                    f'</tr>\n'
                )
            f.write("</table>\n</body></html>\n")

    print(f"  Generated {len(sorted_types)} mismatch type pages")


def main():
    # Load work metadata
    works = []
    for line in open(ONE_DIR / "works.tsv"):
        if line.startswith("work_id\t"):
            continue
        parts = line.rstrip("\n").split("\t")
        works.append({
            "work_id": parts[0],
            "author": parts[1],
            "title": parts[2],
            "genre": parts[3] if len(parts) > 3 else "",
        })

    work_ids = [w["work_id"] for w in works]

    # Pass 1: collect all mismatches to build type→slug mapping
    all_mismatches = []
    for w in works:
        data = load_work(w["work_id"])
        for entry in data["lemmas"]:
            if entry["notes"] == "DISAGREE":
                all_mismatches.append({
                    "work_id": w["work_id"],
                    "form": entry["form"],
                    "section": entry["section"],
                    "oga_lemma": entry["oga_lemma"],
                    "glaux_lemma": entry["glaux_lemma"],
                    "oga_postag": entry["oga_postag"],
                    "glaux_postag": entry["glaux_postag"],
                })

    # Build type→slug mapping (sorted by frequency)
    from collections import defaultdict
    by_type: dict[tuple[str, str], list] = defaultdict(list)
    for m in all_mismatches:
        by_type[(m["oga_lemma"], m["glaux_lemma"])].append(m)
    sorted_types = sorted(by_type.items(), key=lambda x: -len(x[1]))
    type_slugs = {key: f"m{i:04d}" for i, (key, _) in enumerate(sorted_types)}

    # Pass 2: generate per-work reports (with slug links)
    work_stats = []
    for i, w in enumerate(works):
        prev_id = work_ids[i - 1] if i > 0 else None
        next_id = work_ids[i + 1] if i < len(works) - 1 else None
        full_title = f"{w['author']}, {w['title']}"

        generate_report(w["work_id"], full_title,
                        prev_id=prev_id, next_id=next_id, type_slugs=type_slugs)

        # Collect stats for index
        lemmas = open(ONE_DIR / w["work_id"] / "lemma.tsv").readlines()[1:]
        total = len(lemmas)
        disagree = sum(1 for l in lemmas if "DISAGREE" in l)
        unmatched = sum(1 for l in lemmas if l.rstrip("\n").split("\t")[-1] == "unmatched")
        agree = total - disagree - unmatched - sum(1 for l in lemmas if "only" in l.split("\t")[-1])

        work_stats.append({
            "work_id": w["work_id"],
            "author": w["author"],
            "title": w["title"],
            "total": total,
            "agree": agree,
            "disagree": disagree,
            "unmatched": unmatched,
        })

    generate_index(work_stats)
    generate_mismatch_index(all_mismatches)
    print(f"Generated {len(works)} reports + index + {len(all_mismatches):,} mismatches in {REPORT_DIR}/")


if __name__ == "__main__":
    main()
