# Attic Prose Vocabulary Corpus

A balanced corpus of Attic prose for vocabulary learning, organised by genre.

## Corpus Composition

### Philosophy/Dialogue — ~198,000 tokens

#### Plato — ~125,000 tokens

| Work | CTS URN | Tokens |
|------|---------|--------|
| Euthyphro | `urn:cts:greekLit:tlg0059.tlg001` | 5,421 |
| Apology | `urn:cts:greekLit:tlg0059.tlg002` | 8,817 |
| Crito | `urn:cts:greekLit:tlg0059.tlg003` | 4,290 |
| Symposium | `urn:cts:greekLit:tlg0059.tlg011` | 17,496 |
| Republic | `urn:cts:greekLit:tlg0059.tlg030` | 88,611 |

#### Xenophon (Socratic works) — ~73,000 tokens

| Work | CTS URN | Tokens |
|------|---------|--------|
| Memorabilia | `urn:cts:greekLit:tlg0032.tlg002` | ~36,000 |
| Symposium | `urn:cts:greekLit:tlg0032.tlg003` | ~18,000 |
| Oeconomicus | `urn:cts:greekLit:tlg0032.tlg004` | ~10,000 |
| Apology | `urn:cts:greekLit:tlg0032.tlg014` | ~9,000 |

### Oration — ~171,000 tokens

#### Lysias — ~60,000 tokens

All 25 extant orations in Perseus: `urn:cts:greekLit:tlg0540.*`

(001, 002, 003, 004, 005, 006, 007, 008, 009, 010, 012, 013, 014, 015, 016, 017, 018, 019, 020, 022, 023, 025, 026, 032, 033)

#### Demosthenes — ~58,000 tokens

| Work | CTS URN | Tokens |
|------|---------|--------|
| Olynthiac 1 | `urn:cts:greekLit:tlg0014.tlg001` | 1,843 |
| Philippic 1 | `urn:cts:greekLit:tlg0014.tlg004` | 3,302 |
| On the Peace | `urn:cts:greekLit:tlg0014.tlg005` | 1,463 |
| Second Philippic | `urn:cts:greekLit:tlg0014.tlg006` | 2,001 |
| On the Crown | `urn:cts:greekLit:tlg0014.tlg018` | 22,494 |
| Against Leptines | `urn:cts:greekLit:tlg0014.tlg020` | 11,391 |
| Against Meidias | `urn:cts:greekLit:tlg0014.tlg021` | 15,786 |

#### Isocrates — ~53,000 tokens

| Work | CTS URN | Tokens |
|------|---------|--------|
| Demonicus | `urn:cts:greekLit:tlg0010.tlg007` | 2,912 |
| Against the Sophists | `urn:cts:greekLit:tlg0010.tlg008` | 1,334 |
| Helen | `urn:cts:greekLit:tlg0010.tlg009` | 3,764 |
| Panegyricus | `urn:cts:greekLit:tlg0010.tlg011` | 10,854 |
| Antidosis | `urn:cts:greekLit:tlg0010.tlg019` | 17,749 |
| Panathenaicus | `urn:cts:greekLit:tlg0010.tlg021` | 15,942 |

### History — ~154,000 tokens

| Author | Work | Sections | CTS URN | Tokens |
|--------|------|----------|---------|--------|
| Thucydides | History | Books 1–5 | `urn:cts:greekLit:tlg0003.tlg001:1–5` | ~97,000 |
| Xenophon | Anabasis | all | `urn:cts:greekLit:tlg0032.tlg006` | 57,228 |

## Summary

| Genre | Tokens |
|-------|--------|
| Philosophy/Dialogue | ~198,000 |
| Oration | ~171,000 |
| History | ~154,000 |
| **Total** | **~523,000** |

## Base Text Sources

Most base texts are extracted from Perseus canonical-greekLit TEI XML via `scripts/extract_base.py`.

Exception: Plato's Euthyphro uses the higher-quality text from [plato-texts](https://github.com/jtauber/plato-texts) (converted via `scripts/convert_plato_texts.py`), as Perseus only has a `grc1` edition with significant encoding and accentuation issues.

## Tagging Sources

- [Opera Graeca Adnotata (OGA)](https://github.com/OperaGraecaAdnotata/OGA)
- [Greek Dependency Trees (Gorman)](https://github.com/vgorman1/Greek-Dependency-Trees)
- [Scaife Viewer Tagging Pipeline](https://github.com/scaife-viewer/tagging-pipeline)
- [GLAUx (Keersmaekers)](https://github.com/alekkeersmaekers/glaux)
