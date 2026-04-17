# Lemma Lattice for the Attic Prose Vocabulary Corpus

## Background

No two resources lemmatise the same way, and no single lemma level serves all
purposes. A lemma is a key linking a token to an entry in a lexical resource —
but different resources have different entries, and different use cases need
different granularity.

This problem was first articulated by James Tauber and Ulrik Sandborg-Petersen
in 2006 and presented at SBL 2017 as the **lemma lattice** approach: instead
of a flat mapping from tokens to lemmas, we use a partially ordered set of
lemma levels, where finer-grained levels can be grouped into coarser ones
depending on purpose.

## The Problem in This Corpus

Our corpus alignment (OGA vs Glaux) produces 10,031 disagreement tokens across
1,981 distinct mismatch types. These fall into exactly 10 categories — and
each category corresponds to a **relationship between levels** in the lemma
lattice.

## Lattice Levels

We propose three levels, from finest to coarsest:

### Level 1: Flexeme (morphological citation form)

The finest grain. Each distinct stem pattern, dialect variant, or voice form
gets its own entry. This is the level needed for morphological generation and
paradigm tables.

Examples:
- μᾶλλον (comparative adverb) — distinct from μάλα (positive)
- εἶπον (aorist stem) — distinct from λέγω (present stem)
- ἀνάπειρος — distinct from ἀνάπηρος (different stems)
- χράομαι (middle) — distinct from χράω (active)
- καταλιμπάνω (dialectal) — distinct from καταλείπω (standard)

### Level 2: Lexeme (dictionary entry)

The standard dictionary headword. Suppletive stems are grouped together,
comparatives/superlatives are cited under the positive, dialect variants
are merged.

Examples:
- μᾶλλον → **μάλα**
- εἶπον → **λέγω**
- ἀνάπειρος, ἀνάπηρος → **ἀνάπηρος**
- χράομαι → **χράω**
- καταλιμπάνω → **καταλείπω**

### Level 3: Lemma group (cross-resource key)

The coarsest grain. Used for linking across resources that make different
headword choices — Strongs numbers, BDAG entries, LSJ entries.

This level is less relevant for our Attic prose corpus (which isn't mapping
to NT resources) but the structure supports it.

## How Our Mismatch Categories Map to the Lattice

| Category | Count | Lattice interpretation |
|---|---|---|
| comparative_lemma (2,190) | Level 1→2 | OGA uses flexeme (μᾶλλον), Glaux uses lexeme (μάλα) |
| suppletive_verb (1,323) | Level 1→2 | OGA uses flexeme (εἶπον), Glaux uses lexeme (λέγω) |
| variant_lemma (1,316) | Level 1→1 or 1→2 | Different flexemes of the same lexeme (dialect, spelling) |
| artefact (1,178) | — | Not a real disagreement (alignment errors, encoding) |
| capitalisation (1,077) | Level 1→1 | Same flexeme, different orthographic convention |
| pos_ambiguity (983) | Ambiguous | Genuinely different lexemes sharing a form — needs context |
| homographic (827) | Ambiguous | Different lexemes entirely — needs context |
| related_form (481) | Level 2→2 | Different lexeme grouping choices (ἐπεί vs ἐπειδή) |
| voice_lemma (450) | Level 1→2 | Different citation form convention (χράομαι vs χράω) |
| compound_vs_simple (206) | Level 2→2 | Different lexeme boundary (ὅσπερ: own entry or under ὅς?) |

## Resolution Strategy

### Auto-resolvable (no human needed)

- **capitalisation** (1,077 tokens): normalise to standard form. Trivial.
- **artefact** (1,178 tokens): discard. Not real disagreements.

Total: **2,255 tokens** (22% of disagreements) → eliminate entirely.

### Policy decisions (apply a rule)

These are systematic: one source uses flexeme-level lemmas, the other uses
lexeme-level. We choose the **lexeme level** (Level 2) for the vocabulary
corpus, since the purpose is vocabulary learning.

- **comparative_lemma** (2,190): cite under positive → use Glaux
- **suppletive_verb** (1,323): cite under present stem → use Glaux
- **voice_lemma** (450): cite under active/standard form → use Glaux
- **variant_lemma** (1,316): cite under standard Attic form → use Glaux
- **compound_vs_simple** (206): case by case, but mostly own lemma → use OGA

Total: **5,485 tokens** (55%) → resolve by rule.

### Context-dependent (need per-token adjudication)

- **pos_ambiguity** (983): adjective/adverb, verb/noun — form is shared,
  meaning differs. Need syntactic context.
- **homographic** (827): ὅς/ὁ, δεῖ/δέω — genuinely different words.
  Need syntactic context.
- **related_form** (481): ἐπεί/ἐπειδή, ἄν/ἐάν — borderline cases.

Total: **2,291 tokens** (23%) → need human review or syntactic heuristics.

## Implementation

### Phase 1: Build the lattice data structure

A TSV file mapping flexeme → lexeme:

```
flexeme_id    lexeme_id    relationship
μᾶλλον        μάλα         comparative
μάλιστα       μάλα         superlative
εἶπον         λέγω         suppletive_aorist
ἐρῶ           λέγω         suppletive_future
χράομαι       χράω         voice_variant
καταλιμπάνω   καταλείπω    dialect_variant
```

Seeded from the mismatch taxonomy (1,981 entries already categorised).

### Phase 2: Apply auto-resolution

For each token in lemma.tsv where sources disagree:
1. Look up the mismatch type in the taxonomy
2. If category is `capitalisation` or `artefact` → resolve automatically
3. If category is a Level 1→2 mapping → use lexeme-level (Glaux) lemma
4. If category is ambiguous → flag for review

### Phase 3: Adjudicate ambiguous tokens

For pos_ambiguity and homographic tokens (2,291):
- Use POS tags from both sources as evidence
- Use syntactic context (preceding article, preposition, etc.)
- Where POS tags agree → trust POS to disambiguate lemma
- Where POS tags disagree → flag for manual review

### Phase 4: Produce final lemmatisation

Output: `one/{work_id}/lemma_final.tsv`

```
token_ref    lemma    lexeme    confidence    source
1            καταβαίνω    καταβαίνω    both    agree
2            χθές         χθές         both    agree
...
439          εἶπον        λέγω         lattice suppletive_verb
...
827          δεῖ          δέω          manual  homographic
```

## Connection to Vocabulary Learning

The vocabulary corpus's purpose is **frequency lists for learners**. For this:

- Level 2 (lexeme) is the right granularity: learners look up λέγω, not εἶπον
- But Level 1 (flexeme) data is preserved: a learner tool can show "this form
  (εἶπον) is the aorist of λέγω" — which requires knowing the flexeme→lexeme
  mapping
- The lattice makes this bidirectional: from a dictionary entry (λέγω), show
  all forms including suppletive ones; from a text token (εἶπον), link to the
  dictionary entry

This is exactly the infrastructure James built for MorphGNT/NT Greek, now
extended to Classical Attic prose.
