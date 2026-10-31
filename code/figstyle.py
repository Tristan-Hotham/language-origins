"""House style for static figures: fonts (a static Fraunces Black instance cut from the variable font, Source Serif 4,
IBM Plex Mono), colours, Natural Earth outlines and language points in the Equal Earth projection."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly
import numpy as np
from pyproj import Transformer
from common import *

FONTS = "/home/claude/ref/fonts"
FD = os.path.join(SHM, "fonts")
os.makedirs(FD, exist_ok=True)
if not os.path.exists(f"{FD}/Fraunces-Black.ttf"):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    vf = TTFont(f"{FONTS}/FrauncesVar.ttf")
    loc = {a.axisTag: a.defaultValue for a in vf["fvar"].axes}
    loc.update({"wght": 900, "opsz": 144})
    loc = {k: v for k, v in loc.items() if k in ("wght", "opsz", "SOFT", "WONK")}
    if "SOFT" in loc: loc["SOFT"] = 0
    if "WONK" in loc: loc["WONK"] = 0
    instancer.instantiateVariableFont(vf, loc).save(f"{FD}/Fraunces-Black.ttf")
DISP = fm.FontProperties(fname=f"{FD}/Fraunces-Black.ttf")
SERP = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-Regular.ttf")
SERB = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-Semibold.ttf")
fm.fontManager.addfont(f"{FONTS}/IBMPlexMono-Regular.ttf")
fm.fontManager.addfont(f"{FONTS}/IBMPlexMono-Medium.ttf")
MONO = "IBM Plex Mono"
plt.rcParams.update({"font.family": MONO, "font.size": 11, "axes.edgecolor": "#66626F", "axes.labelcolor": "#1E1C26",
                     "xtick.color": "#66626F", "ytick.color": "#66626F", "svg.fonttype": "none"})
BG, FG, MUT, LAND, RULE, HOT, GOLD = "#F8F5EE", "#1E1C26", "#66626F", "#E9E3D6", "#E2DBCF", "#1D6E8A", "#C77A1F"
tr = Transformer.from_crs(4326, 8857, always_xy=True)
W = jload(f"{DATA}/world.json")
SITE = jload(f"{DATA}/site.json")
LJ = jload(f"{DATA}/langs.json")
LG = LJ["L"]
FAM = SITE["fams"]
FCOL = [f[2] for f in FAM]
FIDX = {f[0]: i for i, f in enumerate(FAM)}
AESC = {int(k): v[1] for k, v in SITE["aes"].items()}
AESN = {int(k): v[0] for k, v in SITE["aes"].items()}


def rings(geom):
    cs = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poly in cs:
        yield np.array(poly[0])


SHAPES = []
for f in W["features"]:
    ps = []
    for ring in rings(f["geometry"]):
        x, y = tr.transform(np.clip(ring[:, 0], -179.9, 179.9), ring[:, 1])
        ps.append(np.column_stack([x, y]))
    SHAPES.append((f["properties"]["iso"], ps))
WORLD_EXT = (-12.6e6, 16.0e6, -5.9e6, 8.0e6)


def world(ax, fc=LAND, ec="#FFFFFF", lw=.35, extent=WORLD_EXT, zorder=0):
    for iso, ps in SHAPES:
        for p in ps:
            ax.add_patch(MPoly(p, closed=True, fc=fc, ec=ec, lw=lw, zorder=zorder))
    ax.set_xlim(extent[0], extent[1]); ax.set_ylim(extent[2], extent[3]); ax.set_aspect("equal"); ax.axis("off")


def xy(lat, lon):
    return tr.transform(np.asarray(lon, float), np.asarray(lat, float))


def fam_colour(l):
    return FCOL[l[4]] if l[4] >= 0 else (SITE["iso_col"] if l[4] == -1 else None)


def lang_points(ax, s=4, colour=fam_colour, alpha=.9, ec="none", lw=0, zorder=3, only=None):
    pts = [(l, colour(l)) for l in LG if l[2] is not None and (only is None or only(l))]
    pts = [(l, c) for l, c in pts if c]
    x, y = xy([l[2] for l, _ in pts], [l[3] for l, _ in pts])
    ax.scatter(x, y, s=s, c=[c for _, c in pts], alpha=alpha, edgecolors=ec, linewidths=lw, zorder=zorder)


def mix(a, b, t):
    A = [int(a[i:i + 2], 16) for i in (1, 3, 5)]; B = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(A, B))


def save(fig, name, dpi=200):
    fig.savefig(name, dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)


STAR = [(0, -11), (3.1, -3.6), (10.9, -3.4), (4.9, 1.6), (6.9, 9.4), (0, 5), (-6.9, 9.4), (-4.9, 1.6), (-10.9, -3.4), (-3.1, -3.6)]
STARM = matplotlib.path.Path([(x, -y) for x, y in STAR] + [(0, 11)], [1] + [2] * 9 + [79])


def fam_col_node(node):
    if node == "narr1281":
        return FCOL[FIDX["atla1278"]]
    return FCOL[FIDX[node]] if node in FIDX else GOLD
