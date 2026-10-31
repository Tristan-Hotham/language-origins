"""Build index.html from code/page_template.html. Every number in the text is a {{path|format}} token filled from
data/results.json; site.json, world.json and the place names are embedded; data/langs.json, data/tree.json, data/grid.json
and data/dialects.json are loaded by the page. Facts stated in words are checked in checks.py. The full-screen map snippet
(code/fullscreen_snippet.html, copied from the reference studies) is pasted before </body>.
{{DOI}} and https://blog.tristanhotham.com/2026/10/31/language-origins/ are left as placeholders for publication."""
import re
import checks  # noqa: F401
from common import *

R = jload(f"{DATA}/results.json")
SITE = jload(f"{DATA}/site.json")


def build():
    tpl = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
    html = placeholders(fill(tpl, R))
    left = set(re.findall(r"\{\{([^}]*)\}\}", html))
    assert left <= {"DOI", "BLOG_URL"}, left
    J = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    html = html.replace("/*RESULTS*/", J(R)).replace("/*SITE*/", J(SITE))
    html = html.replace("/*WORLD*/", open(f"{DATA}/world.json", encoding="utf-8").read())
    html = html.replace("/*CITIES*/", J([{"name": x["name"], "lat": x["lat"], "lon": x["lon"], "pop": x["pop"]} for x in jload(f"{DATA}/cities.json")]))
    html = html.replace("/*FULLSCREEN*/", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
    vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", html, flags=re.S)
    vis = re.sub(r"<[^>]+>", " ", vis)
    for bad in ("—", "–", "--", "DSIT", "DCMS", "civil serv"):
        assert bad not in vis, bad
    for scr in re.findall(r"<script>(.*?)</script>", html, flags=re.S):
        for bad in ("—", "–"):
            assert bad not in scr, bad
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print("index.html", len(html.encode()) // 1024, "KB")


if __name__ == "__main__":
    build()
