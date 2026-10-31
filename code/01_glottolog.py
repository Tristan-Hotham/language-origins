"""Read Glottolog (CLDF) and Wikidata speaker counts into one table of languages and one table of family-tree nodes.

Writes
- work/langs.json: every language-level languoid except Glottolog's 'Bookkeeping' entries (spurious or duplicate names kept
  for reference): glottocode, name, coordinates, macroarea, countries, category, classification path, endangerment (AES),
  most extensive description (MED), number of dialects, and the Wikidata speaker count chosen by the rule below.
- work/nodes.json: every family-level node (top-level families, subgroups) and pseudo family, with parent and name.
- work/dialects.json: dialect names under each language (for the family-tree browser).
- data/languages.csv: the language table for reuse.

Speaker counts (Wikidata P1098). An item can carry several counts, from different years and sources and often a first-
language, second-language and total figure side by side (the qualifiers that say which were not in the download). Rule:
take the count with the most recent point in time; where several counts share that date, take the smallest (most often the
first-language figure); where no count is dated, take the largest. A date before 1800 is treated as an error and
the count as undated (one case). Only Wikidata items whose Glottolog code is a
language-level languoid are used; where several items share a glottocode the same rule is applied across all their counts.
Zero counts are dropped (Wikidata records some extinct languages as 0 speakers).
"""
import csv
from collections import defaultdict, Counter
from common import *

csv.field_size_limit(10 ** 9)
LANG = list(csv.DictReader(open(f"{GLOTTO}/languages.csv", encoding="utf-8")))
VAL = defaultdict(dict)
for r in csv.DictReader(open(f"{GLOTTO}/values.csv", encoding="utf-8")):
    if r["Parameter_ID"] in ("category", "classification", "aes", "med"):
        VAL[r["Language_ID"]][r["Parameter_ID"]] = r["Value"]
meta = jload(f"{GLOTTO}/cldf-metadata.json")
assert GLOTTOLOG_VERSION in meta["dc:bibliographicCitation"], meta["dc:bibliographicCitation"]

BYID = {r["ID"]: r for r in LANG}
cat = lambda i: VAL[i].get("category", "")
path = lambda i: [x for x in VAL[i].get("classification", "").split("/") if x]

# ---- nodes of the family trees (family level), including pseudo families
nodes = {}
for r in LANG:
    if r["Level"] != "family":
        continue
    p = path(r["ID"])
    nodes[r["ID"]] = {"id": r["ID"], "name": r["Name"], "parent": p[-1] if p else None, "top": p[0] if p else r["ID"],
                      "pseudo": cat(r["ID"]) == "Pseudo_Family", "depth": len(p),
                      "lat": float(r["Latitude"]) if r["Latitude"] else None, "lon": float(r["Longitude"]) if r["Longitude"] else None}

# ---- dialects, grouped under their language
dial = defaultdict(list)
for r in LANG:
    if r["Level"] == "dialect" and r["Language_ID"]:
        dial[r["Language_ID"]].append(r["Name"])

# ---- Wikidata speaker counts
lang_ids = {r["ID"] for r in LANG if r["Level"] == "language"}
counts = defaultdict(list)
wd_label, wd_q = {}, {}
n_wd_rows = 0
with open(WD, encoding="utf-8") as f:
    head = [h.lstrip("?") for h in f.readline().rstrip("\n").split("\t")]
    for ln in f:
        n_wd_rows += 1
        v = dict(zip(head, ln.rstrip("\n").split("\t")))
        g = v["g"].strip('"')
        if g not in lang_ids:
            continue
        q = v["lang"].rsplit("/", 1)[-1].rstrip(">")
        lab = re.sub(r'^"(.*)"@en$', r"\1", v["l"])
        wd_label.setdefault(g, lab); wd_q.setdefault(g, set()).add(q)
        if re.match(r"^[\d.eE+]+$", v["n"]):   # skip blank and 'unknown value' counts
            n = float(v["n"])
            when = v["when"][:4] if re.match(r"^\d{4}-", v["when"]) else None
            if when and int(when) < 1800:   # an implausible point in time (a data-entry error) is treated as undated
                when = None
            if n > 0:
                counts[g].append((when, n, q))


def pick(cs):
    dated = [c for c in cs if c[0]]
    if dated:
        y = max(c[0] for c in dated)
        return min((c for c in dated if c[0] == y), key=lambda c: c[1])
    return max(cs, key=lambda c: c[1])


langs = []
for r in LANG:
    if r["Level"] != "language" or cat(r["ID"]) == "Bookkeeping":
        continue
    i = r["ID"]
    p = path(i)
    c = cat(i)
    top = p[0] if p else None
    if top is None:
        assert r["Is_Isolate"] == "true" and c == "Spoken_L1_Language", (i, c)
    sp = pick(counts[i]) if counts.get(i) else None
    langs.append({
        "id": i, "name": r["Name"], "lat": float(r["Latitude"]) if r["Latitude"] else None,
        "lon": float(r["Longitude"]) if r["Longitude"] else None, "iso": r["ISO639P3code"], "macro": r["Macroarea"],
        "countries": [x for x in r["Countries"].split(";") if x], "cat": c, "path": p, "top": top,
        "isolate": r["Is_Isolate"] == "true", "aes": int(VAL[i]["aes"]) if VAL[i].get("aes") else None,
        "med": int(VAL[i]["med"]) if VAL[i].get("med") else None, "ndial": len(dial.get(i, [])),
        "speakers": sp[1] if sp else None, "sp_year": sp[0] if sp else None, "sp_n_counts": len(counts.get(i, [])),
        "wd_label": wd_label.get(i), "wd_q": sorted(wd_q.get(i, []))})

# every path step is a known node
for l in langs:
    for x in l["path"]:
        assert x in nodes, (l["id"], x)
# Dialects carry the name of their language's closest language-level ancestor in Language_ID
print(len(langs), "languages (no Bookkeeping);", Counter(l["cat"] for l in langs).most_common())
print(len(nodes), "family-level nodes;", sum(1 for n in nodes.values() if n["parent"] is None and not n["pseudo"]), "top-level families")
print("with speaker count:", sum(1 for l in langs if l["speakers"]), "; Wikidata rows", n_wd_rows)

jsave(langs, f"{WORK}/langs.json")
jsave(nodes, f"{WORK}/nodes.json")
jsave({k: sorted(v) for k, v in dial.items()}, f"{WORK}/dialects.json")
jsave({"wd_rows": n_wd_rows, "wd_items_matched": len({q for s in wd_q.values() for q in s}),
       "glottolog_citation": meta["dc:bibliographicCitation"]}, f"{WORK}/meta.json")

# ---- reusable CSV
AESN = AES
with open(f"{DATA}/languages.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["glottocode", "name", "iso639_3", "latitude", "longitude", "macroarea", "countries", "category",
                "family_glottocode", "family", "isolate", "classification_glottocodes", "classification_names",
                "endangerment_aes", "endangerment_label", "most_extensive_description", "n_dialects",
                "speakers_wikidata", "speakers_year", "wikidata_items"])
    for l in langs:
        w.writerow([l["id"], l["name"], l["iso"], l["lat"] if l["lat"] is not None else "", l["lon"] if l["lon"] is not None else "",
                    l["macro"], ";".join(l["countries"]), l["cat"], l["top"] or "", nodes[l["top"]]["name"] if l["top"] else "",
                    int(l["isolate"]), "/".join(l["path"]), " / ".join(nodes[x]["name"] for x in l["path"]),
                    l["aes"] or "", AESN.get(l["aes"], ""), l["med"] if l["med"] is not None else "", l["ndial"],
                    int(l["speakers"]) if l["speakers"] else "", l["sp_year"] or "", ";".join(l["wd_q"])])
