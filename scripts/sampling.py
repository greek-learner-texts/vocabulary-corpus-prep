#!/usr/bin/env python3

from collections import Counter, defaultdict
from pathlib import Path
from random import randint

REPO_DIR = Path(__file__).parent.parent
ALIGNED_TAGGING_DIR = REPO_DIR / "aligned-tagging"


lemmas_by_work = defaultdict(list)
pos_by_lemma = defaultdict(set)
group_lemmas = defaultdict(Counter)
work_lemmas = defaultdict(Counter)
lemma_counts2 = Counter()

for work_file in sorted(ALIGNED_TAGGING_DIR.iterdir()):
    with open(work_file) as f:
        work_id = ".".join(work_file.stem.split(".")[:2])
        f.readline()  # header
        for line in f:
            fields = line.split("\t")
            glaux_postag = fields[6]
            glaux_lemma = fields[9]
            if (
                glaux_postag
                and glaux_postag != "u--------"
                and glaux_lemma.lower() == glaux_lemma
            ):
                lemmas_by_work[work_id].append(glaux_lemma)
                pos_by_lemma[glaux_lemma].add(glaux_postag[0])
                group_lemmas[glaux_lemma][work_id.split(".")[0]] += 1
                work_lemmas[glaux_lemma][work_id] += 1
                lemma_counts2[glaux_lemma] += 1

offsets = {}
cummulative_tokens = 0
for work_id in sorted(lemmas_by_work):
    for lemma in lemmas_by_work[work_id]:
        cummulative_tokens += 1
        if work_id not in offsets:
            offsets[work_id] = [cummulative_tokens, cummulative_tokens]
        else:
            offsets[work_id][1] = cummulative_tokens

offsets = offsets.items()

WINDOW_SIZE = 1000


lemma_counts = Counter()

for i in range(1_000_000):
    offset = randint(1, cummulative_tokens)

    for work_id, r in offsets:
        if r[0] <= offset <= r[1]:
            break

    lemmas = set(lemmas_by_work[work_id][offset - r[0] : offset - r[0] + WINDOW_SIZE])

    for lemma in lemmas:
        lemma_counts[lemma] += 1


for lemma, count in lemma_counts.most_common():
    print(
        lemma,
        " ".join(sorted(pos_by_lemma[lemma])),
        lemma_counts2[lemma],
        len(group_lemmas[lemma]),
        len(work_lemmas[lemma]),
        count,
        sep="\t",
    )
