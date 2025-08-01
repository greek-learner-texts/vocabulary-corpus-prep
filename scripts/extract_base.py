#!/usr/bin/env python3

from os import makedirs 
from pathlib import Path
import re

from lxml import etree # type: ignore


REPO_DIR = Path(__file__).parent.parent
GREEK_LIT = (REPO_DIR / "../../Scaife/canonical-greekLit").resolve()


def d(text_group, text_id, version="perseus-grc2"):
    return f"data/{text_group}/{text_id}/{text_group}.{text_id}.{version}.xml"

def tei(name):
    return "{http://www.tei-c.org/ns/1.0}" + name


def write_base(text_group, text_id, version="perseus-grc2", refs_filter=None):
    makedirs(f"base-texts/{text_group}", exist_ok=True)
    with open(f"base-texts/{text_group}/{text_group}.{text_id}.{version}.base.tsv", "w") as g:
        root = etree.parse(GREEK_LIT / d(text_group, text_id, version)).getroot()
        for para in root.xpath("/tei:TEI/tei:text/tei:body//tei:p", namespaces={"tei": "http://www.tei-c.org/ns/1.0"}):
            xml_str = etree.tostring(para, encoding="unicode", method="xml", exclusive=True).strip()
            xml_str = re.sub(r'\s*xmlns[^=]*="[^"]*"', '', xml_str)
            xml_str = re.sub(r'\s+', ' ', xml_str)
            xml_str = re.sub(r'<p>\s+', '<p>', xml_str)
            xml_str = re.sub(r'\s+</p>', '</p>', xml_str)
            parent = para.getparent()
            refs = []
            while parent.tag == tei("div") and parent.attrib.get("type") == "textpart":
                refs.insert(0, parent.attrib["n"])
                parent = parent.getparent()
            if refs_filter is None or (refs != [] and refs_filter(refs)):
                if refs !=[] and xml_str != "<p/>":
                    print(".".join(refs), xml_str, sep="\t", file=g)


write_base("tlg0003", "tlg001", refs_filter=lambda refs: refs[0] in ["1", "2", "3"])

for work in ["tlg007", "tlg008", "tlg009", "tlg011", "tlg019", "tlg021"]:
    write_base("tlg0010", work)

for work in ["tlg001", "tlg004", "tlg005", "tlg006", "tlg018", "tlg020", "tlg021"]:
    write_base("tlg0014", work)

write_base("tlg0032", "tlg006")

write_base("tlg0059", "tlg001", "perseus-grc1")

for work in ["tlg002", "tlg003", "tlg011", "tlg030"]:
    write_base("tlg0059", work)

for work in ["tlg001", "tlg002", "tlg003", "tlg004", "tlg005", "tlg006",
             "tlg007", "tlg008", "tlg009", "tlg010", "tlg012", "tlg013",
             "tlg014", "tlg015", "tlg016", "tlg017", "tlg018", "tlg019",
             "tlg020", "tlg022", "tlg023", "tlg025", "tlg026", "tlg032",
             "tlg033"]:
    write_base("tlg0540", work)
