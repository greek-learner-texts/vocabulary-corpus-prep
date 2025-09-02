#!/usr/bin/env python3

from os import makedirs 
from itertools import zip_longest
import unicodedata


def fold(w):
    if w != "" and w[-1].isdigit():
        w = w[:-1]
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
    for c, d in zip(a, b):
        print(hex(ord(c)), unicodedata.name(c), unicodedata.name(d) if d else "", sep="\t")


def empty(x):
    return x is None or x.strip() == ""


def align_tagging(base_path, oga_path, glaux_path, gorman_path, output_filename):

    makedirs("aligned-tagging", exist_ok=True)

    base = open(base_path).readlines()
    oga = open(oga_path).readlines()
    glaux = open(glaux_path).readlines()

    if gorman_path is None:
        gorman = []
    else:
        gorman = open(gorman_path).readlines()

    with open(f"aligned-tagging/{output_filename}", "w") as g:
        print(
            "ref", "idx", "token",
            "oga_id", "glaux_id",
            "oga_postag", "glaux_postag", "gorman_postag",
            "oga_lemma", "glaux_lemma", "gorman_lemma",
            "mismatch_oga_gorman|mismatch_glaux_gorman|mismatch_oga_glaux",
            sep="\t", file=g
        )

        glaux_crasis = None

        for token_base, token_oga, token_glaux, token_gorman in zip_longest(base, oga, glaux, gorman):
            if empty(token_base):
                continue

            form_base = norm(split(token_base)[2])

            if not empty(token_oga):
                split_oga = split(token_oga)
                form_oga = norm(split_oga[6])
                id_oga = split_oga[5]
                postag_oga = split_oga[10]
                lemma_oga = split_oga[12]

                if form_base != form_oga:
                    print("[OGA]")
                    print(split(token_base)[0], split(token_base)[1], id_oga)
                    debug_pair(form_base, form_oga)
                    break

            if not empty(token_glaux):
                split_glaux = split(token_glaux)
                form_glaux = norm(split_glaux[6])
                id_glaux = split_glaux[4]
                postag_glaux = split_glaux[10]
                lemma_glaux = split_glaux[12]

                if glaux_crasis:
                    assert form_glaux.startswith(glaux_crasis), (form_glaux, glaux_crasis)
                    form_glaux = form_glaux[len(glaux_crasis):]
                    glaux_crasis = None

                if form_glaux in ["-τε", "-δ’", "-δὲ", "-θ’", "-τ’", "-δέ"]:
                    form_glaux = form_glaux[1:]
                if form_glaux in ["το-", "τα-", "κα-"]:
                    form_glaux = form_glaux[0]
                    glaux_crasis = form_glaux

                if form_base != form_glaux:
                    if form_base == "·" and form_glaux == ",":
                        pass
                    else:
                        print("[GLAUX]")
                        print(split(token_base)[0], split(token_base)[1], id_glaux)
                        debug_pair(form_base, form_glaux)
                        break
            
                match_oga_glaux = ""

                if postag_oga != postag_glaux or lemma_oga != lemma_glaux:
                    pass  # match_oga_glaux = "."
                if fold(lemma_oga) != fold(lemma_glaux):
                    match_oga_glaux = "@"

            else:
                postag_glaux = ""
                lemma_glaux = ""
                id_glaux = ""
                match_oga_glaux = "m"

            if not empty(token_gorman):

                split_gorman = split(token_gorman) + [""]
                form_gorman = norm(split_gorman[6])
                postag_gorman = split_gorman[10]
                lemma_gorman = split_gorman[12]
                if lemma_gorman == "punc1":
                    lemma_gorman = form_gorman

                if form_gorman in ["-τε", "-δ’", "-δὲ", "-θ’", "-τ’", "-δέ"]:
                    form_gorman = form_gorman[1:]
                if form_gorman in ["τ-", "κ-"]:
                    form_gorman = form_gorman[:-1]

                if form_base != form_gorman:
                    print("[GORMAN]")
                    print(split(token_base)[0], split(token_gorman)[2])
                    print(split(token_base)[1], split(token_gorman)[4])
                    debug_pair(form_base, form_gorman)
                    break

                match_oga_gorman = ""

                if postag_oga != postag_gorman or lemma_oga != lemma_gorman:
                    pass  # match_oga_gorman = "."
                if fold(lemma_oga) != fold(lemma_gorman):
                    match_oga_gorman = "@"

                match_glaux_gorman = ""

                if not empty(token_glaux):
                    if postag_glaux != postag_gorman or lemma_glaux != lemma_gorman:
                        pass  # match_glaux_gorman = "."
                    if fold(lemma_glaux) != fold(lemma_gorman):
                        match_glaux_gorman = "@"
                else:
                    match_glaux_gorman = "m"

            else:
                postag_gorman = ""
                lemma_gorman = ""
                match_oga_gorman = "m"
                match_glaux_gorman = "m"

            print(
                token_base.strip(), id_oga, id_glaux,
                postag_oga, postag_glaux, postag_gorman,
                lemma_oga, lemma_glaux, lemma_gorman,
                match_oga_gorman + "|" + match_glaux_gorman + "|" + match_oga_glaux,
                sep="\t", file=g
            )


def align(group_label, group_id, work_id, no_gorman=False):
    align_tagging(
        f"tokenized-texts/tlg{group_id}.tlg{work_id}.tokens.tsv",
        f"tagged-texts/{group_id}_{group_label}/{work_id}/tlg{group_id}.tlg{work_id}.oga.tsv",
        f"tagged-texts/{group_id}_{group_label}/{work_id}/tlg{group_id}.tlg{work_id}.glaux.tsv",
        None if no_gorman else f"tagged-texts/{group_id}_{group_label}/{work_id}/tlg{group_id}.tlg{work_id}.gorman.tsv",
        f"tlg{group_id}.tlg{work_id}.aligned.tsv"
    )


if __name__ == "__main__":

    align("thucydides", "0003", "001")
    align("xenophon", "0032", "006")

    for work in ["007", "008", "009", "011", "019", "021"]:
        align("isocrates", "0010", work, no_gorman=True)

    for work in ["001", "018"]:
        align("demosthenes", "0014", work)

    for work in ["004", "005", "006", "020", "021"]:
        align("demosthenes", "0014", work, no_gorman=True)

    for work in ["002", "003"]:
        align("plato", "0059", work)

    for work in ["001", "011", "030"]:
        align("plato", "0059", work, no_gorman=True)

    for work in ["001", "012", "013", "014", "015", "019", "023"]:
        align("lysias", "0540", work)

    for work in ["002", "003", "004", "005", "006", "007", "008", "009",
      "010", "016", "019", "023", 
    ]:
        align("lysias", "0540", work, no_gorman=True)
