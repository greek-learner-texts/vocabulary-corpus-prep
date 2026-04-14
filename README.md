# Greek Learner Texts Vocabulary Corpus Prep

Extraction and normalization of a balanced Attic Prose tagged corpus for the Greek Learner Texts Project.

See [CORPUS.md](CORPUS.md) for the definitive corpus composition (texts, genres, token counts).

## Directory Structure

- `base-texts/` — chunked base texts extracted from Perseus TEI XML
- `tokenized-texts/` — tokenized base texts
- `tagged-texts/` — extracted taggings from multiple sources (with minor manual corrections)
- `aligned-tagging/` — aligned taggings across sources for comparison
- `counts.tsv` — token counts per work per source
- `reports/` — greek-check validation reports (not committed)

## Scripts

- `scripts/extract_base.py` — extract base texts from Perseus canonical-greekLit
- `scripts/tokens.py` — tokenize base texts (handles crasis, negation compounds, punctuation)
- `scripts/gather.py` — extract tagged texts from OGA, Glaux, Gorman, and Tagging Pipeline
- `scripts/align.py` — align tokenized base text with multiple taggings
- `scripts/stats.py` — produce token counts
- `scripts/check_texts.py` — run greek-check validation (levels 1–3) on all base texts
