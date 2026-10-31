"""Shared paths and helpers for the language-origins project.

Raw inputs (read in place, never modified), all retrieved in 2026:
- GLOTTO: Glottolog 5.2.1 as CLDF (Hammarstrom, Forkel, Haspelmath and Bank 2025), CC BY 4.0:
  languages.csv (every languoid with glottocode, name, coordinates, macroarea, countries, family, level),
  values.csv (level, category, classification path, endangerment status 'aes', most extensive description 'med'),
  codes.csv (the code tables), cldf-metadata.json (version and citation).
- WD: Wikidata (CC0), a TSV query result of items with a Glottolog code (P1394): item, English label, glottocode, ISO 639-3
  code, number of speakers (P1098) and its point in time, UNESCO endangerment status (P1999) and Ethnologue status (P3823).
- GEO: Natural Earth countries (1:50m, 1:10m), land (1:50m) and populated places (1:10m), public domain.
- The proposed homelands (data/homelands_literature.csv) are typed in from the published literature cited in that file
  (code/03_origins.py), not taken from a database.
"""
import json, gzip, os, re, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLOTTO = "/home/claude/newdata/raw2/glottolog-cldf/cldf"
WD = "/home/claude/newdata/raw2/langs.tsv"
GEO = "/home/claude/newdata/raw/geo"
DATA = os.path.join(ROOT, "data")
SHM = os.environ.get("LANGTMP", "/dev/shm/langorig")
WORK = os.path.join(SHM, "work")       # intermediates live in memory, not in the repo
for d in (DATA, WORK):
    os.makedirs(d, exist_ok=True)

DOI = os.environ.get("STUDY_DOI", "{{DOI}}")          # set STUDY_DOI when the Zenodo DOI is known, then rerun 05, 07 and 09
BLOG_ENV = os.environ.get("STUDY_BLOG_URL")
SLUG = "language-origins"
PAGE = "https://maps.tristanhotham.com/language-origins/"
REPO = "https://github.com/Tristan-Hotham/language-origins"
BLOG = BLOG_ENV or "https://blog.tristanhotham.com/2026/10/31/language-origins/"
RETRIEVED = "2026"
GLOTTOLOG_VERSION = "5.2.1"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")

AES = {1: "not endangered", 2: "threatened", 3: "shifting", 4: "moribund", 5: "nearly extinct", 6: "extinct"}
AES_COL = {1: "#3E8E6E", 2: "#C9B23C", 3: "#E58A2E", 4: "#D0532F", 5: "#A3243B", 6: "#3A2E3F", 0: "#B9B2A6"}


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def nodash(v):
    if isinstance(v, str):
        v = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", v)
        v = v.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", "-")
        while "--" in v:
            v = v.replace("--", "-")
        return v
    if isinstance(v, list):
        return [nodash(x) for x in v]
    if isinstance(v, dict):
        return {k: nodash(x) for k, x in v.items()}
    return v


def jsave(obj, path, indent=None):
    if os.path.abspath(path).startswith(DATA):
        obj = nodash(obj)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))


def norm(s):
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    return re.sub(r"[\W_]+", " ", s).strip()


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f, tex=False):
    if f is None or f == "raw":
        s = str(v)
    elif f == "int":
        s = f"{round(float(v)):,}"
    elif f == "pc":
        s = f"{round(float(v))}%"
    elif f == "f1":
        s = f"{float(v):.1f}"
    elif f == "pc1":
        s = f"{float(v):.1f}%"
    elif f == "m":       # millions, no decimals
        s = f"{float(v) / 1e6:,.0f}"
    elif f == "bn":
        s = f"{float(v) / 1e9:.1f}"
    else:
        raise ValueError(f)
    if tex:
        s = s.replace("%", "\\%").replace("&", "\\&").replace("_", "\\_").replace("#", "\\#")
    return s


TOKEN = re.compile(r"\{\{(?!IMG|DOI|BLOG_URL|TABLE_|BIBLIOGRAPHY)([^}|]+)(\|(\w+))?\}\}")


def fill(text, R, tex=False):
    return TOKEN.sub(lambda m: fmt(get(R, m.group(1)), m.group(3), tex), text)


def great_circle_km(lat1, lon1, lat2, lon2):
    import math
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians(lon2 - lon1)
    a = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * 6371.0 * math.asin(min(1, math.sqrt(a)))


def placeholders(text):
    """Fill {{DOI}} and https://blog.tristanhotham.com/2026/10/31/language-origins/ when they are known (environment), otherwise leave them for the publisher."""
    if DOI != "{{DOI}}":
        text = text.replace("{{DOI}}", DOI)
    if BLOG_ENV:
        text = text.replace("https://blog.tristanhotham.com/2026/10/31/language-origins/", BLOG_ENV)
    return text
