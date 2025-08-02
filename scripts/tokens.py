#!/usr/bin/env python3

from os import makedirs
from pathlib import Path
import re

from lxml import etree  # type: ignore

BASE_TEXTS_DIR = Path(__file__).parent.parent / "base-texts"

path = BASE_TEXTS_DIR / "tlg0003" / "tlg0003.tlg001.perseus-grc2.base.tsv"

def get_tokens():
    for line in open(path):
        ref, text = line.strip().split("\t")
        text = re.sub(r'<bibl[^<]+</bibl>', '', text)
        text = etree.fromstring(text)
        text = etree.tostring(text, encoding="unicode", method="text")

        text = text.replace("οὔτ᾽", "οὔτ’")
        text = text.replace("οὐδ᾽", "οὐδ’")

        text = re.sub(r" \]", r"]", text)
        text = re.sub(r"(\w+)\.(\w+)", r"\1. \2", text)
        text = re.sub(r"(\w+),(\w+)", r"\1, \2", text)

        text = text.replace(".’", ". ’")
        text = text.replace(",’", ", ’")
        text = text.replace(";’", "; ’")

        idx = 1
        for token in text.split():
            while token[0] in "[(‘〈":
                yield ref, idx, token[0]
                idx += 1
                token = token[1:]
            tail = ""
            while token and token[-1] in ".,·])〉;":
                tail = token[-1] + tail
                token = token[:-1]
            if token in [
                "οὔτε", "οὐδ’", "οὐδὲ", "οὔθ’", "οὔτ’",
                "μηδέ", "μηδὲ", "μήτε", "μηδ’", "μήθ’", "μήτ’",
                "εἴτε",
            ]:
                yield ref, idx, token[:2]
                idx += 1
                yield ref, idx, token[2:]
            elif token.startswith(("κἀ", "κἂ")):
                yield ref, idx, "κ"
                idx += 1
                yield ref, idx, token[1:]
            elif token.startswith(("τἀ", "τἆ", "ταὐ", "τοὐ", "τοὔ")):
                yield ref, idx, "τ"
                idx += 1
                yield ref, idx, token[1:]
            else:
                yield ref, idx, token
            idx += 1
            for token in tail:
                yield ref, idx, token
                idx += 1


makedirs("tokenized-texts")
with open("tokenized-texts/tlg0003.tlg001.tokens.tsv", "w") as g:
    for ref, idx, token in get_tokens():
        print(ref, idx, token, sep="\t", file=g)

