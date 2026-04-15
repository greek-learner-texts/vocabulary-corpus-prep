# Greek Learner Texts Vocabulary Corpus Prep

Extraction and normalization of a balanced Attic Prose tagged corpus for the Greek Learner Texts Project.

See [CORPUS.md](CORPUS.md) for the definitive corpus composition (texts, genres, token counts).

## Canonical Output

The `one/` directory contains the canonical ONE-format base texts for all downstream work:

- `one/works.tsv` — work metadata (work_id, author, title, genre)
- `one/{work_id}/section.tsv` — clean base text per work (section_id, text)
- `one/verse_dialect.tsv` — stand-off annotations for verse quotations, dialect passages, and oracles

49 works, 10,076 sections, 6 authors, 3 genres (philosophy, oration, history).

## Directory Structure

- `one/` — canonical ONE-format base texts (clean, no markup)
- `base-texts/` — intermediate extracted texts (may contain XML tags)
- `annotations/` — verse/dialect/oracle annotations and per-text settings
- `scripts/` — extraction, cleaning, validation, and build pipeline
- `tokenized-texts/` — tokenized base texts
- `tagged-texts/` — extracted taggings from multiple sources
- `aligned-tagging/` — aligned taggings across sources for comparison
- `reports/` — greek-check validation reports (not committed)

## Pipeline

```
Perseus TEI XML / plato-texts
        |
        v
extract_base.py / convert_plato_texts.py   --> base-texts/*.base.tsv
        |
        v
fix_base_texts.py                           --> base-texts/*.base.tsv (patched)
        |
        v
check_texts.py                              --> reports/*.html
        |
        v
build_one.py                                --> one/*/section.tsv
                                                one/verse_dialect.tsv
                                                one/works.tsv
```

## Scripts

### Extraction and cleaning
- `scripts/extract_base.py` — extract base texts from Perseus canonical-greekLit TEI XML
- `scripts/convert_plato_texts.py` — convert plato-texts GLTP format to base-text TSV
- `scripts/fix_base_texts.py` — post-extraction cleanup (documented source errors, apostrophe normalization)
- `scripts/build_one.py` — build canonical ONE-format output from base texts

### Validation
- `scripts/check_texts.py` — run greek-check validation (levels 1-3) on all base texts
- `scripts/find_verse.py` — discover verse quotations and dialect passages via structural markers

### Tokenization and alignment
- `scripts/tokens.py` — tokenize base texts (handles crasis, negation compounds, punctuation)
- `scripts/gather.py` — extract tagged texts from OGA, Glaux, Gorman, and Tagging Pipeline
- `scripts/align.py` — align tokenized base text with multiple taggings
- `scripts/stats.py` — produce token counts
- `scripts/sampling.py` — corpus sampling

## Base Text Quality

The base texts have been validated with [greek-check](https://github.com/jtauber/greek-check) at three levels (encoding, graphotactics, accentuation). Starting from 4,591 errors, the corpus has been cleaned to 35 remaining warnings, all editorial accent conventions in the source editions.

24 of 49 texts are completely error-free. 122 verse/dialect/oracle sections are annotated for downstream filtering.
