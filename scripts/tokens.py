#!/usr/bin/env python3

from os import makedirs
from pathlib import Path
import re

from lxml import etree  # type: ignore

BASE_TEXTS_DIR = Path(__file__).parent.parent / "base-texts"


def get_tokens(path):
    for line in open(path):
        ref, text = line.strip().split("\t")
        text = re.sub(r'<bibl[^<]+</bibl>', '', text)
        text = etree.fromstring(text)
        text = etree.tostring(text, encoding="unicode", method="text")

        text = text.replace("οὔτʼ", "οὔτ’")
        text = text.replace("οὔτ᾽", "οὔτ’")
        text = text.replace("οὐδʼ", "οὐδ’")
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


def tokenize(input_path, output_filename):
    makedirs("tokenized-texts", exist_ok=True)
    with open(f"tokenized-texts/{output_filename}", "w") as g:
        for ref, idx, token in get_tokens(input_path):
            print(ref, idx, token, sep="\t", file=g)


if __name__ == "__main__":
    tokenize(BASE_TEXTS_DIR / "tlg0003" / "tlg0003.tlg001.perseus-grc2.base.tsv", "tlg0003.tlg001.tokens.tsv")

    tokenize(BASE_TEXTS_DIR / "tlg0032" / "tlg0032.tlg006.perseus-grc2.base.tsv", "tlg0032.tlg006.tokens.tsv")

    tokenize(BASE_TEXTS_DIR / "tlg0010" / "tlg0010.tlg007.perseus-grc2.base.tsv", "tlg0010.tlg007.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0010" / "tlg0010.tlg008.perseus-grc2.base.tsv", "tlg0010.tlg008.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0010" / "tlg0010.tlg009.perseus-grc2.base.tsv", "tlg0010.tlg009.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0010" / "tlg0010.tlg011.perseus-grc2.base.tsv", "tlg0010.tlg011.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0010" / "tlg0010.tlg019.perseus-grc2.base.tsv", "tlg0010.tlg019.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0010" / "tlg0010.tlg021.perseus-grc2.base.tsv", "tlg0010.tlg021.tokens.tsv")

    tokenize(BASE_TEXTS_DIR / "tlg0014" / "tlg0014.tlg001.perseus-grc2.base.tsv", "tlg0014.tlg001.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0014" / "tlg0014.tlg004.perseus-grc2.base.tsv", "tlg0014.tlg004.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0014" / "tlg0014.tlg005.perseus-grc2.base.tsv", "tlg0014.tlg005.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0014" / "tlg0014.tlg006.perseus-grc2.base.tsv", "tlg0014.tlg006.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0014" / "tlg0014.tlg018.perseus-grc2.base.tsv", "tlg0014.tlg018.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0014" / "tlg0014.tlg020.perseus-grc2.base.tsv", "tlg0014.tlg020.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0014" / "tlg0014.tlg021.perseus-grc2.base.tsv", "tlg0014.tlg021.tokens.tsv")

    tokenize(BASE_TEXTS_DIR / "tlg0540" / "tlg0540.tlg001.perseus-grc2.base.tsv", "tlg0540.tlg001.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0540" / "tlg0540.tlg002.perseus-grc2.base.tsv", "tlg0540.tlg002.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0540" / "tlg0540.tlg003.perseus-grc2.base.tsv", "tlg0540.tlg003.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0540" / "tlg0540.tlg004.perseus-grc2.base.tsv", "tlg0540.tlg004.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0540" / "tlg0540.tlg005.perseus-grc2.base.tsv", "tlg0540.tlg005.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0540" / "tlg0540.tlg006.perseus-grc2.base.tsv", "tlg0540.tlg006.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0540" / "tlg0540.tlg007.perseus-grc2.base.tsv", "tlg0540.tlg007.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0540" / "tlg0540.tlg008.perseus-grc2.base.tsv", "tlg0540.tlg008.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0540" / "tlg0540.tlg009.perseus-grc2.base.tsv", "tlg0540.tlg009.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0540" / "tlg0540.tlg010.perseus-grc2.base.tsv", "tlg0540.tlg010.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0540" / "tlg0540.tlg012.perseus-grc2.base.tsv", "tlg0540.tlg012.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0540" / "tlg0540.tlg013.perseus-grc2.base.tsv", "tlg0540.tlg013.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0540" / "tlg0540.tlg014.perseus-grc2.base.tsv", "tlg0540.tlg014.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0540" / "tlg0540.tlg015.perseus-grc2.base.tsv", "tlg0540.tlg015.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0540" / "tlg0540.tlg016.perseus-grc2.base.tsv", "tlg0540.tlg016.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0540" / "tlg0540.tlg017.perseus-grc2.base.tsv", "tlg0540.tlg017.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0540" / "tlg0540.tlg018.perseus-grc2.base.tsv", "tlg0540.tlg018.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0540" / "tlg0540.tlg019.perseus-grc2.base.tsv", "tlg0540.tlg019.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0540" / "tlg0540.tlg020.perseus-grc2.base.tsv", "tlg0540.tlg020.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0540" / "tlg0540.tlg022.perseus-grc2.base.tsv", "tlg0540.tlg022.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0540" / "tlg0540.tlg023.perseus-grc2.base.tsv", "tlg0540.tlg023.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0540" / "tlg0540.tlg025.perseus-grc2.base.tsv", "tlg0540.tlg025.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0540" / "tlg0540.tlg026.perseus-grc2.base.tsv", "tlg0540.tlg026.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0540" / "tlg0540.tlg032.perseus-grc2.base.tsv", "tlg0540.tlg032.tokens.tsv")
    tokenize(BASE_TEXTS_DIR / "tlg0540" / "tlg0540.tlg033.perseus-grc2.base.tsv", "tlg0540.tlg033.tokens.tsv")


