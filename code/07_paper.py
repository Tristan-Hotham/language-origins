"""Build the paper: fill code/paper_template.tex from data/results.json, add tables and references, compile with xelatex.
Output: release/paper/Hotham_Where_Languages_Come_From.tex and .pdf (figures f_*.png alongside)."""
import re, subprocess
import checks  # noqa: F401
from common import *

R = jload(f"{DATA}/results.json")
HL = jload(f"{WORK}/homelands.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Where_Languages_Come_From"
tex = lambda s: str(s).replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#")
c, s = R["counts"], R["speakers"]

TS = ("\\begin{table}[tbp]\\centering\\small\\caption{Sources, what was used and licences.}\\label{tab:sources}"
      "\\begin{tabular}{>{\\raggedright\\arraybackslash}p{3.2cm}>{\\raggedright\\arraybackslash}p{7.4cm}>{\\raggedright\\arraybackslash}p{2.6cm}}\\toprule Source & Used & Licence\\\\\\midrule\n"
      f"Glottolog {R['meta']['glottolog']} (CLDF) & {c['mapped']:,} languages mapped ({c['spoken']:,} spoken first languages), {c['nodes']:,} family and subgroup nodes, {c['dialects']:,} dialects; endangerment and description status & CC BY 4.0\\\\\n"
      f"Wikidata & Speaker counts for {s['n']:,} spoken languages; English labels & CC0\\\\\n"
      "Natural Earth & Country outlines and areas, land, admin-1 regions, place names & Public domain\\\\\n"
      f"Published studies & {R['origins']['n_hyp']} homeland hypotheses for {R['origins']['n_fam']} families (Table~\\ref{{tab:homelands}}) & Cited\\\\\n"
      "\\bottomrule\\end{tabular}\\end{table}")

rows = ""
for x in R["grid"]["top_n"][:8]:
    rows += f"{tex(x['place'])} & {x['n']:,} & {x['lin']:,}\\\\\n"
TC = ("\\begin{table}[tbp]\\centering\\small\\caption{The eight " + str(R['grid']['cell_km']) + " km squares with the most living languages, named by the admin-1 region where most of their languages lie.}\\label{tab:cells}"
      "\\begin{tabular}{lrr}\\toprule Square (region, country) & Living languages & Lineages\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")

KEYS = {k: k for k in HL["REFS"]}
rows = ""
for h in HL["H"]:
    cite = "; ".join(f"\\citealt{{{k}}}" for k in h["refs"].split(";"))
    rows += f"{tex(h['family'])} & \\textbf{{{tex(h['hyp'])}}}: {tex(h['place'])} & {tex(h['date'])} & {cite}\\\\\n"
TH = ("{\\small\\setlength{\\tabcolsep}{4pt}\\begin{longtable}{>{\\raggedright\\arraybackslash}p{2.1cm}>{\\raggedright\\arraybackslash}p{5.1cm}>{\\raggedright\\arraybackslash}p{4.1cm}>{\\raggedright\\arraybackslash}p{3.6cm}}"
      "\\caption{Proposed homelands and dates from the literature. Places are approximate centres of the proposed regions. These are hypotheses, several of them contested.}\\label{tab:homelands}\\\\\\toprule Family & Hypothesis and place & When & Sources\\\\\\midrule\\endfirsthead\\toprule Family & Hypothesis and place & When & Sources\\\\\\midrule\\endhead\n"
      + rows + "\\bottomrule\\end{longtable}}")


SHORT = {"anthony2015": "Anthony and Ringe", "adelaar2004": "Adelaar and Muysken", "gray2009": "Gray et al.", "zhang2019": "Zhang et al.",
         "bouckaert2018": "Bouckaert et al.", "williamson2000": "Williamson and Blench", "savelyev2020": "Savelyev and Robbeets", "ehret2004": "Ehret et al."}


def label(ref, key=None):
    if key in SHORT:
        return f"{SHORT[key]}({re.search(r'[(](\d{4})[)]', ref).group(1)})"
    m = re.match(r"^(.*?) \((\d{4})\)", ref)
    au, yr = m.group(1), m.group(2)
    names = [x.strip() for x in re.split(r",? and |, (?=[A-Z][^,]*, [A-Z]\.)", au)]
    sur = [n.split(",")[0] for n in names]
    if " et al." in au:
        short = sur[0].replace(" et al.", "") + " et al."
    elif len(sur) == 1:
        short = sur[0]
    elif len(sur) == 2:
        short = f"{sur[0]} and {sur[1]}"
    else:
        short = f"{sur[0]} et al."
    return f"{short}({yr})"


EXTRA = {
    "glottolog": ("Hammarström et al.(2025)", f"Hammarström, H., Forkel, R., Haspelmath, M. and Bank, S. (2025) Glottolog {R['meta']['glottolog']}. Leipzig: Max Planck Institute for Evolutionary Anthropology. CLDF release, CC BY 4.0. \\url{{https://glottolog.org}}"),
    "wikidata": ("Vrandečić and Krötzsch(2014)", "Vrandečić, D. and Krötzsch, M. (2014) Wikidata: a free collaborative knowledgebase. \\emph{Communications of the ACM} 57(10), 78 to 85. Data CC0, \\url{https://www.wikidata.org/}"),
    "naturalearth": ("Natural Earth(2026)", "Natural Earth (2026) Admin 0 countries, land, admin 1 states and provinces, populated places. Public domain. \\url{https://www.naturalearthdata.com/}"),
    "equalearth": ("Šavrič et al.(2019)", "Šavrič, B., Patterson, T. and Jenny, B. (2019) The Equal Earth map projection. \\emph{International Journal of Geographical Information Science} 33(3), 454 to 465."),
}
bib = []
for k, ref in HL["REFS"].items():
    r = tex(ref).replace("\\&", "\\&")
    r = re.sub(r"(\d+)-(\d+)\.$", r"\1 to \2.", r)
    bib.append((ref, f"\\bibitem[{label(ref, k)}]{{{k}}} {r}"))
for k, (lab, txt) in EXTRA.items():
    bib.append((txt, f"\\bibitem[{lab}]{{{k}}} {txt}"))
bib.sort(key=lambda x: x[0].replace("Š", "S"))
BIB = "\\begin{thebibliography}{40}\n" + "\n".join(b for _, b in bib) + "\n\\end{thebibliography}"

t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
for k in ("page", "repo"):
    t = t.replace("\\url{{{meta.%s}}}" % k, "\\url{%s}" % R["meta"][k])
t = fill(t, R, tex=True)
t = t.replace("{{TABLE_SOURCES}}", TS).replace("{{TABLE_CELLS}}", TC).replace("{{TABLE_HOMELANDS}}", TH).replace("{{BIBLIOGRAPHY}}", BIB)
t = placeholders(t)
left = set(re.findall(r"\{\{([^}]*)\}\}", t))
assert left <= {"DOI"}, left
assert "--" not in t and "\u2014" not in t and "\u2013" not in t
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
# until the DOI is known the .tex keeps the {{DOI}} placeholder; the PDF shows it as visible text
tc = t.replace("\\href{https://doi.org/{{DOI}}}{https://doi.org/{{DOI}}}", "https://doi.org/\\{\\{DOI\\}\\}").replace("\\url{https://doi.org/{{DOI}}}", "\\url{https://doi.org/}\\{\\{DOI\\}\\}")
assert "{{DOI}}" not in tc
open(os.path.join(OUT, NAME + "_build.tex"), "w", encoding="utf-8").write(tc)
for _ in range(3):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-jobname=" + NAME, NAME + "_build.tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
os.remove(os.path.join(OUT, NAME + "_build.tex"))
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l][:12])
for ext in (".aux", ".log", ".out"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q):
        os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("\u2014") + txt.count("\u2013") + txt.count("--"))
