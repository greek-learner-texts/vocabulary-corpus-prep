#!/usr/bin/env python3

from os import makedirs 
from itertools import zip_longest
import unicodedata


makedirs("aligned-tagging", exist_ok=True)

a = open("tokenized-texts/tlg0003.tlg001.tokens.tsv").readlines()
b = open("tagged-texts/0003_thucydides/001/tlg0003.tlg001.oga.tsv").readlines()
b2 = open("tagged-texts/0003_thucydides/001/tlg0003.tlg001.gorman.tsv").readlines()

with open("aligned-tagging/tlg0003.tlg001.aligned.tsv", "w") as g:
    print("ref", "idx", "token", "oga_id", "oga_postag", "gorman_postag", "oga_lemma", "gorman_lemma", "mismatch", sep="\t", file=g)

    for c, d, d2 in zip(a, b, b2):
        try:
            e = unicodedata.normalize("NFC", c.strip().split("\t")[2])
        except IndexError:
            print(c.strip().split("\t")[0])
            print(d.strip().split("\t")[5])
            print(d2.strip().split("\t")[5])
            quit()
        e = e.replace("\u1FBD", "\u2019")
        f = unicodedata.normalize("NFC", d.strip().split("\t")[6])
        f = f.replace("\u02BC", "\u2019")
        if e != f:
            print(d.strip().split("\t")[5])
            print(e, f, sep="\t")
            for g, h in zip_longest(e, f):
                print(hex(ord(g)), unicodedata.name(g), unicodedata.name(h) if h else "", sep="\t")
            break
        if d2.strip() == "":
            continue
        f2 = unicodedata.normalize("NFC", d2.strip().split("\t")[6])
        f2 = f2.replace("\u1FBD", "\u2019")
        f2 = f2.replace("\u02BC", "\u2019")
        f2 = f2.replace(":", "\u00B7")
        if f2 in ["-τε", "-δ’", "-δὲ", "-θ’", "-τ’", "-δέ"]:
            f2 = f2[1:]
        if f2 in ["τ-", "κ-"]:
            f2 = f2[:-1]
        if e != f2:
            print(c.strip().split("\t")[0], d2.strip().split("\t")[2])
            print(c.strip().split("\t")[1], d2.strip().split("\t")[4])
            print(e, f2, sep="\t")
            for g, h2 in zip_longest(e, f2):
                print(hex(ord(g)), unicodedata.name(g), unicodedata.name(h2) if h2 else "", sep="\t")
            break

        j = d.strip().split("\t")
        j2 = d2.strip().split("\t") + [""]
        match = j[10] != j2[10] or (j[12] != j2[12] and j2[12] != "punc1")
        print(c.strip(), j[5], j[10], j2[10], j[12], j2[12], "@" if match else "", sep="\t", file=g)