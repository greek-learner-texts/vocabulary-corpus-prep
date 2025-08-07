#!/usr/bin/env python3

from os import makedirs 
from itertools import zip_longest
import unicodedata


def fold(w):
    return unicodedata.normalize("NFC",
        "".join(ch for ch in unicodedata.normalize("NFD", w.lower())
        if unicodedata.category(ch)[0] != "M")
    )

def norm(s):
    s = unicodedata.normalize("NFC", s)
    s = s.replace("\u1FBD", "\u2019")
    s = s.replace("\u02BC", "\u2019")
    s = s.replace(":", "\u00B7")
    return s


def split(s):
    return s.strip().split("\t")


def debug_pair(a, b):
    print(a, b, sep="\t")
    for c, d in zip_longest(a, b):
        print(hex(ord(c)), unicodedata.name(c), unicodedata.name(d) if d else "", sep="\t")


def empty(x):
    return x is None or x.strip() == ""


if __name__ == "__main__":

    makedirs("aligned-tagging", exist_ok=True)

    base = open("tokenized-texts/tlg0003.tlg001.tokens.tsv").readlines()
    oga = open("tagged-texts/0003_thucydides/001/tlg0003.tlg001.oga.tsv").readlines()
    glaux = open("tagged-texts/0003_thucydides/001/tlg0003.tlg001.glaux.tsv").readlines()
    gorman = open("tagged-texts/0003_thucydides/001/tlg0003.tlg001.gorman.tsv").readlines()

    with open("aligned-tagging/tlg0003.tlg001.aligned.tsv", "w") as g:
        print("ref", "idx", "token", "oga_id", "glaux_id", "oga_postag", "glaux_postag", "gorman_postag", "oga_lemma", "glaux_lemma", "gorman_lemma", "mismatch", sep="\t", file=g)

        for token_base, token_oga, token_glaux, token_gorman in zip_longest(base, oga, glaux, gorman):
            if empty(token_base) or empty(token_oga):
                continue
            # try:
            #     e = norm(split(token_base)[2])
            # except IndexError:
            #     print(split(token_base)[0])
            #     print(split(token_oga)[5])
            #     print(split(token_gorman)[5])
            #     quit()
            form_base = norm(split(token_base)[2])

            split_oga = split(token_oga)
            form_oga = norm(split_oga[6])
            id_oga = split_oga[5]
            postag_oga = split_oga[10]
            lemma_oga = split_oga[12]

            if form_base != form_oga:
                print(id_oga)
                debug_pair(form_base, form_oga)
                break

            split_glaux = split(token_glaux)
            form_glaux = norm(split_glaux[6])
            id_glaux = split_glaux[4]
            postag_glaux = split_glaux[10]
            lemma_glaux = split_glaux[12]

            if form_base != form_glaux:
                print(id_glaux)
                debug_pair(form_base, form_glaux)
                break

            if not empty(token_gorman):

                split_gorman = split(token_gorman) + [""]
                form_gorman = norm(split_gorman[6])
                postag_gorman = split_gorman[10]
                lemma_gorman = split_gorman[12]

                if form_gorman in ["-τε", "-δ’", "-δὲ", "-θ’", "-τ’", "-δέ"]:
                    form_gorman = form_gorman[1:]
                if form_gorman in ["τ-", "κ-"]:
                    form_gorman = form_gorman[:-1]

                if form_base != form_gorman:
                    print(split(token_base)[0], split(token_gorman)[2])
                    print(split(token_base)[1], split(token_gorman)[4])
                    debug_pair(form_base, form_gorman)
                    break

                match = ""

                if lemma_gorman != "punc1":
                    if postag_oga != postag_gorman or lemma_oga != lemma_gorman:
                        match = "."
                    if fold(lemma_oga) != fold(lemma_gorman):
                        match = "@"
            else:
                postag_gorman = ""
                lemma_gorman = ""
                match = ""

            print(
                token_base.strip(), id_oga,
                postag_oga, postag_gorman,
                lemma_oga, lemma_gorman,
                match, sep="\t", file=g
            )