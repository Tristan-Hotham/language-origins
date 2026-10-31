"""Blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
Zenodo copies of files that also live elsewhere in the repo are hard links, so they take no extra disk.
{{DOI}}, {{DOI_URL}} and https://blog.tristanhotham.com/2026/10/31/language-origins/ are left for the publisher unless STUDY_DOI / STUDY_BLOG_URL are set."""
import re, zipfile, json as _json
import checks  # noqa: F401
from common import *

R = jload(f"{DATA}/results.json")
REL = os.path.join(ROOT, "release")
NAME = "Hotham_Where_Languages_Come_From"

# facts written as numbers in alt text, checked here
mb = R["macro_by"]; sp = R["speakers"]
assert round(mb["Africa"]["safe_pct"]) == 59 and round(mb["North America"]["extinct_pct"]) == 28
assert round(mb["South America"]["extinct_pct"]) == 35 and round(mb["Australia"]["extinct_pct"]) == 64
assert all(28 <= mb[k]["safe_pct"] <= 38 for k in ("Papunesia", "Eurasia"))
assert [round(t["n"] / 1e6) for t in sp["top"][:4]] == [918, 485, 379, 341] and [t["name"] for t in sp["top"][:4]] == ["Mandarin Chinese", "Spanish", "English", "Hindi"]
assert (sp["top10_share"], sp["top20_share"], sp["top100_share"]) == (50.9, 62.6, 89.8)
assert max(R["grid"]["top_n"][0]["n"], 0) > 100
TREE = {n[1]: n[3] for n in jload(f"{DATA}/tree.json")["N"] if n[1] in ("Germanic", "Italic", "Balto-Slavic", "Celtic", "Graeco-Phrygian", "Albanian")}
assert R["ie_ii"] > sum(TREE.values()), TREE

post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = placeholders(fill(post, R))
if DOI != "{{DOI}}":
    post = post.replace("{{DOI_URL}}", f"https://doi.org/{DOI}")
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
for img in used:
    assert os.path.exists(f"{REL}/blog/{img}"), img
assert 5 <= len(used) <= 8
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS"):
    assert bad not in vis, bad
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
c, a = R["counts"], R["aes"]
meta = {"title": "Where languages come from: every language on one map, with its family tree, its future and its homeland",
        "slug": "language-origins",
        "excerpt": f"{c['spoken']:,} spoken languages, {c['lineages']} separate lineages, {a['endangered_pct']}% endangered. I mapped every language in Glottolog with its family tree, endangerment, speaker numbers and the proposed homelands of the great language families.",
        "seo_description": "An interactive map of every language in Glottolog: language families and isolates, endangerment, speakers and proposed family homelands.",
        "tags": ["languages", "linguistics", "language families", "endangered languages", "Glottolog", "Indo-European", "maps", "data visualisation"],
        "header_alt": f"Title card reading 'Where languages come from' in black and deep teal on cream, beside a world map with a coloured dot for every language: orange across Africa, teal across the Pacific islands, blue from Europe to India, red in China and coral in Australia. Text: every one of the world's {c['spoken']:,} spoken languages, coloured by family: {c['families']} families and {c['isolates']} isolates."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

# ---------------------------------------------------------------- Zenodo
Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)


def link(src, dst):
    if os.path.exists(dst):
        os.remove(dst)
    os.link(src, dst)


link(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/language-origins_data_and_code.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for d in ("code", "data"):
        for fn in sorted(os.listdir(os.path.join(ROOT, d))):
            if fn.endswith(".pyc") or fn == "__pycache__":
                continue
            z.write(os.path.join(ROOT, d, fn), f"language-origins/{d}/{fn}")
    for fn in ("README.md", "LICENSE"):
        z.write(os.path.join(ROOT, fn), f"language-origins/{fn}")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\emph{", "").replace("}", "").replace("\\&", "&")
zmeta = {"title": "Where Languages Come From: The World's Language Families, Their Proposed Homelands and Where They Are Spoken Today, Mapped from Glottolog",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive version: https://maps.tristanhotham.com/language-origins/. Data and code: https://github.com/Tristan-Hotham/language-origins. Includes data from Glottolog {GLOTTOLOG_VERSION} (Hammarström, Forkel, Haspelmath and Bank, CC BY 4.0) and Wikidata (CC0).</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["languages", "language families", "Glottolog", "language endangerment", "linguistic diversity", "homelands", "Indo-European", "Austronesian", "Bantu", "maps"],
         "license": "cc-by-4.0",
         "related_identifiers": [
             {"identifier": "https://github.com/Tristan-Hotham/language-origins", "relation": "isSupplementedBy", "resource_type": "software"},
             {"identifier": "https://maps.tristanhotham.com/language-origins/", "relation": "isSupplementedBy", "resource_type": "other"},
             {"identifier": "https://glottolog.org", "relation": "isDerivedFrom", "resource_type": "dataset"},
             {"identifier": "https://www.wikidata.org/", "relation": "isDerivedFrom", "resource_type": "dataset"},
             {"identifier": "https://www.naturalearthdata.com/", "relation": "isDerivedFrom", "resource_type": "dataset"}]}
jsave(zmeta, f"{Z}/metadata.json", indent=2)
s = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in s and "\u2013" not in s and "--" not in s
print("blog words", words, "; zenodo files", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
