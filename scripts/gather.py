#!/usr/bin/env python3

from os import makedirs 
from pathlib import Path
import re

from lxml import etree # type: ignore



REPO_DIR = Path(__file__).parent.parent
TAGGING_PIPELINE_DATA_DIR = (REPO_DIR / "../../Scaife/tagging-pipeline" / "data").resolve()
GRC_CONLLU_DIR = (REPO_DIR / "../../Scaife/giuseppe" / "downloads/opera_graeca_adnotata_v0.2.0/workspace/conllu").resolve()
GORMAN_DIR = (REPO_DIR / "../Greek-Dependency-Trees" / "xml versions").resolve()
GLAUX_DIR = (REPO_DIR / "../glaux/xml").resolve()


def get_tagging_pipeline_files(directory, work_ids):
    for d in sorted((TAGGING_PIPELINE_DATA_DIR / directory).iterdir()):
        if d.name[-3:] in work_ids:
            for path in d.glob("*-grc*.tagged.tsv"):
                yield path, d.name[-3:]


def write_tagged_file(path, work_id, group_id, group_label, ref_filter=None):
    makedirs(f"tagged-texts/{group_id}_{group_label}/{work_id}", exist_ok=True)
    with open(f"tagged-texts/{group_id}_{group_label}/{work_id}/tlg{group_id}.tlg{work_id}.tagged.tsv", "w") as g:
        for line in path.open():
            ref, word_id, word, pos1, pos2, features, lemma, _, _ = line.strip().split("\t")
            if ref_filter is None or ref_filter(ref):
                print(group_id, work_id, ref, word_id, "-", "-", word, "-", pos1, pos2, "-", features, lemma, sep="\t", file=g)


def get_oga_files(group_id, work_ids):
    for work_id in work_ids:
        file_glob = f"{group_id}.tlg{work_id}.*-grc*.tok01_sentence-seg01_annotated_lemma.conllu"
        for path in (GRC_CONLLU_DIR).glob(file_glob):
            yield path, work_id

def write_oga_file(path, work_id, group_id, group_label):
    makedirs(f"tagged-texts/{group_id}_{group_label}/{work_id}", exist_ok=True)
    with open(f"tagged-texts/{group_id}_{group_label}/{work_id}/tlg{group_id}.tlg{work_id}.oga.tsv", "w") as g:
        for line in path.open():
            if line.strip():
                word_id, word, lemma, pos, tag, features, head, deprel, _, token_id = line.strip().split("\t")
                if re.match(r"\[\d\]", word):
                    continue
                print(group_id, work_id, "-", "-", word_id, token_id, word, pos, "-", "-", tag, features, lemma, sep="\t", file=g)


def write_gorman_file(paths, work_id, group_id, group_label):
    makedirs(f"tagged-texts/{group_id}_{group_label}/{work_id}", exist_ok=True)
    with open(f"tagged-texts/{group_id}_{group_label}/{work_id}/tlg{group_id}.tlg{work_id}.gorman.tsv", "w") as g:
        for path in paths:
            root = etree.parse(path).getroot()
            assert root.tag == "treebank", root.tag
            for child in root:
                assert child.tag in ["date", "annotator", "sentence"], child.tag
                if child.tag == "sentence":
                    sentence_id = child.attrib.get("id")
                    subdoc = child.attrib.get("subdoc")
                    for gchild in child:
                        assert gchild.tag in ["word"], gchild.tag
                        word_id = gchild.attrib.get("id")
                        form = gchild.attrib.get("form")
                        lemma = gchild.attrib.get("lemma")
                        postag = gchild.attrib.get("postag")
                        relation = gchild.attrib.get("relation")
                        head = gchild.attrib.get("head")
                        if re.match(r"\[\d\]", form):
                            continue
                        if gchild.attrib.get("artificial"):
                            continue
                        print(group_id, work_id, subdoc, "-", word_id, "-", form, "-", "-", "-", postag, "-", lemma, sep="\t", file=g)


def write_glaux_file(path, work_id, group_id, group_label, ref_filter=None):
    makedirs(f"tagged-texts/{group_id}_{group_label}/{work_id}", exist_ok=True)
    with open(f"tagged-texts/{group_id}_{group_label}/{work_id}/tlg{group_id}.tlg{work_id}.glaux.tsv", "w") as g:
        root = etree.parse(path).getroot()
        assert root.tag == "treebank", root.tag
        for child in root:
            assert child.tag in ["sentence"], child.tag
            struct_id = child.attrib.get("struct_id")
            document_id = child.attrib.get("document_id")
            assert document_id == f"{group_id}-{work_id}", (document_id, group_id, work_id)
            for gchild in child:
                assert gchild.tag in ["word"], gchild.tag
                word_id = gchild.attrib.get("id")
                form = gchild.attrib.get("form")
                ref = gchild.attrib.get("div_section")
                lemma = gchild.attrib.get("lemma")
                postag = gchild.attrib.get("postag")
                head = gchild.attrib.get("head")
                relation = gchild.attrib.get("relation")
                # if re.match(r"\[\d\]", form):
                #     continue
                if ref_filter is None or ref_filter(ref):
                    print(group_id, work_id, ref, "-", word_id, "-", form, "-", "-", "-", postag, "-", lemma, sep="\t", file=g)


def process(shard, group_id, group_label, work_ids, ref_filter=None):
    for path, work_id in get_tagging_pipeline_files(f"tagging-shard-{shard}/tlg{group_id}", work_ids):
        write_tagged_file(path, work_id, group_id, group_label, ref_filter)

    for path, work_id in get_oga_files(f"tlg{group_id}", work_ids):
        write_oga_file(path, work_id, group_id, group_label)

    for work_id in work_ids:
        write_glaux_file(GLAUX_DIR / f"{group_id}-{work_id}.xml", work_id, group_id, group_label, ref_filter)


process("07", "0059", "plato", [
        "001", "002", "003", "011", "030"
    ])

work_ids = {"plato apology.xml": "002", "Plato_Crito_Travis_Kahl.xml": "003"}
for filename in work_ids.keys():
    write_gorman_file([GORMAN_DIR / filename], work_ids[filename], "0059", "plato")


process("12", "0540", "lysias", [
        "001", "002", "003", "004", "005", "006", "007", "008", "009", "010",
        "012", "013", "014", "015", "016", "017", "018", "019", "020", "022",
        "023", "025", "026", "032", "033",
    ])

work_ids = {"Lysias 1 bu1.xml": "001", "Lysias 12 bu1.xml": "012", "lysias 13 bu1.xml": "013",
    "Lysias 14 bu1.xml": "014", "lysias 15.xml": "015", "lysias 19 bu1.xml": "019",
    "Lysias 23 bu1.xml": "023"}
for filename in work_ids.keys():
    write_gorman_file([GORMAN_DIR / filename], work_ids[filename], "0540", "lysias")


process("10", "0014", "demosthenes", [
        "001", "004", "005", "006", "018", "020", "021"
    ])

write_gorman_file([GORMAN_DIR / "Demosthenes 1 bu1.xml"], "001", "0014", "demosthenes")
write_gorman_file([
    GORMAN_DIR / "demosthenes 18 1-50 bu2.xml",
    GORMAN_DIR / "demosthenes 18 101-150 bu2.xml",
    GORMAN_DIR / "demosthenes 18 151-200 bu2.xml",
    GORMAN_DIR / "demosthenes 18 201-275 bu1.xml",
    GORMAN_DIR / "demosthenes 18 276-324 bu1.xml",
    GORMAN_DIR / "demosthenes 18 51-100 bu1.xml",
], "018", "0014", "demosthenes")


process("10", "0010", "isocrates", [
        "007", "008", "009", "011", "019", "021"
    ])

# no Gorman overlap

process("10", "0032", "xenophon", [
        "006"
    ])

write_gorman_file([
    GORMAN_DIR / "Xen_Anab_book_1.1-5.xml",
    GORMAN_DIR / "Xen_Anab_book_1.6-9.xml",
    GORMAN_DIR / "Xen_Anab_book_3.xml",
], "006", "0032", "xenophon")


process("06", "0003", "thucydides", [
        "001"
    ], lambda ref: ref[0] in ["1", "2", "3"])

write_gorman_file([
    GORMAN_DIR / "thuc 1 1-20 bu5.xml",
    GORMAN_DIR / "thuc 1 21-40 bu4.xml",
    GORMAN_DIR / "thuc 1 41-60 bu3.xml",
    GORMAN_DIR / "thuc 1 61-80 bu3.xml",
    GORMAN_DIR / "thuc 3.1-20 bu1.xml",
], "001", "0003", "thucydides")
