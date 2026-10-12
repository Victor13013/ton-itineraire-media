# -*- coding: utf-8 -*-
"""Rendu des visuels et Reels Pulse Care + planning Make.

Usage : python render/render.py [--fake] [--only DATE]
  --fake : remplace les photos par des images de test (pas de réseau)
Sorties : media/posts/*.jpg · media/reels/*.mp4 · planning/*.json · index.html
"""
import io, json, math, os, re, subprocess, sys, time, urllib.request
from collections import Counter
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "render"))
from content import POSTS, SHOP, CTA_IG, CTA_FB  # noqa: E402
from content_am import POSTS_AM  # noqa: E402
SLOTS = [("", POSTS, 0), ("-10h", POSTS_AM, 1)]   # 18h -> AAAA-MM-JJ.json · 10h -> AAAA-MM-JJ-10h.json
ALL = [p for _, L, _ in SLOTS for p in L]
# Les posts publiés en test ont une date préfixée "test-" : leur fichier n'est lu par aucun scénario

FAKE = "--fake" in sys.argv
ONLY = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
RAW = "https://raw.githubusercontent.com/Victor13013/ton-itineraire-media/pulse-care/"
PAGES = "https://victor13013.github.io/pulse-care-media/"

GREEN = (30, 58, 47); DEEP = (18, 36, 29); CREAM = (243, 238, 228)
BAMBOO = (196, 158, 98); MINT = (221, 232, 223); WHITE = (255, 255, 255)

FD = os.path.join(ROOT, "render", "fonts")
_fc = {}
def F(name, size):
    k = (name, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(os.path.join(FD, name), size)
    return _fc[k]
def BOLD(s): return F("Poppins-Bold.ttf", s)
def MED(s): return F("Poppins-Medium.ttf", s)
def REG(s): return F("Poppins-Regular.ttf", s)
def ARR(s): return F("Inter-Bold.otf", s)

def nb(t):  # espaces insécables avant ? ! : ; €
    return re.sub(r" ([?!:;€])", " \\1", t)

# ───────────────────────────── sources
CACHE = os.path.join(ROOT, "render", ".cache")
def src_url(ref):
    k, v = ref.split(":", 1)
    if k == "s":
        return SHOP + v + "?width=2000"
    return f"https://images.unsplash.com/photo-{v}?w=2000&q=85&fm=jpg"

def load(ref):
    if FAKE:
        h = abs(hash(ref)) % 360
        im = Image.new("RGB", (1600, 1600))
        a = np.linspace(0, 1, 1600)
        r = (90 + 80 * np.outer(a, np.ones(1600))).astype(np.uint8)
        g = (110 + 60 * np.outer(np.ones(1600), a)).astype(np.uint8)
        b = np.full((1600, 1600), (h % 120) + 60, np.uint8)
        im = Image.fromarray(np.dstack([r, g, b]))
        ImageDraw.Draw(im).ellipse([500, 400, 1100, 1000], fill=(230, 220, 200))
        return im
    os.makedirs(CACHE, exist_ok=True)
    fn = os.path.join(CACHE, re.sub(r"[^a-zA-Z0-9.-]", "_", ref) + ".bin")
    if not os.path.exists(fn):
        for i in range(4):
            try:
                req = urllib.request.Request(src_url(ref), headers={"User-Agent": "pulse-care-media/1.0"})
                data = urllib.request.urlopen(req, timeout=60).read()
                open(fn, "wb").write(data); break
            except Exception as e:
                print("retry", ref, e); time.sleep(3 * (i + 1))
        else:
            raise RuntimeError("download failed: " + ref)
    im = Image.open(fn)
    im = ImageOps.exif_transpose(im)
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA"); bg = Image.new("RGB", im.size, WHITE); bg.paste(im, mask=im.split()[3]); im = bg
    return im.convert("RGB")

def cover(im, w, h, fx=0.5, fy=0.5):
    s = max(w / im.width, h / im.height)
    nw, nh = math.ceil(im.width * s), math.ceil(im.height * s)
    im = im.resize((nw, nh), Image.LANCZOS)
    x = int((nw - w) * fx); y = int((nh - h) * fy)
    return im.crop((x, y, x + w, y + h))

# ───────────────────────────── texte
def wrap(text, fnt, maxw):
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    out = []
    for para in nb(text).split("\n"):
        line = ""
        for w in para.split(" "):
            t = (line + " " + w).strip()
            if d.textlength(t, font=fnt) <= maxw: line = t
            else:
                if line: out.append(line)
                line = w
        out.append(line)
    return out

def fit(text, maker, maxw, start, minsize, maxlines):
    s = start
    while s > minsize and len(wrap(text, maker(s), maxw)) > maxlines:
        s -= 4
    return maker(s)

def draw_lines(d, x, y, lines, fnt, fill, lh=1.15, anchor_center=False, W=1080):
    for l in lines:
        if anchor_center:
            tw = d.textlength(l, font=fnt); d.text(((W - tw) / 2, y), l, font=fnt, fill=fill)
        else:
            d.text((x, y), l, font=fnt, fill=fill)
        y += fnt.size * lh
    return y

def text_h(lines, fnt, lh=1.15): return fnt.size * lh * len(lines)

def pill(d, x, y, text, fnt, bg, fg, padx=22, pady=10):
    tw = d.textlength(text, font=fnt)
    h = fnt.size + pady * 2
    d.rounded_rectangle([x, y, x + tw + padx * 2, y + h], radius=h // 2, fill=bg)
    d.text((x + padx, y + pady - fnt.size * 0.12), text, font=fnt, fill=fg)
    return x + tw + padx * 2, y + h

def wordmark(d, x, y, fg, size=30):
    d.ellipse([x, y + size * 0.32, x + size * 0.5, y + size * 0.82], fill=BAMBOO)
    d.text((x + size * 0.8, y), "PULSE CARE", font=MED(size), fill=fg)

def gradient(w, h, color, start, end, a0=0, a1=235):
    g = np.zeros((h, w, 4), np.uint8); g[..., :3] = color
    ys = np.arange(h) / h
    a = np.clip((ys - start) / max(end - start, 1e-6), 0, 1)
    a = a ** 1.4 * (a1 - a0) + a0
    g[..., 3] = (a[:, None] * np.ones(w)).astype(np.uint8)
    return Image.fromarray(g, "RGBA")

def shadow_paste(base, im, x, y, radius=36, blur=30, alpha=70):
    w, h = im.size
    sh = Image.new("RGBA", (w + blur * 4, h + blur * 4), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle([blur * 2, blur * 2 + 14, blur * 2 + w, blur * 2 + h + 14], radius=radius, fill=(18, 36, 29, alpha))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(sh, (x - blur * 2, y - blur * 2))
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w, h], radius=radius, fill=255)
    base.paste(im, (x, y), m)

def footer(d, W, H, fg, page=None, swipe=False, acc=BAMBOO):
    if page:
        f = MED(26); tw = d.textlength(page, font=f)
        d.text((W - 70 - tw, H - 84), page, font=f, fill=fg)
    if swipe:
        f = MED(30); d.text((70, H - 88), "Swipe", font=f, fill=acc)
        d.text((70 + d.textlength("Swipe ", font=f), H - 90), "→", font=ARR(32), fill=acc)

# ───────────────────────────── visuels 1080x1350 (v2 : éditorial)
W, H = 1080, 1350
M = 90                      # marge
INK = (34, 52, 44); SOFT = (92, 110, 100); SAGE = (205, 220, 208); SAND = (233, 224, 207)

def SERIF(size, italic=False, w=600):
    k = ("lora", size, italic, w)
    if k not in _fc:
        f = ImageFont.truetype(os.path.join(FD, "Lora-Italic-Variable.ttf" if italic else "Lora-Variable.ttf"), size)
        try: f.set_variation_by_axes([w])
        except Exception: pass
        _fc[k] = f
    return _fc[k]

def tracked(d, x, y, text, fnt, fill, tr=0.16, center_w=None):
    """Texte espacé (lettrage)."""
    sp = fnt.size * tr
    tw = sum(d.textlength(ch, font=fnt) for ch in text) + sp * (len(text) - 1)
    if center_w: x = x + (center_w - tw) / 2
    for ch in text:
        d.text((x, y), ch, font=fnt, fill=fill); x += d.textlength(ch, font=fnt) + sp
    return tw

def kicker(d, x, y, text, fill, line=True, center_w=None, size=26):
    f = MED(size)
    if line and not center_w:
        d.line([(x, y + size * 0.62), (x + 44, y + size * 0.62)], fill=fill, width=3); x += 62
    tracked(d, x, y, text.upper(), f, fill, 0.2, center_w)

def brand(d, x, y, fill, center_w=None):
    tracked(d, x, y, "PULSE CARE", MED(22), fill, 0.42, center_w)

# texte riche : *mot* = italique couleur accent
def tokens(text):
    out = []
    for i, part in enumerate(re.split(r"\*", nb(text))):
        for line_i, seg in enumerate(part.split("\n")):
            if line_i: out.append(("\n", False))
            for w in seg.split(" "):
                if w: out.append((w, i % 2 == 1))
    return out

def rich_lines(text, size, maxw):
    d = ImageDraw.Draw(Image.new("L", (1, 1)))
    lines, cur, cw = [], [], 0
    for w, it in tokens(text):
        if w == "\n":
            lines.append(cur); cur, cw = [], 0; continue
        f = SERIF(size, it, 500 if it else 600)
        ww = d.textlength(w, font=f); sp = d.textlength(" ", font=SERIF(size))
        if w.startswith("\u00a0") and cur:          # « ? » « ! » collés au mot précédent
            pw, pit, pww = cur[-1]; cur[-1] = (pw, pit, pww, [(w, it, ww)]) if False else cur[-1]
            cur.append((w, it, ww, "glue")); cw += ww; continue
        if cur and cw + sp + ww > maxw:
            lines.append(cur); cur, cw = [], 0
        cur.append((w, it, ww)); cw += (sp if len(cur) > 1 else 0) + ww
    if cur: lines.append(cur)
    return lines

def rich_fit(text, maxw, start, minsize, maxlines):
    s = start
    while s > minsize and len(rich_lines(text, s, maxw)) > maxlines: s -= 4
    return s, rich_lines(text, s, maxw)

def rich_draw(d, x, y, lines, size, fill, accent, lh=1.12, center_w=None):
    sp = d.textlength(" ", font=SERIF(size))
    for ln in lines:
        lw = sum(t[2] for t in ln) + sp * sum(1 for t in ln[1:] if len(t) == 3)
        xx = x + ((center_w - lw) / 2 if center_w else 0)
        for k, t in enumerate(ln):
            w, it, ww = t[:3]
            if len(t) == 4: xx -= sp
            d.text((xx, y), w, font=SERIF(size, it, 500 if it else 600), fill=accent if it else fill)
            xx += ww + sp
        y += size * lh
    return y

def frame(base, color=(243, 238, 228, 70), inset=34):
    ov = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).rectangle([inset, inset, base.width - inset, base.height - inset], outline=color, width=2)
    base.alpha_composite(ov)

def grain(base, amount=7):
    n = np.random.default_rng(7).normal(0, amount, (base.height, base.width, 1))
    a = np.array(base).astype(np.int16); a[..., :3] = np.clip(a[..., :3] + n, 0, 255)
    return Image.fromarray(a.astype(np.uint8), base.mode)

def foot(d, fg, page=None, swipe=False, acc=BAMBOO):
    f = MED(22)
    if page:
        tw = d.textlength(page, font=f); d.text((W - M - tw, H - 92), page, font=f, fill=fg)
    if swipe:
        tracked(d, M, H - 92, "SWIPE", f, acc, 0.3)
        d.text((M + 104, H - 96), "→", font=ARR(28), fill=acc)

def seal(base, price, cx, cy, r=104, ring=CREAM, txt=CREAM, fill=None):
    d = ImageDraw.Draw(base)
    if fill: d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ring, width=2)
    d.ellipse([cx - r + 10, cy - r + 10, cx + r - 10, cy + r - 10], outline=ring, width=1)
    f = SERIF(46 if len(price) < 7 else 40, True, 500); p = nb(price)
    tw = d.textlength(p, font=f); d.text((cx - tw / 2, cy - 30), p, font=f, fill=txt)

def border_px(im):
    a = np.array(im.convert("RGB").resize((200, 200))).astype(np.float32)
    return np.concatenate([a[:6].reshape(-1, 3), a[-6:].reshape(-1, 3), a[:, :6].reshape(-1, 3), a[:, -6:].reshape(-1, 3)])

def fit_size(im, mw, mh):
    r = min(mw / im.width, mh / im.height); return max(1, int(im.width * r)), max(1, int(im.height * r))

def is_packshot(im):
    b = border_px(im); return b.mean() > 232 and b.std() < 14

def is_flat(im):
    b = border_px(im); return b.std(axis=0).max() < 16

def whiten(im):
    """Fond clair légèrement gris/crème -> blanc pur (pour fondre le produit dans le décor)."""
    b = border_px(im).mean(axis=0)
    a = np.array(im.convert("RGB")).astype(np.float32)
    return Image.fromarray(np.clip(a / np.maximum(b, 1) * 255, 0, 255).astype(np.uint8))

def prep(src):
    """Normalise les photos produit à fond uni : renvoie (image, est_packshot)."""
    if is_packshot(src): return src, True
    b = border_px(src)
    if (b.min(axis=1) > 238).mean() > 0.8: return whiten(src), True
    if is_flat(src):
        r, g, bl = b.mean(axis=0)
        if g > r and g > bl: return src, False        # fond vert : déjà dans la charte, on garde la photo
        return rekey(src, (255, 255, 255)), True
    return src, False

def rekey(im, target):
    """Remplace un fond uni (rose, olive...) par la couleur de la charte."""
    b = border_px(im).mean(axis=0)
    a = np.array(im.convert("RGB")).astype(np.float32)
    dist = np.sqrt(((a - b) ** 2).sum(axis=2))
    alpha = np.clip((dist - 28) / 40, 0, 1)[..., None]
    out = a * alpha + np.array(target, np.float32) * (1 - alpha)
    return Image.fromarray(out.astype(np.uint8))

def trim(im, pad=0.06):
    a = np.array(im.convert("L")); ys, xs = np.where(a < 225)
    if len(xs) < 50: return im
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    px, py = int((x1 - x0) * pad) + 10, int((y1 - y0) * pad) + 10
    return im.crop((max(0, x0 - px), max(0, y0 - py), min(im.width, x1 + px), min(im.height, y1 + py)))

def multiply_on(bg, im):
    a = np.array(bg.convert("RGB")).astype(np.float32); b = np.array(im.convert("RGB")).astype(np.float32)
    return Image.fromarray((a * b / 255).astype(np.uint8))

def arch_mask(w, h):
    m = Image.new("L", (w, h), 0); d = ImageDraw.Draw(m)
    d.rectangle([0, w // 2, w, h], fill=255); d.ellipse([0, 0, w, w], fill=255)
    return m

# ───────────────────────────── v4 : codes des marques DTC qui performent
# Grosse typo sans-serif noire, produit détouré sur aplat de couleur, callouts,
# cartes blanches, texte « natif » sur photo, bento. Pas de cadre.
def BLACK(s): return F("InterDisplay-Black.otf", s)
def XB(s): return F("InterDisplay-ExtraBold.otf", s)
def DB(s): return F("InterDisplay-Bold.otf", s)
def SB(s): return F("Inter-SemiBold.otf", s)
def IM(s): return F("Inter-Medium.otf", s)
def IR(s): return F("Inter-Regular.otf", s)

FOREST = (24, 52, 40); MINTV = (210, 234, 220); SANDV = (243, 232, 214); HONEY = (236, 205, 150)
LIME = (214, 240, 120); INKV = (16, 28, 22); GREYV = (84, 98, 90)
BGS = [MINTV, SANDV, HONEY, FOREST]
def bg_for(c, k=0): return BGS[(c.get("_n", 0) + k) % len(BGS)]
def on(bg): return CREAM if bg == FOREST else INKV
def sub_on(bg): return (200, 214, 204) if bg == FOREST else GREYV
def hl_on(bg): return LIME if bg == FOREST else FOREST

def clean(t): return t.replace("*", "")

def mk_tokens(text):
    out = []
    for i, part in enumerate(re.split(r"\*", nb(text))):
        for j, seg in enumerate(part.split("\n")):
            if j: out.append(("\n", False))
            for w in seg.split(" "):
                if w: out.append((w, i % 2 == 1))
    return out

def sans_lines(text, fnt, maxw):
    d = ImageDraw.Draw(Image.new("L", (1, 1))); sp = d.textlength(" ", font=fnt)
    lines, cur, cw = [], [], 0
    for w, hl in mk_tokens(text):
        if w == "\n": lines.append(cur); cur, cw = [], 0; continue
        ww = d.textlength(w, font=fnt)
        if w.startswith(" ") and cur: cur.append((w, hl, ww, 1)); cw += ww; continue
        if cur and cw + sp + ww > maxw: lines.append(cur); cur, cw = [], 0
        cur.append((w, hl, ww, 0)); cw += (sp if len(cur) > 1 else 0) + ww
    if cur: lines.append(cur)
    return lines

def sans_fit(text, maker, maxw, start, minsize, maxlines):
    s_ = start
    while s_ > minsize and len(sans_lines(text, maker(s_), maxw)) > maxlines: s_ -= 4
    return maker(s_), sans_lines(text, maker(s_), maxw)

def sans_draw(base, x, y, lines, fnt, fill, hl_bg=None, hl_fg=None, lh=1.0, center_w=None):
    """Titre gras ; les *mots* consécutifs reçoivent un seul surlignage façon marqueur."""
    d = ImageDraw.Draw(base); sp = d.textlength(" ", font=fnt); pad = fnt.size * 0.14
    for ln in lines:
        lw = sum(t[2] for t in ln) + sp * sum(1 for t in ln[1:] if not t[3])
        xx = x + ((center_w - lw) / 2 if center_w else 0)
        pos = []
        for w, hl, ww, glue in ln:
            if glue: xx -= sp
            pos.append((w, hl, ww, xx)); xx += ww + sp
        if hl_bg:   # regroupe les mots surlignés contigus
            run = None
            for w, hl, ww, px in pos + [("", False, 0, 0)]:
                if hl and run is None: run = [px, px + ww]
                elif hl: run[1] = px + ww
                elif run is not None:
                    d.rounded_rectangle([run[0] - pad, y + fnt.size * 0.08, run[1] + pad, y + fnt.size * 1.1], radius=int(fnt.size * 0.16), fill=hl_bg); run = None
        for w, hl, ww, px in pos:
            d.text((px, y), w, font=fnt, fill=(hl_fg if (hl and hl_fg) else fill))
        y += fnt.size * lh
    return y + (fnt.size * 0.12)

def handle(d, x, y, fill, center_w=None):
    f = SB(24); t = "@pulsecare.france"
    if center_w: x = x + (center_w - d.textlength(t, font=f)) / 2
    d.text((x, y), t, font=f, fill=fill)

def dots(d, n, k, fill, dim):
    if not n: return
    r, g = 7, 22; x = W - M - (n - 1) * g
    for i in range(n):
        d.ellipse([x + i * g - r, H - 74 - r, x + i * g + r, H - 74 + r], fill=fill if i == k else dim)

def page_info(c):
    if c.get("page"):
        a_, b_ = c["page"].split("/"); return int(b_), int(a_) - 1
    if c.get("swipe"): return 0, 0
    return 0, 0

def swipe_btn(base, color, fg):
    d = ImageDraw.Draw(base); r = 46; cx, cy = W - M - r, H - 74 - 0
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    tw = d.textlength("→", font=ARR(40)); d.text((cx - tw / 2, cy - 26), "→", font=ARR(40), fill=fg)

def chrome(base, c, fg, dim, light_btn=True):
    """Seul élément d'interface gardé : le bouton swipe sur les couvertures."""
    if c.get("swipe"): swipe_btn(base, CREAM if light_btn else FOREST, INKV if light_btn else CREAM)

def pill_box(d, x, y, text, fnt, bg, fg, padx=22, pady=12, r=None):
    tw = d.textlength(text, font=fnt); h = fnt.size + 2 * pady
    d.rounded_rectangle([x, y, x + tw + 2 * padx, y + h], radius=r if r is not None else h // 2, fill=bg)
    d.text((x + padx, y + pady - fnt.size * 0.08), text, font=fnt, fill=fg)
    return x + tw + 2 * padx, y + h

def sticker_v4(base, text, cx, cy, r=110, bg=LIME, fg=INKV, angle=-10):
    s_ = Image.new("RGBA", (2 * r + 6, 2 * r + 6), (0, 0, 0, 0)); d = ImageDraw.Draw(s_)
    d.ellipse([3, 3, 2 * r + 3, 2 * r + 3], fill=bg)
    f = BLACK(int(r * 0.42)); t = nb(text); tw = d.textlength(t, font=f)
    d.text((r + 3 - tw / 2, r + 3 - f.size * 0.62), t, font=f, fill=fg)
    s_ = s_.rotate(angle, resample=Image.BICUBIC, expand=True)
    base.alpha_composite(s_, (int(cx - s_.width / 2), int(cy - s_.height / 2)))

def touches_edge(im):
    a = np.array(im.convert("L").resize((300, 300)))
    edge = np.concatenate([a[:3].ravel(), a[-3:].ravel(), a[:, :3].ravel(), a[:, -3:].ravel()])
    return (edge < 200).mean() > 0.02

def product_cut(src, bg, mw, mh):
    """Produit détouré (fond blanc fondu dans l'aplat) ou photo arrondie."""
    im, pk = prep(src)
    if pk and touches_edge(im): pk = False
    if pk:
        prod = trim(im); prod = prod.resize(fit_size(prod, mw, mh), Image.LANCZOS)
        return multiply_on(Image.new("RGB", prod.size, bg), prod), True
    return None, False

def soft_shadow(base, box, alpha=70, blur=26):
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([x0, y1 - 26, x1, y1 + 26], fill=(10, 24, 18, alpha))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(blur)))

def rounded_photo(base, src, box, r=44, fy=0.5):
    x0, y0, x1, y1 = box; w, h = x1 - x0, y1 - y0
    im = src
    if (border_px(im).min(axis=1) > 238).mean() > 0.5:
        ww, hh = im.size; k = 0.62
        im = im.crop((int(ww * (1 - k) / 2), int(hh * (1 - k) / 2), int(ww * (1 + k) / 2), int(hh * (1 + k) / 2)))
    ph = cover(im, w, h, 0.5, fy)
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w, h], radius=r, fill=255)
    base.paste(ph, (x0, y0), m)

# ───────────────────────────── v5 : même DA, plus de graphisme
# Icônes, badges, flèches dessinées, étincelles, fonds travaillés, comparatifs.
CORAL = (226, 108, 92); WHITE_A = (255, 255, 255)

ICONS = {"tooth": "", "teeth": "", "stopwatch": "", "clock": "", "battery": "",
         "bolt": "", "plug": "", "droplet": "", "shower": "", "leaf": "",
         "seedling": "", "check": "", "xmark": "", "calendar": "", "gift": "",
         "euro": "", "box": "", "plane": "", "smile": "", "star": "",
         "heart": "", "bulb": "", "warn": "", "question": "", "rotate": "",
         "recycle": "", "truck": "", "doctor": "", "shield": "", "magic": "",
         "hourglass": "", "bacteria": "", "comment": "", "thumbs": "",
         "children": "", "feather": "", "snow": "", "candy": "", "mug": "",
         "sun": "", "moon": "", "wind": "", "wave": "", "sliders": "",
         "hand": "", "ban": "", "glass": "", "brush": "", "list": "",
         "award": "", "gauge": "", "pause": "", "money": "", "cart": ""}
KEYWORDS = [  # ordre = priorité
    (("abonnement", "livr", "automatiquement", "sans engagement", "compte"), "truck"),
    (("prix", "€", "budget", "coût", "coûte", "calcul", "pack de"), "euro"),
    (("cadeau", "offrir"), "gift"),
    (("voyage", "vacances", "trousse", "hôtel"), "plane"),
    (("étui", "boîte", "coffret"), "box"),
    (("usb", "câble", "recharge", "charge "), "plug"),
    (("autonomie", "batterie", "30 j", "mah"), "battery"),
    (("ipx7", "étanche", "douche", "immersion"), "shower"),
    (("rince", "bain de bouche", "eau", "verre d'eau", "boire", "bois de l'eau"), "droplet"),
    (("minute", "minuteur", " 30 s", "pause", "temps", "chrono", "2 min"), "stopwatch"),
    (("vibration", "sonique", "41 000"), "wave"),
    (("mode", "modes"), "sliders"),
    (("blanchiment", "tache", "polissage", "lisse"), "magic"),
    (("sensible", "doux", "douce", "douceur", "fragile"), "feather"),
    (("ricin", "végétal", "plante", "bambou", "pousse"), "leaf"),
    (("dentiste", "contrôle", "détartrage"), "doctor"),
    (("carie", "bactérie", "plaque", "tartre", "acide", "gingivite", "parodontite"), "bacteria"),
    (("sucre", "bonbon", "jus", "gélifié", "barres"), "candy"),
    (("café", "thé"), "mug"),
    (("haleine", "langue"), "wind"),
    (("famille", "enfant", "parents", "pyjama", "défi"), "children"),
    (("matin", "réveil", "petit-déj"), "sun"),
    (("soir", "nuit", "dormir"), "moon"),
    (("froid", "glace"), "snow"),
    (("appuyer", "frotter", "erreur", "oublier", "rincer juste", "garder la même"), "warn"),
    (("tête", "poils", "change", "clip", "recharge"), "rotate"),
    (("manche", "garde"), "hand"),
    (("fil", "brossette", "entre les dents"), "teeth"),
    (("gencive", "dent", "émail", "sourire", "brossage", "brosse"), "tooth"),
]
def icon_for(*texts):
    t = " ".join(x for x in texts if x).lower()
    for keys, ic in KEYWORDS:
        if any(k in t for k in keys): return ic
    return "star"

def ICONF(size): return F("fa-solid-900.ttf", size)

def draw_icon(d, name, cx, cy, size, fill):
    ch = ICONS.get(name, ICONS["star"]); f = ICONF(size)
    l, t, r, b = d.textbbox((0, 0), ch, font=f)
    d.text((cx - (l + r) / 2, cy - (t + b) / 2), ch, font=f, fill=fill)

def icon_disc(d, name, cx, cy, r, bg, fg):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg); draw_icon(d, name, cx, cy, int(r * 0.95), fg)

def sparkle(base, cx, cy, r, color):
    d = ImageDraw.Draw(base); k = r * 0.26
    d.polygon([(cx, cy - r), (cx + k, cy - k), (cx + r, cy), (cx + k, cy + k), (cx, cy + r), (cx - k, cy + k), (cx - r, cy), (cx - k, cy - k)], fill=color)

def doodle_arrow(base, p0, p1, color, bend=0.35, width=7):
    """Flèche dessinée à la main (courbe + pointe)."""
    d = ImageDraw.Draw(base)
    (x0, y0), (x1, y1) = p0, p1
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2; dx, dy = x1 - x0, y1 - y0
    cx, cy = mx - dy * bend, my + dx * bend
    pts = [((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1, (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1) for t in [i / 40 for i in range(41)]]
    d.line(pts, fill=color, width=width, joint="curve")
    for q in (pts[0], pts[-1]): d.ellipse([q[0] - width / 2, q[1] - width / 2, q[0] + width / 2, q[1] + width / 2], fill=color)
    ax, ay = pts[-1]; bx, by = pts[-4]; ang = math.atan2(ay - by, ax - bx); L = 34
    for s_ in (-0.55, 0.55):
        ex, ey = ax - L * math.cos(ang + s_), ay - L * math.sin(ang + s_)
        d.line([(ax, ay), (ex, ey)], fill=color, width=width)
        d.ellipse([ex - width / 2, ey - width / 2, ex + width / 2, ey + width / 2], fill=color)

def ring_badge(base, cx, cy, r, text, ring_bg, ring_fg, center_icon="tooth", angle=0):
    """Badge rond avec texte circulaire (code DTC)."""
    size = 2 * r + 8; im = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    c0 = size / 2
    d.ellipse([c0 - r, c0 - r, c0 + r, c0 + r], fill=ring_bg)
    d.ellipse([c0 - r * 0.52, c0 - r * 0.52, c0 + r * 0.52, c0 + r * 0.52], fill=ring_fg)
    draw_icon(d, center_icon, c0, c0, int(r * 0.44), ring_bg)
    f = SB(int(r * 0.15)); txt = text.upper() + "  •  "
    n = len(txt); rr = r * 0.76
    for i, ch in enumerate(txt):
        a_ = 2 * math.pi * i / n - math.pi / 2
        g = Image.new("RGBA", (f.size * 2, f.size * 2), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
        l, t, rt, b = gd.textbbox((0, 0), ch, font=f)
        gd.text((f.size - (l + rt) / 2, f.size - (t + b) / 2), ch, font=f, fill=ring_fg)
        g = g.rotate(-math.degrees(a_) - 90, resample=Image.BICUBIC)
        im.alpha_composite(g, (int(c0 + rr * math.cos(a_) - f.size), int(c0 + rr * math.sin(a_) - f.size)))
    im = im.rotate(angle, resample=Image.BICUBIC)
    base.alpha_composite(im, (int(cx - size / 2), int(cy - size / 2)))

def rich_bg(bg, seed=0):
    """Aplat travaillé : halo lumineux + grand disque ton sur ton + grain."""
    base = Image.new("RGBA", (W, H), bg + (255,))
    dark = bg == FOREST
    glow = Image.new("L", (W, H), 0); gd = ImageDraw.Draw(glow)
    gx, gy = (W * 0.5, H * 0.62)
    gd.ellipse([gx - 520, gy - 520, gx + 520, gy + 520], fill=110 if not dark else 70)
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    base.paste(Image.new("RGBA", (W, H), (255, 255, 255, 255)), (0, 0), glow)
    tone = tuple(max(0, int(v * (0.93 if not dark else 1.18))) if not dark else min(255, int(v * 1.25)) for v in bg)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    pos = [(W + 60, -40, 520), (-120, H - 160, 420), (W + 40, H - 100, 380)][seed % 3]
    od.ellipse([pos[0] - pos[2], pos[1] - pos[2], pos[0] + pos[2], pos[1] + pos[2]], fill=tone + (255,))
    base.alpha_composite(ov)
    return grain(base, 3)

def kicker_pill(base, x, y, text, bg, fg, icon=None, center=False):
    d = ImageDraw.Draw(base); f = SB(24); t = clean(text).upper()
    ic = icon or icon_for(text); iw = 34
    tw = d.textlength(t, font=f); h = f.size + 24; w = tw + 44 + iw
    if center: x = (W - w) / 2
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, fill=bg)
    draw_icon(d, ic, x + 22 + 12, y + h / 2, 22, fg)
    d.text((x + 22 + iw, y + 12 - f.size * 0.08), t, font=f, fill=fg)
    return y + h

def sans_draw_marks(base, x, y, lines, fnt, fill, hl_bg, hl_fg, lh=1.0, center_w=None, spark=None):
    """sans_draw + étincelles à côté du dernier surlignage."""
    d = ImageDraw.Draw(base); sp = d.textlength(" ", font=fnt); last = None
    yy = y
    for ln in lines:
        lw = sum(t[2] for t in ln) + sp * sum(1 for t in ln[1:] if not t[3])
        xx = x + ((center_w - lw) / 2 if center_w else 0)
        for w, hl, ww, glue in ln:
            if glue: xx -= sp
            if hl: last = (xx + ww, yy)
            xx += ww + sp
        yy += fnt.size * lh
    out = sans_draw(base, x, y, lines, fnt, fill, hl_bg, hl_fg, lh, center_w)
    if spark and last:
        lx, ly = last
        if lx + 60 < W - 20:
            sparkle(base, lx + 34, ly + 4, 20, spark); sparkle(base, lx + 62, ly + 38, 11, spark)
    return out

def info_chip(base, x, y, text, icon, maxw=W - 2 * M, bg=WHITE_A, fg=INKV, ic_bg=FOREST, ic_fg=LIME):
    d = ImageDraw.Draw(base); f = IM(30)
    lines = wrap(text, f, maxw - 120); h = max(84, 30 + f.size * 1.32 * len(lines))
    w = min(maxw, 112 + max(d.textlength(l, font=f) for l in lines) + 28)
    d.rounded_rectangle([x, y, x + w, y + h], radius=26, fill=bg)
    icon_disc(d, icon, x + 50, y + h / 2, 28, ic_bg, ic_fg)
    draw_lines(d, x + 96, y + (h - f.size * 1.32 * len(lines)) / 2 - 2, lines, f, fg, 1.32)
    return y + h

# ── 1. Hook : photo plein cadre + gros titre natif
def t_hero(c):
    src = load(c["img"])
    if prep(src)[1]: return t_product(c)
    base = cover(src, W, H, 0.5, c.get("fy", 0.5)).convert("RGBA")
    base.alpha_composite(gradient(W, H, (8, 18, 12), 0.0, 0.58, 170, 0))
    base.alpha_composite(gradient(W, H, (8, 18, 12), 0.70, 1.0, 0, 170))
    y = 104
    if c.get("kicker"): y = kicker_pill(base, M, y, c["kicker"], LIME, INKV) + 26
    f, tl = sans_fit(c["title"], BLACK, W - 2 * M, 112, 64, 4)
    y = sans_draw_marks(base, M, y, tl, f, WHITE, LIME, INKV, 1.02, spark=LIME)
    if c.get("sub"):
        info_chip(base, M, y + 22, c["sub"], icon_for(c.get("kicker", ""), c["sub"], clean(c["title"])), maxw=W - 2 * M - 40)
    if c.get("price"):
        sticker_v4(base, c["price"], W - M - 110, H - 300)
    elif c.get("_n", 0) % 2 == 0:
        ring_badge(base, M + 108, H - M - 108, 108, "Brosse à dents électrique · Pulse Care", LIME, INKV, icon_for(clean(c["title"])), angle=-8)
    chrome(base, c, WHITE, (255, 255, 255, 110))
    return base.convert("RGB")

# ── 2. Question : texte en boîtes blanches façon story
def t_statement(c):
    base = cover(load(c["img"]), W, H).convert("RGBA")
    base.alpha_composite(Image.new("RGBA", (W, H), (8, 18, 12, 110)))
    d = ImageDraw.Draw(base)
    f, tl = sans_fit(clean(c["title"]), XB, W - 2 * M - 60, 76, 50, 5)
    sub = wrap(c["sub"], IM(34), W - 2 * M - 80) if c.get("sub") else []
    lh = f.size + 30
    total = 150 + (70 if c.get("kicker") else 0) + lh * len(tl) + (24 + 64 * len(sub) if sub else 0)
    y = (H - total) / 2
    ic = icon_for(c.get("kicker", ""), clean(c["title"]), c.get("sub", ""))
    icon_disc(d, ic, W / 2, y + 56, 56, LIME, INKV)
    sparkle(base, W / 2 + 74, y + 8, 18, LIME); sparkle(base, W / 2 - 80, y + 96, 11, WHITE_A)
    y += 140
    if c.get("kicker"): y = kicker_pill(base, 0, y, c["kicker"], WHITE_A, INKV, icon="star" if False else None, center=True) + 18
    d = ImageDraw.Draw(base)
    for i, ln in enumerate(tl):
        txt = " ".join(t[0] for t in ln).replace("  ", " ")
        tw = d.textlength(txt, font=f)
        d.rounded_rectangle([(W - tw) / 2 - 26, y, (W + tw) / 2 + 26, y + f.size + 22], radius=16, fill=WHITE_A)
        d.text(((W - tw) / 2, y + 8), txt, font=f, fill=INKV); y += lh
    y += 24
    for ln in sub:
        tw = d.textlength(ln, font=IM(34))
        d.rounded_rectangle([(W - tw) / 2 - 20, y, (W + tw) / 2 + 20, y + 56], radius=12, fill=FOREST)
        d.text(((W - tw) / 2, y + 8), ln, font=IM(34), fill=CREAM); y += 64
    chrome(base, c, WHITE, (255, 255, 255, 110))
    return base.convert("RGB")

# ── 3. Produit : fond travaillé, produit sur socle, puces à icônes, flèche dessinée
def t_product(c):
    bg = [MINTV, SANDV, HONEY][c.get("_n", 0) % 3]; fg = on(bg)
    base = rich_bg(bg, c.get("_n", 0))
    y = 96
    if c.get("kicker"): y = kicker_pill(base, 0, y, c["kicker"], FOREST, CREAM, center=True) + 24
    f, tl = sans_fit(c["title"], BLACK, W - 2 * M, 92, 56, 2)
    y = sans_draw_marks(base, 0, y, tl, f, fg, FOREST, CREAM, 1.02, center_w=W, spark=FOREST)
    if c.get("sub"):
        y = draw_lines(ImageDraw.Draw(base), 0, y + 10, wrap(c["sub"], IM(30), W - 2 * M - 80), IM(30), sub_on(bg), 1.4, anchor_center=True, W=W)
    top = int(y + 40); bottom = H - 150
    src = load(c["img"])
    cut, pk = product_cut(src, (255, 255, 255), W - 300, bottom - top - 30)
    if pk:
        px = (W - cut.width) // 2; py = top + (bottom - top - cut.height) // 2
        # socle : disque clair + ombre
        sd = ImageDraw.Draw(base); cxm = W / 2; ry = 26; rx = min(max(cut.width * 0.55, 150), 300)
        sd.ellipse([cxm - rx, py + cut.height - ry, cxm + rx, py + cut.height + ry], fill=tuple(int(v * 0.95) for v in bg))
        soft_shadow(base, (cxm - rx * 0.6, py + cut.height - 22, cxm + rx * 0.6, py + cut.height + 2), 55, 18)
        region = base.crop((px, py, px + cut.width, py + cut.height)).convert("RGB")
        base.paste(multiply_on(region, cut), (px, py))
        pbox = (px, py, px + cut.width, py + cut.height)
    else:
        pbox = (M, top, W - M, bottom); rounded_photo(base, src, pbox)
    d = ImageDraw.Draw(base)
    calls = c.get("callouts", [])
    for i, txt in enumerate(calls):          # puces reliées au produit
        left = i % 2 == 0; cy = pbox[1] + (pbox[3] - pbox[1]) * (0.30 + 0.56 * (i // 2) / max(1, (len(calls) - 1) // 2))
        cx = (pbox[0] + pbox[2]) / 2 + (-30 if left else 30)
        f2 = SB(27); tw = d.textlength(txt, font=f2); w = tw + 96; bx = M - 20 if left else W - M + 20 - w
        ex = bx + w if left else bx
        for k in range(0, int(abs(ex - cx)), 14):   # pointillés
            xx = cx - k if left else cx + k
            d.line([(xx, cy), (xx + (-7 if left else 7), cy)], fill=fg, width=3)
        d.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=FOREST); d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=LIME)
        d.rounded_rectangle([bx, cy - 32, bx + w, cy + 32], radius=32, fill=WHITE_A)
        icon_disc(d, icon_for(txt), bx + 34, cy, 22, FOREST, LIME)
        d.text((bx + 66, cy - f2.size * 0.62), txt, font=f2, fill=INKV)
    if c.get("price"):
        sx, sy = W - M - 90, top + 90
        sticker_v4(base, c["price"], sx, sy)
        if not calls and pk: doodle_arrow(base, (sx - 70, sy + 110), (pbox[2] - 10, sy + 230), FOREST, bend=-0.35)
    elif pk and not calls:
        doodle_arrow(base, (M + 30, top + 40), (pbox[0] - 14, top + 170), FOREST, bend=0.4)
    sparkle(base, pbox[0] - 10 if pk else M + 30, pbox[1] + 20, 22, FOREST)
    chrome(base, c, fg, sub_on(bg), light_btn=False)
    return base.convert("RGB")

# ── 4. Liste : photo en tête, cartes blanches à icônes
def t_list(c):
    bg = bg_for(c, 1) if bg_for(c, 1) != FOREST else MINTV
    base = rich_bg(bg, c.get("_n", 0) + 1)
    src = load(c["img"]); im, pk = prep(src); ph_h = 520
    if pk and touches_edge(im): pk = False
    if pk:
        cut, _ = product_cut(src, (255, 255, 255), W - 300, ph_h - 120)
        band = multiply_on(Image.new("RGB", (W, ph_h), CREAM), Image.new("RGB", (W, ph_h), WHITE_A))
        band.paste(multiply_on(Image.new("RGB", cut.size, CREAM), cut), ((W - cut.width) // 2, (ph_h - cut.height) // 2 + 30))
        base.paste(band, (0, 0)); title_fg = INKV
    else:
        ph = cover(im, W, ph_h).convert("RGBA"); ph.alpha_composite(gradient(W, ph_h, (8, 18, 12), 0.25, 1, 0, 210))
        base.paste(ph, (0, 0)); title_fg = WHITE_A
    if c.get("stamp"):                                   # tampon MYTHE / FAUX
        st = Image.new("RGBA", (360, 130), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        sd.rounded_rectangle([4, 4, 356, 126], radius=20, outline=CORAL, width=8)
        fs = BLACK(72); tw = sd.textlength(c["stamp"], font=fs); sd.text(((360 - tw) / 2, 18), c["stamp"], font=fs, fill=CORAL)
        st = st.rotate(-12, resample=Image.BICUBIC, expand=True); base.alpha_composite(st, (W - M - st.width + 20, 70))
    f, tl = sans_fit(c["title"], BLACK, W - 2 * M, 74, 50, 2)
    sans_draw_marks(base, M, ph_h - 40 - f.size * 1.02 * len(tl), tl, f, title_fg, LIME, INKV, 1.02, spark=LIME if title_fg == WHITE_A else FOREST)
    d = ImageDraw.Draw(base)
    y = ph_h + 40; n = len(c["items"]); fa = 36 if n <= 3 else 32; fb = 27 if n <= 3 else 25
    avail = H - 130 - y; gap = 18
    ch = min((avail - gap * (n - 1)) / n, 190)
    numbered = c.get("numbered")
    for i, (a_, b_) in enumerate(c["items"]):
        if numbered and i < n - 1:   # fil de la timeline
            d.line([(M + 30, y + ch / 2), (M + 30, y + ch + gap + ch / 2)], fill=FOREST, width=4)
        d.rounded_rectangle([M - 20, y, W - M + 20, y + ch], radius=28, fill=WHITE_A)
        r = 32; cx, cy = M + 30, y + ch / 2; ic = icon_for(a_, b_)
        if numbered:
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=FOREST)
            num = str(c.get("start", 1) + i); fnum = BLACK(32); tw = d.textlength(num, font=fnum)
            d.text((cx - tw / 2, cy - fnum.size * 0.62), num, font=fnum, fill=LIME)
            # icône rappel à droite
            d.rounded_rectangle([W - M - 66, cy - 30, W - M + 2, cy + 30], radius=18, fill=bg)
            draw_icon(d, ic, W - M - 32, cy, 28, FOREST)
            maxw = W - 2 * M - 200
        else:
            icon_disc(d, ic, cx, cy, r, FOREST, LIME); maxw = W - 2 * M - 120
        la = wrap(a_, DB(fa), maxw); lb = wrap(b_, IR(fb), maxw) if b_ else []
        th = fa * 1.15 * len(la) + (6 + fb * 1.3 * len(lb) if lb else 0)
        ty = draw_lines(d, M + 90, cy - th / 2, la, DB(fa), INKV, 1.15)
        if lb: draw_lines(d, M + 90, ty + 6, lb, IR(fb), GREYV, 1.3)
        y += ch + gap
    chrome(base, c, INKV, GREYV)
    return base.convert("RGB")

# ── 5. Bento : photo + tuiles chiffres à icônes
def t_stats(c):
    base = rich_bg(FOREST, c.get("_n", 0)); d = ImageDraw.Draw(base)
    f, tl = sans_fit(c["title"], BLACK, W - 2 * M, 84, 56, 2)
    y = sans_draw_marks(base, M, 96, tl, f, CREAM, LIME, INKV, 1.02, spark=LIME) + 30
    g = 20; tw_ = (W - 2 * M - g) // 2; ph_h = 330
    rounded_photo(base, load(c["img"]), (M, int(y), W - M, int(y) + ph_h), 32)
    y = int(y) + ph_h + g
    th = (H - 130 - y - g) // 2
    cols = [LIME, MINTV, SANDV, HONEY]
    d = ImageDraw.Draw(base)
    for i, (big, small) in enumerate(c["items"]):
        x = M + (i % 2) * (tw_ + g); yy = y + (i // 2) * (th + g)
        d.rounded_rectangle([x, yy, x + tw_, yy + th], radius=32, fill=cols[i])
        icon_disc(d, icon_for(big, small), x + tw_ - 52, yy + 52, 30, FOREST, cols[i])
        fb_ = BLACK(104)
        while d.textlength(nb(big), font=fb_) > tw_ - 130: fb_ = BLACK(fb_.size - 6)
        d.text((x + 30, yy + 26), nb(big), font=fb_, fill=INKV)
        ls = wrap(small, IM(28), tw_ - 64)
        draw_lines(d, x + 32, yy + th - 30 - 28 * 1.3 * len(ls), ls, IM(28), INKV, 1.3)
    chrome(base, c, CREAM, (120, 150, 132))
    return base.convert("RGB")

# ── 6. Comparatif : 2 colonnes, coches et croix
def t_versus(c):
    base = rich_bg(SANDV if c.get("_n", 0) % 2 else MINTV, c.get("_n", 0)); d = ImageDraw.Draw(base)
    y = 96
    if c.get("kicker"): y = kicker_pill(base, 0, y, c["kicker"], FOREST, CREAM, center=True) + 24
    f, tl = sans_fit(c["title"], BLACK, W - 2 * M, 96, 56, 2)
    y = sans_draw_marks(base, 0, y, tl, f, INKV, FOREST, CREAM, 1.02, center_w=W, spark=FOREST) + 30
    g = 24; cw = (W - 2 * M - g) // 2
    cols = [c["left"], c["right"]]; fi = SB(42)
    # hauteur commune des 2 cartes
    def col_h(items):
        return 170 + sum(42 * 1.24 * len(wrap(it, fi, cw - 130)) + 56 for it in items) + 40
    ch = max(col_h(it) for _, it in cols)
    avail_top, avail_bot = int(y), H - 140
    top = int(avail_top + max(0, (avail_bot - avail_top - ch) / 2)); bot = int(top + ch)
    for side, (head, items) in enumerate(cols):
        x = M + side * (cw + g); good = side == 1 or c.get("both_good")
        bgc = FOREST if side == 1 else WHITE_A; fg = CREAM if side == 1 else INKV
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([x + 6, top + 14, x + cw + 6, bot + 14], radius=40, fill=(10, 24, 18, 60))
        base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16))); d = ImageDraw.Draw(base)
        d.rounded_rectangle([x, top, x + cw, bot], radius=40, fill=bgc)
        hf = BLACK(54)
        while d.textlength(head, font=hf) > cw - 80: hf = BLACK(hf.size - 4)
        hy = top + 40; hw = d.textlength(head, font=hf)
        if side == 1: d.rounded_rectangle([x + 24, hy - 10, x + 44 + hw + 20, hy + hf.size + 16], radius=18, fill=LIME)
        d.text((x + 44, hy), head, font=hf, fill=INKV)
        iy = hy + hf.size + 64
        for it in items:
            icon_disc(d, "check" if good else "xmark", x + 62, iy + 24, 27, LIME if side == 1 else (FOREST if good else CORAL), INKV if side == 1 else WHITE_A)
            iy = draw_lines(d, x + 108, iy + 2, wrap(it, fi, cw - 130), fi, fg, 1.24) + 56
    # pastille « VS » au centre
    vx, vy = W / 2, top + 4
    d.ellipse([vx - 46, vy - 46, vx + 46, vy + 46], fill=LIME, outline=INKV, width=5)
    fv = BLACK(40); tw = d.textlength("VS", font=fv); d.text((vx - tw / 2, vy - 26), "VS", font=fv, fill=INKV)
    sparkle(base, W - M - 6, top - 10, 24, FOREST); sparkle(base, M + 10, bot + 34, 14, FOREST)
    chrome(base, c, INKV, GREYV, light_btn=False)
    return base.convert("RGB")

TPL = {"hero": t_hero, "statement": t_statement, "product": t_product, "list": t_list, "stats": t_stats, "versus": t_versus}

# ───────────────────────────── DA B : « Gradient & verre » (variante de la DA principale)
# Même palette et même typo. Fonds en dégradés doux, cartes en verre dépoli, photos
# encadrées et inclinées, mots-clés en couleur soulignés d'une vague, widgets façon notification.
TEAL = (34, 92, 78); MIST = (232, 243, 236)

def mesh_bg(kind, seed=0):
    pal = {"fresh": (MINTV, [(LIME, (0.85, 0.12), 520), (CREAM, (0.1, 0.9), 560), ((190, 228, 205), (0.2, 0.25), 420)]),
           "sand":  (SANDV, [(HONEY, (0.9, 0.85), 560), (MINTV, (0.05, 0.1), 480), (CREAM, (0.6, 0.4), 420)]),
           "forest": (FOREST, [(TEAL, (0.85, 0.15), 620), ((14, 36, 28), (0.1, 0.95), 560), ((60, 110, 70), (0.15, 0.3), 380)])}[kind]
    base = Image.new("RGB", (W, H), pal[0])
    for i, (col, (fx, fy), r) in enumerate(pal[1]):
        if seed % 2 and i == 0: fx = 1 - fx
        m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).ellipse([fx * W - r, fy * H - r, fx * W + r, fy * H + r], fill=255)
        base.paste(Image.new("RGB", (W, H), col), (0, 0), m.filter(ImageFilter.GaussianBlur(170)))
    return grain(base.convert("RGBA"), 4)

def glass(base, box, r=36, tint=(255, 255, 255), alpha=150, outline=110):
    x0, y0, x1, y1 = [int(v) for v in box]
    reg = base.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(22))
    reg = Image.alpha_composite(reg.convert("RGBA"), Image.new("RGBA", reg.size, tint + (alpha,)))
    m = Image.new("L", reg.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, reg.width - 1, reg.height - 1], radius=r, fill=255)
    base.paste(reg, (x0, y0), m)
    ImageDraw.Draw(base).rounded_rectangle([x0, y0, x1, y1], radius=r, outline=(255, 255, 255, outline), width=2)

def squiggle(d, x0, x1, y, color, amp=7, width=6):
    pts = [(x, y + amp * math.sin((x - x0) / 15.0)) for x in range(int(x0), int(x1) + 1, 3)]
    if len(pts) > 1: d.line(pts, fill=color, width=width, joint="curve")

def title_b(base, x, y, lines, fnt, fill, accent, lh=1.04, wave=None):
    """Titre ; les *mots* passent en couleur avec une vague dessous (au lieu du surlignage plein)."""
    d = ImageDraw.Draw(base); sp = d.textlength(" ", font=fnt)
    for ln in lines:
        xx = x; run = None
        for w, hl, ww, glue in ln:
            if glue: xx -= sp
            d.text((xx, y), w, font=fnt, fill=accent if hl else fill)
            if hl: run = [run[0] if run else xx, xx + ww]
            elif run: squiggle(d, run[0], run[1], y + fnt.size * 1.06, wave or accent); run = None
            xx += ww + sp
        if run: squiggle(d, run[0], run[1], y + fnt.size * 1.06, wave or accent)
        y += fnt.size * lh
    return y + fnt.size * 0.18

def framed_photo(base, src, box, angle=-4, border=16, r=34, fy=0.5):
    x0, y0, x1, y1 = box; w, h = x1 - x0, y1 - y0
    im, _ = prep(src) if False else (src, False)
    if (border_px(im).min(axis=1) > 238).mean() > 0.5:
        ww, hh = im.size; k = 0.62
        im = im.crop((int(ww * (1 - k) / 2), int(hh * (1 - k) / 2), int(ww * (1 + k) / 2), int(hh * (1 + k) / 2)))
    ph = cover(im, w - 2 * border, h - 2 * border, 0.5, fy)
    card = Image.new("RGBA", (w, h), (0, 0, 0, 0)); cd = ImageDraw.Draw(card)
    cd.rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=(255, 255, 255, 255))
    m = Image.new("L", ph.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, ph.width - 1, ph.height - 1], radius=r - 10, fill=255)
    card.paste(ph, (border, border), m)
    pad = 60; big = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    sh = Image.new("RGBA", big.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([pad + 10, pad + 24, pad + w + 10, pad + h + 24], radius=r, fill=(10, 24, 18, 90))
    big.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22))); big.alpha_composite(card, (pad, pad))
    big = big.rotate(angle, resample=Image.BICUBIC, expand=True)
    base.alpha_composite(big, (int(x0 + w / 2 - big.width / 2), int(y0 + h / 2 - big.height / 2)))

def notif(base, x, y, w, text, icon="tooth", dark=False):
    """Widget façon notification : icône d'appli, « PULSE CARE · maintenant », message."""
    f = SB(30); lines = wrap(text, f, w - 150); h = 92 + f.size * 1.28 * len(lines)
    glass(base, (x, y, x + w, y + h), 32, (255, 255, 255) if not dark else (20, 40, 32), 175 if not dark else 150)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([x + 26, y + 26, x + 92, y + 92], radius=18, fill=FOREST)
    draw_icon(d, icon, x + 59, y + 59, 32, LIME)
    fg = INKV if not dark else CREAM; sub = GREYV if not dark else (190, 210, 198)
    d.text((x + 116, y + 26), "PULSE CARE  ·  maintenant", font=SB(20), fill=sub)
    draw_lines(d, x + 116, y + 56, lines, f, fg, 1.28)
    return y + h

def pill_outline(base, x, y, text, color, center=False):
    d = ImageDraw.Draw(base); f = SB(24); t = clean(text).upper(); tw = d.textlength(t, font=f); h = f.size + 24; w = tw + 44 + 34
    if center: x = (W - w) / 2
    d.rounded_rectangle([x, y, x + w, y + h], radius=h // 2, outline=color, width=3)
    draw_icon(d, icon_for(text), x + 34, y + h / 2, 22, color)
    d.text((x + 56, y + 12 - f.size * 0.08), t, font=f, fill=color)
    return y + h

def b_title_block(base, c, dark, x=M, y=110, maxw=W - 2 * M, start=104, maxlines=3):
    fg = CREAM if dark else INKV; acc = LIME if dark else FOREST
    if c.get("kicker"): y = pill_outline(base, x, y, c["kicker"], acc) + 30
    f, tl = sans_fit(c["title"], BLACK, maxw, start, 58, maxlines)
    return title_b(base, x, y, tl, f, fg, acc)

def tb_hero(c):
    src = load(c["img"])
    if prep(src)[1]: return tb_product(c)
    n = c.get("_n", 0); base = mesh_bg(["fresh", "sand"][n % 2], n)
    y = b_title_block(base, c, False)
    top = int(y + 30); bot = H - 120
    framed_photo(base, src, (M + 40, top, W - M - 40, bot), angle=(-4 if n % 2 else 4), fy=c.get("fy", 0.45))
    if c.get("sub"): notif(base, M - 10, bot - 190, W - 2 * M + 20, c["sub"], icon_for(c.get("kicker", ""), c["sub"]))
    if c.get("price"): sticker_v4(base, c["price"], W - M - 60, top + 40, r=100)
    sparkle(base, W - M - 20, top - 20, 26, FOREST); sparkle(base, W - M - 60, top + 30, 13, FOREST)
    chrome(base, c, INKV, GREYV, light_btn=False)
    return base.convert("RGB")

def tb_statement(c):
    n = c.get("_n", 0); base = mesh_bg("forest", n)
    framed_photo(base, load(c["img"]), (W - M - 330, 90, W - M - 10, 470), angle=6)
    d = ImageDraw.Draw(base)
    d.text((M - 6, 120), "“", font=BLACK(260), fill=LIME)
    y = 520
    if c.get("kicker"): y = pill_outline(base, M, y, c["kicker"], LIME) + 30
    f, tl = sans_fit(c["title"], BLACK, W - 2 * M, 96, 56, 4)
    y = title_b(base, M, y, tl, f, CREAM, LIME)
    if c.get("sub"): notif(base, M - 10, y + 30, W - 2 * M + 20, c["sub"], icon_for(c.get("kicker", ""), c["sub"]), dark=True)
    chrome(base, c, CREAM, GREYV, light_btn=True)
    return base.convert("RGB")

def tb_product(c):
    n = c.get("_n", 0); base = mesh_bg(["fresh", "sand"][n % 2], n + 1)
    y = b_title_block(base, c, False, maxlines=2, start=96)
    if c.get("sub"): y = draw_lines(ImageDraw.Draw(base), M, y, wrap(c["sub"], IM(30), W - 2 * M - 80), IM(30), GREYV, 1.4)
    top = int(y + 30); bot = H - 130; src = load(c["img"])
    cx, cy = W / 2, (top + bot) / 2; R = min(W - 2 * M, bot - top) / 2
    disc = Image.new("L", (W, H), 0); ImageDraw.Draw(disc).ellipse([cx - R, cy - R, cx + R, cy + R], fill=255)
    base.paste(Image.new("RGBA", (W, H), (255, 255, 255, 255)), (0, 0), disc.point(lambda v: v * 0.55).filter(ImageFilter.GaussianBlur(4)))
    ImageDraw.Draw(base).ellipse([cx - R, cy - R, cx + R, cy + R], outline=(255, 255, 255), width=3)
    cut, pk = product_cut(src, (255, 255, 255), int(R * 1.5), int((bot - top) * 0.92))
    if pk:
        px = int(cx - cut.width / 2); py = int(cy - cut.height / 2)
        soft_shadow(base, (cx - cut.width * 0.35, py, cx + cut.width * 0.35, py + cut.height), 60, 20)
        reg = base.crop((px, py, px + cut.width, py + cut.height)).convert("RGB"); base.paste(multiply_on(reg, cut), (px, py))
    else:
        framed_photo(base, src, (int(cx - R * 0.8), int(cy - R * 0.8), int(cx + R * 0.8), int(cy + R * 0.8)), angle=-3)
    calls = c.get("callouts", [])
    for i, txt in enumerate(calls):
        left = i % 2 == 0; f2 = SB(28); tw = ImageDraw.Draw(base).textlength(txt, font=f2); w = tw + 100
        span_end = bot - (300 if c.get("price") else 160)
        yy = top + 50 + (span_end - top - 50) * (i // 2) / max(1, (len(calls) - 1) // 2)
        x = M - 20 if left else W - M + 20 - w
        glass(base, (x, yy, x + w, yy + 70), 35, (255, 255, 255), 185)
        d = ImageDraw.Draw(base); icon_disc(d, icon_for(txt), x + 36, yy + 35, 23, FOREST, LIME)
        d.text((x + 70, yy + 35 - f2.size * 0.62), txt, font=f2, fill=INKV)
    if c.get("price"): sticker_v4(base, c["price"], W - M - 80, bot - 90, r=100, angle=8)
    if not calls: sparkle(base, cx + R * 0.72, cy - R * 0.72, 28, FOREST); sparkle(base, cx - R * 0.8, cy + R * 0.55, 15, FOREST)
    chrome(base, c, INKV, GREYV, light_btn=False)
    return base.convert("RGB")

def tb_list(c):
    n = c.get("_n", 0); base = mesh_bg(["sand", "fresh"][n % 2], n)
    framed_photo(base, load(c["img"]), (W - M - 300, 80, W - M, 430), angle=5)
    y = b_title_block(base, c, False, maxw=W - 2 * M - 330, start=80, maxlines=3, y=150)
    y = max(y + 20, 490); items = c["items"]; k = len(items)
    avail = H - 120 - y; gap = 20; ch = min((avail - gap * (k - 1)) / k, 200)
    for i, (a_, b_) in enumerate(items):
        glass(base, (M - 20, y, W - M + 20, y + ch), 30, (255, 255, 255), 170)
        d = ImageDraw.Draw(base)
        num = f"{c.get('start', 1) + i:02d}"
        d.text((M + 6, y + ch / 2 - 44), num, font=BLACK(62), fill=FOREST)
        fa = 36 if k <= 3 else 32; fb = 27 if k <= 3 else 25; mw = W - 2 * M - 220
        la = wrap(a_, DB(fa), mw); lb = wrap(b_, IR(fb), mw) if b_ else []
        th = fa * 1.15 * len(la) + (6 + fb * 1.3 * len(lb) if lb else 0)
        ty = draw_lines(d, M + 120, y + (ch - th) / 2, la, DB(fa), INKV, 1.15)
        if lb: draw_lines(d, M + 120, ty + 6, lb, IR(fb), GREYV, 1.3)
        icon_disc(d, icon_for(a_, b_), W - M - 30, y + ch / 2, 30, FOREST, LIME)
        y += ch + gap
    if c.get("stamp"):
        st = Image.new("RGBA", (330, 120), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        sd.rounded_rectangle([4, 4, 326, 116], radius=20, outline=CORAL, width=8)
        fs = BLACK(66); tw = sd.textlength(c["stamp"], font=fs); sd.text(((330 - tw) / 2, 16), c["stamp"], font=fs, fill=CORAL)
        st = st.rotate(10, resample=Image.BICUBIC, expand=True); base.alpha_composite(st, (W - M - 330, 360))
    chrome(base, c, INKV, GREYV, light_btn=False)
    return base.convert("RGB")

def tb_stats(c):
    n = c.get("_n", 0); base = mesh_bg("forest", n)
    y = b_title_block(base, dict(c, kicker=None), True, start=90, maxlines=2, y=100)
    framed_photo(base, load(c["img"]), (M + 20, int(y + 10), W - M - 20, int(y + 330)), angle=-2, border=12)
    y = int(y + 380); g = 22; tw_ = (W - 2 * M - g) // 2; th = (H - 120 - y - g) // 2
    for i, (big, small) in enumerate(c["items"]):
        x = M + (i % 2) * (tw_ + g); yy = y + (i // 2) * (th + g)
        glass(base, (x, yy, x + tw_, yy + th), 32, (255, 255, 255), 28, 70)
        d = ImageDraw.Draw(base)
        fb_ = BLACK(100)
        while d.textlength(nb(big), font=fb_) > tw_ - 120: fb_ = BLACK(fb_.size - 6)
        d.text((x + 30, yy + 24), nb(big), font=fb_, fill=LIME)
        icon_disc(d, icon_for(big, small), x + tw_ - 50, yy + 50, 28, LIME, FOREST)
        ls = wrap(small, IM(28), tw_ - 64)
        draw_lines(d, x + 32, yy + th - 34 - 28 * 1.3 * len(ls), ls, IM(28), CREAM, 1.3)
        d.rounded_rectangle([x + 30, yy + th - 22, x + tw_ - 30, yy + th - 14], radius=4, fill=(255, 255, 255, 50))
        d.rounded_rectangle([x + 30, yy + th - 22, x + 30 + (tw_ - 60) * [0.92, 0.7, 0.85, 0.6][i % 4], yy + th - 14], radius=4, fill=LIME)
    chrome(base, c, CREAM, GREYV, light_btn=True)
    return base.convert("RGB")

def tb_versus(c):
    base = Image.new("RGBA", (W, H), SANDV + (255,))
    right = mesh_bg("forest", 1); base.paste(right.crop((W // 2, 0, W, H)), (W // 2, 0))
    left = mesh_bg("sand", 0); base.paste(left.crop((0, 0, W // 2, H)), (0, 0))
    d = ImageDraw.Draw(base)
    if c.get("kicker"): kicker_pill(base, 0, 90, c["kicker"], LIME, INKV, center=True)
    f, tl = sans_fit(clean(c["title"]), BLACK, W - 2 * M, 84, 52, 2)
    y = 170
    for ln in tl:
        txt = " ".join(t[0] for t in ln).replace("  ", " "); tw = d.textlength(txt, font=f)
        # moitié gauche en vert foncé, moitié droite en crème
        t_img = Image.new("RGBA", (W, f.size + 30), (0, 0, 0, 0)); ImageDraw.Draw(t_img).text(((W - tw) / 2, 0), txt, font=f, fill=INKV)
        t2 = Image.new("RGBA", (W, f.size + 30), (0, 0, 0, 0)); ImageDraw.Draw(t2).text(((W - tw) / 2, 0), txt, font=f, fill=CREAM)
        base.alpha_composite(t_img.crop((0, 0, W // 2, t_img.height)), (0, int(y))); base.alpha_composite(t2.crop((W // 2, 0, W, t2.height)), (W // 2, int(y)))
        y += f.size * 1.04
    y = int(y + 60); fi = SB(40)
    for side, (head, items) in enumerate([c["left"], c["right"]]):
        x = M - 10 if side == 0 else W // 2 + 60; cw = W // 2 - M - 60; good = side == 1 or c.get("both_good")
        fg = INKV if side == 0 else CREAM
        hf = BLACK(60)
        while d.textlength(head, font=hf) > cw - 10: hf = BLACK(hf.size - 4)
        d.text((x, y), head, font=hf, fill=fg); squiggle(d, x, x + d.textlength(head, font=hf), y + hf.size * 1.12, FOREST if side == 0 else LIME)
        iy = y + hf.size + 70
        for it in items:
            icon_disc(d, "check" if good else "xmark", x + 26, iy + 24, 26, (LIME if side else (FOREST if good else CORAL)), (INKV if side else WHITE_A))
            iy = draw_lines(d, x + 70, iy, wrap(it, fi, cw - 70), fi, fg, 1.22) + 46
    vy = y + (H - 140 - y) * 0.42; d.ellipse([W / 2 - 52, vy - 52, W / 2 + 52, vy + 52], fill=LIME, outline=INKV, width=5)
    fv = BLACK(44); tw = d.textlength("VS", font=fv); d.text((W / 2 - tw / 2, vy - 29), "VS", font=fv, fill=INKV)
    chrome(base, c, INKV, GREYV, light_btn=True)
    return base.convert("RGB")

TPL_B = {"hero": tb_hero, "statement": tb_statement, "product": tb_product, "list": tb_list, "stats": tb_stats, "versus": tb_versus}
# ───────────────────────────── DA C : « Carnet & tchat » (3e DA)
# Formats natifs : conversation, note cochée, polaroids scotchés, post-it, annotations manuscrites.
PAPER = (250, 246, 238); DOTC = (222, 214, 198); TAPE = (238, 214, 160, 175)
POSTITS = [(232, 246, 178), (247, 222, 176), (214, 236, 222), (250, 216, 204)]
def HAND(s): return F("Caveat-Bold.ttf", s)

def paper_bg(seed=0):
    base = Image.new("RGBA", (W, H), PAPER + (255,)); d = ImageDraw.Draw(base)
    for yy in range(36, H, 40):
        for xx in range(20 + (seed % 2) * 20, W, 40): d.ellipse([xx - 2, yy - 2, xx + 2, yy + 2], fill=DOTC)
    return grain(base, 3)

def paste_rot(base, layer, cx, cy, angle, shadow=90):
    pad = 70; big = Image.new("RGBA", (layer.width + 2 * pad, layer.height + 2 * pad), (0, 0, 0, 0))
    if shadow:
        a = layer.split()[3].point(lambda v: shadow if v > 0 else 0)
        sh = Image.new("RGBA", layer.size, (20, 30, 24, 0)); sh.putalpha(a)
        big.alpha_composite(sh, (pad + 8, pad + 20)); big = big.filter(ImageFilter.GaussianBlur(18))
    big.alpha_composite(layer, (pad, pad))
    big = big.rotate(angle, resample=Image.BICUBIC, expand=True)
    base.alpha_composite(big, (int(cx - big.width / 2), int(cy - big.height / 2)))

def tape(base, cx, cy, w=170, angle=-6):
    t = Image.new("RGBA", (w, 50), TAPE); td = ImageDraw.Draw(t)
    for i in range(0, 50, 10):   # bords déchirés
        td.polygon([(0, i), (6, i + 5), (0, i + 10)], fill=(0, 0, 0, 0)); td.polygon([(w, i), (w - 6, i + 5), (w, i + 10)], fill=(0, 0, 0, 0))
    paste_rot(base, t, cx, cy, angle, shadow=0)

def marker_title(base, x, y, lines, fnt, fill=None, mark=LIME, lh=1.04, center_w=None):
    """Titre ; les *mots* sont passés au surligneur (trait irrégulier, légèrement penché)."""
    fill = fill or INKV; d = ImageDraw.Draw(base); sp = d.textlength(" ", font=fnt); yy = y
    for ln in lines:
        lw = sum(t[2] for t in ln) + sp * sum(1 for t in ln[1:] if not t[3])
        xx = x + ((center_w - lw) / 2 if center_w else 0); pos = []
        for w, hl, ww, glue in ln:
            if glue: xx -= sp
            pos.append((w, hl, ww, xx)); xx += ww + sp
        run = None
        for w, hl, ww, px in pos + [("", False, 0, 0)]:
            if hl and run is None: run = [px, px + ww]
            elif hl: run[1] = px + ww
            elif run is not None:
                ov = Image.new("RGBA", base.size, (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
                t0, t1 = yy + fnt.size * 0.42, yy + fnt.size * 1.08
                od.polygon([(run[0] - 14, t0 + 6), (run[1] + 12, t0 - 4), (run[1] + 18, t1 - 6), (run[0] - 8, t1 + 4)], fill=mark + (235,))
                base.alpha_composite(ov); run = None
        d = ImageDraw.Draw(base)
        for w, hl, ww, px in pos: d.text((px, yy), w, font=fnt, fill=fill)
        yy += fnt.size * lh
    return yy + fnt.size * 0.14

def hand_note(base, x, y, text, size=52, color=CORAL, angle=-3, maxw=W - 2 * M, center=False):
    f = HAND(size); lines = wrap(clean(text), f, maxw)
    w = int(max(ImageDraw.Draw(base).textlength(l, font=f) for l in lines)) + 20; h = int(f.size * 1.05 * len(lines)) + 24
    lay = Image.new("RGBA", (w, h), (0, 0, 0, 0)); draw_lines(ImageDraw.Draw(lay), 10, 4, lines, f, color, 1.05)
    lay = lay.rotate(angle, resample=Image.BICUBIC, expand=True)
    if center: x = (W - lay.width) / 2
    base.alpha_composite(lay, (int(x), int(y))); return y + lay.height, x + lay.width

def c_title(base, c, x=M, y=100, maxw=W - 2 * M, start=100, maxlines=3, kicker=True, center=False):
    if kicker and c.get("kicker"): y, _ = hand_note(base, x, y, c["kicker"], 54, CORAL, -2, maxw, center); y += 6
    f, tl = sans_fit(c["title"], BLACK, maxw, start, 56, maxlines)
    return marker_title(base, x, y, tl, f, center_w=maxw if center else None)

def polaroid(src, w, h, caption=None, fy=0.5):
    cap_lines = wrap(clean(caption), HAND(46), w - 60) if caption else []
    bottom = 40 + (int(46 * 1.0 * len(cap_lines)) + 36 if cap_lines else 50)
    im = src
    if (border_px(im).min(axis=1) > 238).mean() > 0.5:
        ww, hh = im.size; k = 0.66; im = im.crop((int(ww * (1 - k) / 2), int(hh * (1 - k) / 2), int(ww * (1 + k) / 2), int(hh * (1 + k) / 2)))
    lay = Image.new("RGBA", (w, h), (255, 255, 255, 255)); ph_h = h - 28 - bottom
    lay.paste(cover(im, w - 56, max(ph_h, 50), 0.5, fy), (28, 28))
    if cap_lines: draw_lines(ImageDraw.Draw(lay), 30, h - bottom + 14, cap_lines, HAND(46), INKV, 1.0)
    return lay

def bubble(base, x, y, w, h, fill, tail="left", r=40):
    d = ImageDraw.Draw(base); soft = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(soft).rounded_rectangle([x + 4, y + 10, x + w + 4, y + h + 10], radius=r, fill=(20, 30, 24, 40))
    base.alpha_composite(soft.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(base)
    d.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill)
    if tail == "left": d.polygon([(x + 6, y + h - 40), (x - 16, y + h + 2), (x + 44, y + h - 6)], fill=fill)
    else: d.polygon([(x + w - 6, y + h - 40), (x + w + 16, y + h + 2), (x + w - 44, y + h - 6)], fill=fill)

def hand_check(d, cx, cy, s, color, ok=True, width=7):
    if ok: d.line([(cx - s, cy), (cx - s * 0.3, cy + s * 0.7), (cx + s, cy - s * 0.8)], fill=color, width=width, joint="curve")
    else:
        d.line([(cx - s * 0.8, cy - s * 0.8), (cx + s * 0.8, cy + s * 0.8)], fill=color, width=width)
        d.line([(cx + s * 0.8, cy - s * 0.8), (cx - s * 0.8, cy + s * 0.8)], fill=color, width=width)

def doodle_star(d, cx, cy, r, color, width=5):
    pts = [(cx + (r if i % 2 == 0 else r * 0.45) * math.cos(-math.pi / 2 + i * math.pi / 5), cy + (r if i % 2 == 0 else r * 0.45) * math.sin(-math.pi / 2 + i * math.pi / 5)) for i in range(11)]
    d.line(pts, fill=color, width=width, joint="curve")

def tc_hero(c):
    src = load(c["img"])
    if prep(src)[1]: return tc_product(c)
    n = c.get("_n", 0); base = paper_bg(n)
    y = c_title(base, c, start=96, maxlines=3)
    top = int(y + 50); bot = H - 110; ang = 3 if n % 2 else -3
    w = W - 2 * M - 40; h = bot - top
    paste_rot(base, polaroid(src, w, h, c.get("sub"), c.get("fy", 0.45)), W / 2, (top + bot) / 2, ang)
    tape(base, W / 2, top + 4, 190, -4 if n % 2 else 5)
    d = ImageDraw.Draw(base)
    doodle_star(d, W - M + 10, top - 6, 30, CORAL); sparkle(base, M - 20, bot - 60, 22, FOREST)
    if c.get("price"): sticker_v4(base, c["price"], W - M - 50, top + 90, r=96, bg=CORAL, fg=WHITE_A)
    chrome(base, c, INKV, GREYV, light_btn=False)
    return base.convert("RGB")

def tc_statement(c):
    n = c.get("_n", 0); base = paper_bg(n); d = ImageDraw.Draw(base)
    # en-tête de conversation
    d.ellipse([M - 10, 70, M + 80, 160], fill=FOREST); draw_icon(d, "tooth", M + 35, 115, 40, LIME)
    d.text((M + 104, 78), "Pulse Care", font=DB(36), fill=INKV)
    d.ellipse([M + 106, 136, M + 120, 150], fill=(70, 190, 110)); d.text((M + 130, 126), "en ligne", font=IR(24), fill=GREYV)
    d.line([(0, 190), (W, 190)], fill=(230, 222, 208), width=2)
    y = 230
    if c.get("kicker"):
        f = SB(22); t = clean(c["kicker"]).upper(); tw = d.textlength(t, font=f)
        d.rounded_rectangle([(W - tw) / 2 - 22, y, (W + tw) / 2 + 22, y + 46], radius=23, fill=(236, 229, 214)); d.text(((W - tw) / 2, y + 10), t, font=f, fill=GREYV)
        y += 80
    bw = W - 2 * M - 60
    f, tl = sans_fit(c["title"], BLACK, bw - 80, 70, 46, 4)
    th = f.size * 1.06 * len(tl) + 70
    sub = c.get("sub") or ""; opts = [l for l in sub.split("\n") if re.match(r"^[A-D]\. ", l)]
    fs = IM(32); sl = wrap(sub, fs, bw - 80) if sub and not opts else []
    sh = fs.size * 1.32 * len(sl) + 60 if sl else 0
    oh = len(opts) * 92 if opts else 0
    swipe_h = 110 if c.get("swipe") else 0
    free = H - 120 - y - th - (sh + 30 if sh else 0) - (oh + 20 if oh else 0) - swipe_h - 30
    ph = min(int(free), 600) if free > 230 else 0
    bubble(base, M - 10, y, bw, th, WHITE_A, "left")
    marker_title(base, M + 30, y + 32, tl, f)
    d = ImageDraw.Draw(base); d.ellipse([M - 10 + bw - 40, y + th - 26, M - 10 + bw + 20, y + th + 34], fill=WHITE_A, outline=(230, 222, 208), width=2)
    draw_icon(d, "heart", M + bw - 20, y + th + 4, 28, CORAL)
    y += th + 40
    if ph:
        pw = int(min(bw * 0.86, ph * 1.3)); mk = Image.new("L", (pw, ph), 0); ImageDraw.Draw(mk).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=36, fill=255)
        im = cover(load(c["img"]), pw, ph, 0.5, c.get("fy", 0.45)); base.paste(im, (M - 10, int(y)), mk); y += ph + 30
    if sl:
        bubble(base, M - 10, y, min(bw, max(d.textlength(l, font=fs) for l in sl) + 80), sh, WHITE_A, "left")
        draw_lines(ImageDraw.Draw(base), M + 30, y + 28, sl, fs, INKV, 1.32); y += sh + 30
    for o in opts:   # réponses rapides, côté utilisateur
        d = ImageDraw.Draw(base); fo = SB(32); tw = d.textlength(o, font=fo); x1 = W - M + 10; x0 = x1 - tw - 64
        d.rounded_rectangle([x0, y, x1, y + 72], radius=36, fill=FOREST); d.text((x0 + 32, y + 16), o, font=fo, fill=CREAM); y += 92
    if c.get("swipe"):
        y += 10; bubble(base, M - 10, y, 150, 74, WHITE_A, "left", 37); d = ImageDraw.Draw(base)
        for i in range(3): d.ellipse([M + 25 + i * 34, y + 28, M + 43 + i * 34, y + 46], fill=(170, 180, 172) if i else GREYV)
    chrome(base, c, INKV, GREYV, light_btn=False)
    return base.convert("RGB")

def tc_list(c):
    n = c.get("_n", 0); base = paper_bg(n)
    card = (M - 40, 150, W - M + 40, H - 90)
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([card[0] + 6, card[1] + 18, card[2] + 6, card[3] + 18], radius=40, fill=(20, 30, 24, 55))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20))); d = ImageDraw.Draw(base)
    d.rounded_rectangle(card, radius=40, fill=WHITE_A)
    for i in range(6): d.ellipse([card[0] + 70 + i * 40 - 7, card[1] + 34, card[0] + 70 + i * 40 + 7, card[1] + 48], fill=(236, 229, 214) if i else CORAL)
    paste_rot(base, polaroid(load(c["img"]), 280, 320), W - M - 110, 230, 7)
    tape(base, W - M - 110, 76, 130, -8)
    y = c_title(base, c, x=M, y=210, maxw=W - 2 * M - 300, start=78, maxlines=3)
    y = max(y + 20, 470); items = c["items"]; k = len(items)
    avail = card[3] - 60 - y; ch = min(avail / k, 250); y += (avail - ch * k) / 2; d = ImageDraw.Draw(base)
    for i, (a_, b_) in enumerate(items):
        cy = y + ch / 2
        d.rounded_rectangle([M, cy - 26 - 8, M + 52, cy + 26 - 8], radius=14, fill=FOREST)
        hand_check(d, M + 26, cy - 8, 14, LIME, True, 6)
        fa = 44 if k <= 3 else 38; fb = 31 if k <= 3 else 28; mw = W - 2 * M - 110
        la = wrap(a_, DB(fa), mw); lb = wrap(b_, IR(fb), mw) if b_ else []
        th = fa * 1.15 * len(la) + (6 + fb * 1.3 * len(lb) if lb else 0)
        ty = draw_lines(d, M + 86, cy - th / 2 - 8, la, DB(fa), INKV, 1.15)
        if lb: draw_lines(d, M + 86, ty + 6, lb, IR(fb), GREYV, 1.3)
        if i < k - 1:
            for xx in range(M, W - M, 22): d.line([(xx, y + ch), (xx + 10, y + ch)], fill=(225, 216, 200), width=3)
        y += ch
    if c.get("stamp"):
        st = Image.new("RGBA", (330, 120), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        sd.rounded_rectangle([4, 4, 326, 116], radius=20, outline=CORAL, width=8)
        fs = BLACK(66); tw = sd.textlength(c["stamp"], font=fs); sd.text(((330 - tw) / 2, 16), c["stamp"], font=fs, fill=CORAL)
        st = st.rotate(-9, resample=Image.BICUBIC, expand=True); base.alpha_composite(st, (W - M - 360, 400))
    chrome(base, c, INKV, GREYV, light_btn=False)
    return base.convert("RGB")

def tc_product(c):
    n = c.get("_n", 0); base = paper_bg(n + 1)
    y = c_title(base, c, start=92, maxlines=2)
    if c.get("sub"): y = draw_lines(ImageDraw.Draw(base), M, y + 4, wrap(c["sub"], IM(30), W - 2 * M - 60), IM(30), GREYV, 1.4)
    top = int(y + 40); bot = H - 110; src = load(c["img"]); calls = c.get("callouts", [])
    pw = 430 if calls else W - 2 * M - 40; cx = W / 2 + (40 if calls else 0); cy = (top + bot) / 2
    # tache de couleur organique derrière le produit
    blob = Image.new("L", (W, H), 0); bd = ImageDraw.Draw(blob); R = min(pw * 0.62, (bot - top) * 0.48)
    pts = [(cx + R * (1 + 0.07 * math.sin(3 * a + n)) * math.cos(a), cy + R * (1 + 0.07 * math.cos(2 * a + n)) * math.sin(a)) for a in [i * math.pi / 60 for i in range(120)]]
    bd.polygon(pts, fill=255); base.paste(Image.new("RGBA", (W, H), (226, 243, 170, 255)), (0, 0), blob)
    cut, pk = product_cut(src, (255, 255, 255), int(pw), int((bot - top) * 0.9))
    if pk:
        px = int(cx - cut.width / 2); py = int(cy - cut.height / 2)
        soft_shadow(base, (cx - cut.width * 0.32, py, cx + cut.width * 0.32, py + cut.height), 55, 20)
        reg = base.crop((px, py, px + cut.width, py + cut.height)).convert("RGB"); base.paste(multiply_on(reg, cut), (px, py)); pbox = (px, py, px + cut.width, py + cut.height)
    else:
        ww = int(min(pw, (bot - top) * 0.8)); hh = int(ww * 1.12)
        paste_rot(base, polaroid(src, ww, hh), cx, cy, -3); tape(base, cx, cy - hh / 2 + 4, 150, 4)
        pbox = (cx - ww / 2, cy - hh / 2, cx + ww / 2, cy + hh / 2)
    for i, txt in enumerate(calls):   # annotations manuscrites + flèches
        k = len(calls); ty = top + 30 + (bot - top - 160) * i / max(1, k - 1)
        ye, xe = hand_note(base, M - 40, ty, txt, 44, FOREST, -2, 300)
        doodle_arrow(base, (xe + 14, ty + 34), (pbox[0] + (pbox[2] - pbox[0]) * 0.28, min(max(ty + 40, pbox[1] + 60), pbox[3] - 60)), FOREST, 0.18 * (1 if i % 2 else -1), 5)
    if c.get("price"): sticker_v4(base, c["price"], W - M - 50, bot - 70, r=100, bg=CORAL, fg=WHITE_A, angle=8)
    if not calls: doodle_star(ImageDraw.Draw(base), cx + R * 0.85, cy - R * 0.8, 30, CORAL)
    chrome(base, c, INKV, GREYV, light_btn=False)
    return base.convert("RGB")

def tc_stats(c):
    n = c.get("_n", 0); base = paper_bg(n)
    y = c_title(base, dict(c, kicker=c.get("kicker") or "en bref"), start=92, maxlines=2)
    y = int(y + 50); g = 40; tw_ = (W - 2 * M - g) // 2; th = (H - 110 - y - g) // 2
    for i, (big, small) in enumerate(c["items"]):
        lay = Image.new("RGBA", (tw_, th), POSTITS[i % 4] + (255,)); d = ImageDraw.Draw(lay)
        d.polygon([(tw_ - 50, th), (tw_, th - 50), (tw_, th)], fill=tuple(int(v * 0.9) for v in POSTITS[i % 4]) + (255,))
        fb_ = BLACK(132)
        while d.textlength(nb(big), font=fb_) > tw_ - 60: fb_ = BLACK(fb_.size - 6)
        d.text((30, 40), nb(big), font=fb_, fill=INKV)
        ls = wrap(small, HAND(50), tw_ - 60); draw_lines(d, 30, th - 34 - 50 * 1.0 * len(ls), ls, HAND(50), FOREST, 1.0)
        cxp = M + (i % 2) * (tw_ + g) + tw_ / 2; cyp = y + (i // 2) * (th + g) + th / 2
        paste_rot(base, lay, cxp, cyp, [-2.5, 2, 1.5, -2][i % 4], 60)
        tape(base, cxp, cyp - th / 2 + 2, 120, [5, -6, -4, 6][i % 4])
    chrome(base, c, INKV, GREYV, light_btn=False)
    return base.convert("RGB")

def tc_versus(c):
    base = paper_bg(1)
    y = c_title(base, c, start=84, maxlines=2, center=True)
    y = int(y + 70); g = 34; cw = (W - 2 * M + 60 - g) // 2; fi = SB(38)
    def items_h(items): return sum(fi.size * 1.22 * len(wrap(it, fi, cw - 120)) + 44 for it in items)
    chh = int(min(H - 110 - y, max(0.82 * (H - 110 - y), 200 + max(items_h(c["left"][1]), items_h(c["right"][1])) + 30)))
    y = int(y + (H - 110 - y - chh) * 0.5)
    for side, (head, items) in enumerate([c["left"], c["right"]]):
        good = side == 1 or c.get("both_good"); bg = WHITE_A if side == 0 else FOREST; fg = INKV if side == 0 else CREAM
        lay = Image.new("RGBA", (cw, chh), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        d.rounded_rectangle([0, 0, cw - 1, chh - 1], radius=30, fill=bg)
        for yy in range(170, chh - 30, 70): d.line([(28, yy), (cw - 28, yy)], fill=(236, 229, 216) if side == 0 else (36, 68, 53), width=2)
        hf = BLACK(60)
        while d.textlength(head, font=hf) > cw - 70: hf = BLACK(hf.size - 4)
        d.text((34, 56), head, font=hf, fill=fg)
        squiggle(d, 34, 34 + d.textlength(head, font=hf), 56 + hf.size * 1.15, CORAL if side == 0 else LIME)
        iy = 190
        for it in items:
            hand_check(d, 56, iy + 24, 17, (FOREST if good else CORAL) if side == 0 else LIME, good, 7)
            iy = draw_lines(d, 98, iy, wrap(it, fi, cw - 120), fi, fg, 1.22) + 44
        cx_ = M - 30 + cw / 2 if side == 0 else W - M + 30 - cw / 2
        paste_rot(base, lay, cx_, y + chh / 2, -1.5 if side == 0 else 1.5, 70)
    tape(base, M + 110, y + 2, 140, -10); tape(base, W - M - 110, y + 2, 140, 9)
    d = ImageDraw.Draw(base); vy = y + 4
    d.ellipse([W / 2 - 60, vy - 56, W / 2 + 60, vy + 56], fill=CORAL, outline=PAPER, width=6)
    fv = HAND(80); tw = d.textlength("vs", font=fv); d.text((W / 2 - tw / 2, vy - 52), "vs", font=fv, fill=WHITE_A)
    chrome(base, c, INKV, GREYV, light_btn=False)
    return base.convert("RGB")

TPL_C = {"hero": tc_hero, "statement": tc_statement, "product": tc_product, "list": tc_list, "stats": tc_stats, "versus": tc_versus}

SLOT_DA_10H = "b"                   # 10h en DA B « Gradient & verre », 18h en DA v5
DA_B_ALL = "--da-b" in sys.argv     # aperçu : tout en DA B
DA_C_ALL = "--da-c" in sys.argv     # aperçu : tout en DA C
def pick_tpl(sl):
    if DA_C_ALL or sl.get("da") == "c": return TPL_C[sl["tpl"]]
    return (TPL_B if (DA_B_ALL or sl.get("da") == "b") else TPL)[sl["tpl"]]

# ───────────────────────────── Reels 1080x1920
RW, RH, FPS, XF = 1080, 1920, 30, 0.4

def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ease_io(x): x = min(max(x, 0), 1); return 3 * x * x - 2 * x * x * x

class Layer:
    """Élément pré-rendu (RGBA), animé en opacité / translation."""
    def __init__(self, im, x, y, t0, dur=0.55, dx=0, dy=60):
        self.im, self.x, self.y, self.t0, self.dur, self.dx, self.dy = im, x, y, t0, dur, dx, dy
        self.arr = np.array(im)
    def draw(self, frame, t):
        p = ease((t - self.t0) / self.dur)
        if p <= 0: return
        a = self.arr.copy(); a[..., 3] = (a[..., 3] * p).astype(np.uint8)
        frame.alpha_composite(Image.fromarray(a, "RGBA"), (int(self.x + self.dx * (1 - p)), int(self.y + self.dy * (1 - p))))

def text_layer(lines, fnt, fill, lh=1.15, w=RW - 140, center=False):
    h = int(text_h(lines, fnt, lh) + fnt.size * 0.4)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    y = 0
    for l in lines:
        x = (w - d.textlength(l, font=fnt)) / 2 if center else 0
        d.text((x, y), l, font=fnt, fill=fill); y += fnt.size * lh
    return im

def pill_layer(text, fnt, bg, fg):
    d = ImageDraw.Draw(Image.new("L", (1, 1))); tw = d.textlength(text, font=fnt)
    im = Image.new("RGBA", (int(tw + 48), fnt.size + 24), (0, 0, 0, 0))
    pill(ImageDraw.Draw(im), 0, 0, text, fnt, bg, fg, 24, 12)
    return im

class KenBurns:
    def __init__(self, ref, w, h, zoom=(1.0, 1.1), pan=(0.0, 0.0)):
        self.src = cover(load(ref), int(w * 1.16), int(h * 1.16))
        self.w, self.h, self.zoom, self.pan = w, h, zoom, pan
    def at(self, p):
        z = self.zoom[0] + (self.zoom[1] - self.zoom[0]) * p
        cw, ch = self.src.width / (1.16 * z) * 1.0, self.src.height / (1.16 * z)
        cx = self.src.width / 2 + self.pan[0] * (self.src.width - cw) / 2 * (p * 2 - 1)
        cy = self.src.height / 2 + self.pan[1] * (self.src.height - ch) / 2 * (p * 2 - 1)
        box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
        return self.src.resize((self.w, self.h), Image.BILINEAR, box=box)

def brand_top(frame, fg=CREAM):
    wordmark(ImageDraw.Draw(frame), 70, 90, fg, 34)

class Scene:
    def __init__(self, c, idx):
        self.c, self.dur, self.idx = c, c["dur"], idx
        getattr(self, "setup_" + c["t"])()
    # photo plein cadre + textes en bas
    def setup_photo(self):
        c = self.c
        self.kb = KenBurns(c["img"], RW, RH, (1.0, 1.12), ((-1) ** self.idx * 0.4, 0.2))
        self.grad = gradient(RW, RH, DEEP, 0.38, 0.95, 0, 240)
        self.grad.alpha_composite(gradient(RW, 300, DEEP, 0, 1, 130, 0), (0, 0))
        tf = fit(c["title"], BOLD, RW - 140, 104, 64, 4)
        tl = wrap(c["title"], tf, RW - 140)
        sl = wrap(c["sub"], REG(42), RW - 140) if c.get("sub") else []
        y = RH - 330 - text_h(sl, REG(42), 1.35) - (30 if sl else 0) - text_h(tl, tf)
        self.layers = []
        if c.get("kicker"):
            self.layers.append(Layer(pill_layer(c["kicker"].upper(), MED(30), BAMBOO, DEEP), 70, y - 100, 0.15, dx=-80, dy=0))
        for i, l in enumerate(tl):
            self.layers.append(Layer(text_layer([l], tf, CREAM), 70, y + i * tf.size * 1.15, 0.3 + i * 0.12))
        y += text_h(tl, tf)
        if sl: self.layers.append(Layer(text_layer(sl, REG(42), (226, 232, 226), 1.35), 70, y + 30, 0.75, dy=30))
    def frame_photo(self, t):
        f = self.kb.at(t / self.dur).convert("RGBA"); f.alpha_composite(self.grad); brand_top(f)
        for l in self.layers: l.draw(f, t)
        return f
    # moitié photo / moitié panneau
    def setup_split(self):
        c = self.c
        self.kb = KenBurns(c["img"], RW, 1060, (1.04, 1.14), (0.3, 0.0))
        self.top_grad = gradient(RW, 300, DEEP, 0, 1, 130, 0)
        self.layers = [Layer(pill_layer(c["kicker"].upper(), MED(30), GREEN, CREAM), 70, 1080, 0.35, dx=-60, dy=0)]
        y = 1190
        for i, (a, b) in enumerate(c["items"]):
            im = Image.new("RGBA", (RW - 140, 230), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            d.ellipse([0, 10, 60, 70], fill=BAMBOO); d.text((15, 14), "→", font=ARR(34), fill=DEEP)
            yy = draw_lines(d, 90, 0, wrap(a, BOLD(52), RW - 240), BOLD(52), GREEN, 1.12)
            if b: draw_lines(d, 90, yy + 4, wrap(b, REG(38), RW - 240), REG(38), (70, 92, 82), 1.3)
            self.layers.append(Layer(im, 70, y, 0.6 + i * 0.35, dx=80, dy=0)); y += 250
    def frame_split(self, t):
        f = Image.new("RGBA", (RW, RH), CREAM + (255,))
        f.paste(self.kb.at(t / self.dur), (0, 0)); f.alpha_composite(self.top_grad, (0, 0))
        p = ease(t / 0.55); top = int(RH - (RH - 1000) * p)
        ImageDraw.Draw(f).rounded_rectangle([0, top, RW, RH + 60], radius=60, fill=CREAM)
        brand_top(f)
        for l in self.layers: l.draw(f, t)
        return f
    # liste sur fond uni
    def setup_list(self):
        c = self.c; self.bg = MINT if c.get("theme") == "mint" else CREAM
        self.layers = [Layer(text_layer([c["kicker"].upper()], MED(34), BAMBOO), 70, 380, 0.1, dy=30)]
        y = 500
        for i, (a, b) in enumerate(c["items"]):
            im = Image.new("RGBA", (RW - 140, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            yy = draw_lines(d, 0, 0, wrap(a, BOLD(64), RW - 140), BOLD(64), GREEN, 1.1)
            if b: yy = draw_lines(d, 0, yy + 6, wrap(b, REG(42), RW - 140), REG(42), (70, 92, 82), 1.3)
            self.layers.append(Layer(im.crop((0, 0, RW - 140, int(yy) + 20)), 70, y, 0.35 + i * 0.55, dx=0, dy=50))
            y += yy + 90
    def frame_list(self, t):
        f = Image.new("RGBA", (RW, RH), self.bg + (255,)); d = ImageDraw.Draw(f)
        bar = int(1100 * ease(t / 0.8)); d.rectangle([0, 360, 18, 360 + bar], fill=BAMBOO)
        brand_top(f, GREEN)
        for l in self.layers: l.draw(f, t)
        return f
    # compteur animé
    def setup_counter(self):
        c = self.c
        self.layers = [Layer(text_layer([c["kicker"].upper()], MED(36), BAMBOO, center=True), 70, 500, 0.1, dy=30),
                       Layer(text_layer(wrap(c["label"], MED(50), RW - 160), MED(50), CREAM, center=True), 70, 1120, 1.2, dy=40)]
    def frame_counter(self, t):
        c = self.c
        f = Image.new("RGBA", (RW, RH), GREEN + (255,)); d = ImageDraw.Draw(f)
        for i in range(-6, 14):  # rayures bambou en mouvement
            x = i * 160 + (t * 40) % 160
            d.line([(x, 0), (x + 600, RH)], fill=(36, 66, 54), width=40)
        r = 300 + 60 * ease(t / 1.5)
        d.ellipse([RW / 2 - r, 960 - r, RW / 2 + r, 960 + r], outline=BAMBOO, width=5)
        v = int(round(c["value"] * ease(t / 1.6)))
        s = f"{v:,}".replace(",", " ") + c.get("suffix", "")
        fnt = BOLD(200 if len(s) < 7 else 170)
        tw = d.textlength(s, font=fnt); d.text(((RW - tw) / 2, 820), s, font=fnt, fill=CREAM)
        brand_top(f)
        for l in self.layers: l.draw(f, t)
        return f
    # minuteur circulaire
    def setup_timer(self):
        c = self.c
        self.layers = [Layer(text_layer([c["kicker"].upper()], MED(36), BAMBOO, center=True), 70, 420, 0.1, dy=30),
                       Layer(text_layer([nb(c["title"])], BOLD(110), CREAM, center=True), 70, 880, 0.3, dy=40),
                       Layer(text_layer(wrap(c["sub"], REG(42), RW - 200), REG(42), (226, 232, 226), 1.35, center=True), 70, 1450, 0.8, dy=30)]
    def frame_timer(self, t):
        f = Image.new("RGBA", (RW, RH), DEEP + (255,)); d = ImageDraw.Draw(f)
        cx, cy, r = RW / 2, 960, 360
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(46, 80, 66), width=26)
        p = ease_io(t / (self.dur - 0.3))
        d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * p, fill=BAMBOO, width=26)
        for q in range(4):
            a = math.radians(-90 + q * 90); on = p >= q / 4 + 0.001
            x, y = cx + r * math.cos(a), cy + r * math.sin(a)
            d.ellipse([x - 24, y - 24, x + 24, y + 24], fill=CREAM if on else (46, 80, 66))
        brand_top(f)
        for l in self.layers: l.draw(f, t)
        return f
    # comparatif 2 colonnes
    def setup_compare(self):
        c = self.c; cw = (RW - 170) // 2; self.layers = []
        for i, (head, rows) in enumerate([c["left"], c["right"]]):
            dark = i == 1
            im = Image.new("RGBA", (cw, 820), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            d.rounded_rectangle([0, 0, cw, 820], radius=44, fill=GREEN if dark else MINT)
            d.text((40, 50), head, font=BOLD(54), fill=BAMBOO if dark else GREEN)
            y = 180
            for r_ in rows:
                y = draw_lines(d, 40, y, wrap("• " + r_, REG(46), cw - 80), REG(46), CREAM if dark else GREEN, 1.3) + 40
            self.layers.append(Layer(im, 70 + i * (cw + 30), 600, 0.2 + i * 0.5, dx=(-120 if i == 0 else 120), dy=0))
        self.layers.append(Layer(text_layer(["Le comparatif"], BOLD(84), GREEN), 70, 420, 0.05, dy=30))
    def frame_compare(self, t):
        f = Image.new("RGBA", (RW, RH), CREAM + (255,)); brand_top(f, GREEN)
        for l in self.layers: l.draw(f, t)
        return f
    # carton de fin
    def setup_end(self):
        c = self.c
        tl = wrap(c["title"], BOLD(78), RW - 180)
        self.layers = [Layer(text_layer(tl, BOLD(78), CREAM, 1.15, RW - 180, True), 90, 820, 0.45, dy=40),
                       Layer(text_layer([c.get("sub", "")], MED(40), BAMBOO, center=True), 70, 820 + text_h(tl, BOLD(78)) + 70, 0.85, dy=20)]
    def frame_end(self, t):
        f = Image.new("RGBA", (RW, RH), GREEN + (255,)); d = ImageDraw.Draw(f)
        s = 0.9 + 0.1 * ease(t / 0.6)
        fnt = MED(int(64 * s)); tw = d.textlength("PULSE CARE", font=fnt)
        x = (RW - tw) / 2 + 30
        d.ellipse([x - 64 * s, 560 + 20 * s, x - 30 * s, 560 + 54 * s], fill=BAMBOO)
        d.text((x, 560), "PULSE CARE", font=fnt, fill=CREAM)
        ln = 180 * ease((t - 0.2) / 0.6); d.line([(RW / 2 - ln / 2, 690), (RW / 2 + ln / 2, 690)], fill=BAMBOO, width=5)
        for l in self.layers: l.draw(f, t)
        return f
    def frame(self, t):
        return getattr(self, "frame_" + self.c["t"])(t)

def render_reel(scenes_spec, out):
    scenes = [Scene(c, i) for i, c in enumerate(scenes_spec)]
    starts, t = [], 0.0
    for i, sc in enumerate(scenes):
        starts.append(t); t += sc.dur - (XF if i < len(scenes) - 1 else 0)
    total = t; n = int(total * FPS)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{RW}x{RH}", "-r", str(FPS), "-i", "-",
           "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-shortest",
           "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "21",
           "-maxrate", "4500k", "-bufsize", "9000k", "-g", "60", "-keyint_min", "60", "-sc_threshold", "0",
           "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(n):
        tt = k / FPS
        act = [i for i, s0 in enumerate(starts) if s0 <= tt < s0 + scenes[i].dur]
        i = act[-1]; fr = scenes[i].frame(tt - starts[i])
        if len(act) > 1:  # fondu enchaîné
            j = act[0]; a = ease_io((tt - starts[i]) / XF)
            fr = Image.blend(scenes[j].frame(tt - starts[j]).convert("RGB"), fr.convert("RGB"), a).convert("RGBA")
        d = ImageDraw.Draw(fr); d.rectangle([0, 0, int(RW * (k + 1) / n), 8], fill=BAMBOO)  # barre de progression
        p.stdin.write(fr.convert("RGB").tobytes())
    p.stdin.close(); p.wait()
    if p.returncode: raise RuntimeError("ffmpeg failed")
    # miniature pour l'aperçu
    Scene(scenes_spec[0], 0).frame(min(1.6, scenes_spec[0]["dur"] - 0.1)).convert("RGB").save(out.replace(".mp4", "-cover.jpg"), quality=88)
    return total

# ───────────────────────────── contrôles + export
FORBIDDEN = ["écologique", "éco-responsable", "biodégradable", "respectueux de l", "planète", "zéro déchet",
             "40 000", "massage",
             # marques concurrentes : jamais citées
             "oral-b", "oral b", "philips", "sonicare", "colgate", "sensodyne", "elmex", "parodontax", "signal ",
             "crest", "quip", "suri ", "hismile", "foreo", "waterpik", "listerine", "aquafresh", "fluocaril",
             "meridol", "curaprox", "panasonic", "xiaomi", "oclean", "happybrush", "spotlight", "brosse en bambou", "manche en bambou", "dupont", "tynex", " vous ", " vos ", "votre"]

def check():
    errs, used = [], Counter()
    for p in ALL:
        refs = [x["img"] for x in p.get("slides", []) + p.get("scenes", []) if x.get("img")]
        for r in refs: used[r] += 1
        cap = p["caption"].replace("[CTA]", CTA_IG)
        first = cap.split("\n")[0].lower()
        if not re.search(r"brosses? à dents électriques?", first): errs.append(p["date"] + " mot-clé 1re ligne")
        if len(re.findall(r"#\w+", cap)) > 5: errs.append(p["date"] + " >5 hashtags")
        for w in FORBIDDEN:
            if w in cap.lower() or any(w in json.dumps(x, ensure_ascii=False).lower() for x in p.get("slides", []) + p.get("scenes", [])):
                errs.append(f"{p['date']} mot interdit « {w.strip()} »")
        if p["kind"] == "carousel" and not 2 <= len(p["slides"]) <= 10: errs.append(p["date"] + " carrousel taille")
    errs += [f"visuel réutilisé : {k}" for k, v in used.items() if v > 1]
    return errs, used

def main():
    if "--fetch-only" in sys.argv:   # télécharge les photos sources (utile hors GitHub Actions)
        refs = sorted({x["img"] for p in ALL for x in p.get("slides", []) if x.get("img")})
        for r in refs: load(r)
        print(len(refs), "sources"); return
    errs, used = check()
    if errs:
        print("\n".join(errs)); sys.exit(1)
    print(f"Contrôles OK · {len(ALL)} posts · {len(used)} visuels sources uniques")
    for d_ in ("media/posts", "media/reels", "planning"): os.makedirs(os.path.join(ROOT, d_), exist_ok=True)
    gallery = []
    for suf, LIST, off in SLOTS:
      for p in LIST:
          if ONLY and p["date"] not in ONLY: continue
          date = p["date"] + suf; cap = p["caption"]
          if p["kind"] == "carousel" and "swipe" not in cap.lower():
              cap = cap.replace("[CTA]", "Swipe pour tout voir.\n\n[CTA]")
          ig = cap.replace("[CTA]", CTA_IG); fb = cap.replace("[CTA]", CTA_FB)
          if p["kind"] == "reel":
              rel = f"media/reels/{date}.mp4"; t0 = time.time()
              dur = render_reel(p["scenes"], os.path.join(ROOT, rel))
              print(f"{date} reel {dur:.1f}s ({time.time() - t0:.0f}s de rendu)")
              post = {"type": "reel", "video_url": PAGES + rel, "thumb_offset": 1600, "caption": ig, "fb_message": fb}
              gallery.append((date, "reel", [rel.replace(".mp4", "-cover.jpg")], rel, ig))
          else:
              rels = []
              for i, sl in enumerate(p["slides"], 1):
                  rel = f"media/posts/{date}-{i}.jpg"
                  sl = dict(sl, _n=LIST.index(p) + i - 1 + off)
                  if suf == "-10h" and not sl.get("da"): sl["da"] = SLOT_DA_10H
                  pick_tpl(sl)(sl).save(os.path.join(ROOT, rel), "JPEG", quality=90, optimize=True, progressive=False)
                  rels.append(rel)
              urls = [RAW + r for r in rels]
              print(f"{date} {p['kind']} {len(rels)} visuel(s)")
              if p["kind"] == "photo":
                  post = {"type": "photo", "image_url": urls[0]}
              else:
                  post = {"type": "carousel", "media": [{"media_type": "IMAGE", "image_url": u} for u in urls]}
              post.update({"caption": ig, "fb_message": fb, "fb_photos": [{"type": "url", "url": u} for u in urls]})
              gallery.append((date, p["kind"], rels, None, ig))
          json.dump({"post": post}, open(os.path.join(ROOT, "planning", date + ".json"), "w"), ensure_ascii=False, indent=2)
    if not ONLY: write_index(gallery)

def write_index(gallery):
    import html
    cards = []
    for date, kind, imgs, video, cap in gallery:
        media = (f'<video src="{video}" poster="{imgs[0]}" controls muted playsinline preload="none"></video>' if video
                 else "".join(f'<img src="{i}" loading="lazy" alt="">' for i in imgs))
        cards.append(f'<article><header><b>{date}</b><span class="k {kind}">{kind}</span></header><div class="m">{media}</div>'
                     f'<details><summary>Légende</summary><pre>{html.escape(cap)}</pre></details></article>')
    page = """<!doctype html><html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Pulse Care · planning</title><style>
body{margin:0;font-family:system-ui,sans-serif;background:#F3EEE4;color:#1E3A2F}h1{padding:24px 16px 0;margin:0}
p.s{padding:0 16px;color:#5a6b62}main{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px;padding:16px}
article{background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 2px 10px #0001}header{display:flex;justify-content:space-between;padding:10px 14px}
.k{font-size:12px;padding:2px 10px;border-radius:99px;background:#DDE8DF}.k.reel{background:#C49E62;color:#12241D}
.m{display:flex;overflow-x:auto;scroll-snap-type:x mandatory}.m img,.m video{width:100%;flex:none;scroll-snap-align:start;display:block}
details{padding:8px 14px}pre{white-space:pre-wrap;font:13px/1.45 system-ui}</style>
<h1>Pulse Care · 30 jours</h1><p class="s">Instagram + Facebook · publication automatique à 18h · glisse les carrousels horizontalement</p>
<main>""" + "".join(cards) + "</main></html>"
    open(os.path.join(ROOT, "index.html"), "w").write(page)

if __name__ == "__main__":
    main()
