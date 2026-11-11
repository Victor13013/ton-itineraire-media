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

# ───────────────────────────── garde-fou de lisibilité
# Chaque texte posé est comparé au fond réel juste en dessous (contraste WCAG).
# Fond uni : la couleur du texte est corrigée. Fond photo / vidéo : halo sombre ou clair derrière les lettres.
# Jamais de blanc sur blanc ni de noir sur noir. Chaque correction est notée dans media/audit-contraste.txt.
AUDIT, CTX = [], [""]

def _lum(a):
    a = np.asarray(a, dtype=np.float32) / 255.0
    a = np.where(a <= 0.03928, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
    return a[..., 0] * 0.2126 + a[..., 1] * 0.7152 + a[..., 2] * 0.0722

def _cr(a, b): return (np.maximum(a, b) + 0.05) / (np.minimum(a, b) + 0.05)

DARK_INK, LIGHT_INK = (18, 26, 22), (250, 247, 240)

def _diagnose(bg_rgb, ink):
    """bg_rgb : pixels du fond sous les lettres (N,3). Renvoie None si lisible, sinon ('flat'|'busy', encre conseillée)."""
    if len(bg_rgb) < 12: return None
    lb = _lum(bg_rgb); li = float(_lum(np.array(ink[:3], dtype=np.float32)[None])[0])
    crs = _cr(lb, li)
    if np.median(crs) >= 3.2 and (crs < 2.0).mean() < 0.15: return None
    mb = float(np.median(lb))
    target = DARK_INK if _cr(mb, float(_lum(np.array(DARK_INK, dtype=np.float32)[None])[0])) >= _cr(mb, float(_lum(np.array(LIGHT_INK, dtype=np.float32)[None])[0])) else LIGHT_INK
    return ("flat" if float(lb.std()) < 0.07 else "busy"), target

def _fix_ink(ink, target, mb):
    """Rapproche l'encre de la cible jusqu'à un contraste de 4,5 en gardant sa teinte."""
    for k in range(1, 11):
        c = tuple(int(ink[i] + (target[i] - ink[i]) * k / 10) for i in range(3))
        if _cr(mb, float(_lum(np.array(c, dtype=np.float32)[None])[0])) >= 4.5: return c
    return target

def _halo(dst, mask, pos, ink):
    """Ombre douce derrière les lettres, de la couleur opposée au texte."""
    pad = 22
    m = Image.new("L", (mask.width + 2 * pad, mask.height + 2 * pad), 0); m.paste(mask, (pad, pad))
    m = m.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(min(255, v * 0.85)))
    li = float(_lum(np.array(ink[:3], dtype=np.float32)[None])[0])
    col = (6, 12, 9) if li > 0.3 else (252, 250, 245)
    dst.paste(Image.new(dst.mode, m.size, col + ((255,) if dst.mode == "RGBA" else ())), (int(pos[0]) - pad, int(pos[1]) - pad), m)

def _region(dst, x, y, w, h):
    x0, y0 = max(0, int(x)), max(0, int(y)); x1, y1 = min(dst.width, int(x + w + 0.999)), min(dst.height, int(y + h + 0.999))
    return (x0, y0, x1, y1) if x1 > x0 and y1 > y0 else None

def safe_composite(dst, src, pos):
    """alpha_composite d'un calque texte, avec contrôle du contraste."""
    try:
        a = np.asarray(src); m = a[..., 3] > 150
        r = _region(dst, pos[0], pos[1], src.width, src.height)
        if r is not None and m.sum() > 12:
            sub = np.asarray(dst.crop(r).convert("RGB"))
            mm = m[r[1] - int(pos[1]):r[3] - int(pos[1]), r[0] - int(pos[0]):r[2] - int(pos[0])]
            ink = tuple(int(v) for v in np.median(a[..., :3][m], axis=0))
            dg = _diagnose(sub[mm], ink) if mm.any() else None
            if dg:
                kind, target = dg; AUDIT.append((CTX[0], kind, ink))
                if kind == "flat":
                    nc = _fix_ink(ink, target, float(np.median(_lum(sub[mm]))))
                    a = a.copy(); a[..., :3][a[..., 3] > 0] = nc; src = Image.fromarray(a, "RGBA")
                else:
                    _halo(dst, Image.fromarray((a[..., 3]).astype(np.uint8), "L"), pos, ink)
    except Exception as e:
        AUDIT.append((CTX[0], "erreur " + str(e)[:60], ()))
    dst.alpha_composite(src, (int(pos[0]), int(pos[1])))

_orig_text = ImageDraw.ImageDraw.text

def _safe_text(self, xy, text, fill=None, font=None, *a, **k):
    im = getattr(self, "_image", None)
    if (im is not None and im.mode in ("RGB", "RGBA") and isinstance(fill, tuple) and len(fill) >= 3 and text
            and isinstance(text, str) and text.strip() and not k.get("anchor") and font is not None):
        try:
            bb = self.textbbox(xy, text, font=font)
            r = _region(im, bb[0], bb[1], bb[2] - bb[0], bb[3] - bb[1])
            if r is not None:
                sub = np.asarray(im.crop(r).convert("RGBA"))
                if sub[..., 3].mean() > 200:   # fond opaque (sinon : calque transparent, contrôlé à la composition)
                    mk = Image.new("L", (r[2] - r[0], r[3] - r[1]), 0)
                    ImageDraw.Draw(mk).text((xy[0] - r[0], xy[1] - r[1]), text, fill=255, font=font)
                    mm = np.asarray(mk) > 150
                    dg = _diagnose(sub[..., :3][mm], fill) if mm.any() else None
                    if dg:
                        kind, target = dg; AUDIT.append((CTX[0], kind, fill[:3]))
                        if kind == "flat":
                            nc = _fix_ink(fill, target, float(np.median(_lum(sub[..., :3][mm]))))
                            fill = nc + tuple(fill[3:])
                        else:
                            _halo(im, mk, (r[0], r[1]), fill)
        except Exception as e:
            AUDIT.append((CTX[0], "erreur " + str(e)[:60], ()))
    return _orig_text(self, xy, text, fill, font, *a, **k)

ImageDraw.ImageDraw.text = _safe_text

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "render"))
from content import POSTS, SHOP, CTA_IG, CTA_FB  # noqa: E402
from content_am import POSTS_AM  # noqa: E402
from reels import REELS  # noqa: E402
from tests_axes import apply as _apply_axes, VIDEOS, vo_text  # noqa: E402
from datetime import date as _date, timedelta as _td

_apply_axes(POSTS)
from content_campagne import CAMP_AM, CAMP_PM  # noqa: E402
POSTS += CAMP_PM; POSTS_AM += CAMP_AM

REEL_DATES = {r["date"] for r in REELS}

def _shift(posts, start, offset=0):
    """Redate la file (un post par jour) et fait tourner la DA : jamais deux jours
    de suite dans la même DA, ni la même DA le matin et le soir du même jour."""
    d = _date.fromisoformat(start)
    for i, p in enumerate(posts):
        p["date"] = d.isoformat(); p["da"] = "abcde"[(i + offset) % 5]; d += _td(days=1)

_shift([p for p in POSTS if not p["date"].startswith("test")], "2026-11-11", 0)
_shift([p for p in POSTS_AM if not p["date"].startswith("test")], "2026-11-11", 2)
SLOTS = [("", POSTS, 0), ("-10h", POSTS_AM, 1)]   # 18h -> AAAA-MM-JJ.json · 10h -> AAAA-MM-JJ-10h.json
ALL = [p for _, L, _ in SLOTS for p in L]
# Les posts publiés en test ont une date préfixée "test-" : leur fichier n'est lu par aucun scénario

FAKE = "--fake" in sys.argv
ONLY = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
RAW = "https://raw.githubusercontent.com/Victor13013/ton-itineraire-media/pulse-care/"
PAGES = "https://victor13013.github.io/ton-itineraire-media/"
# Hôte des vidéos. raw.githubusercontent sert du application/octet-stream ;
# si Instagram le refuse, activer GitHub Pages et passer REEL_HOST à PAGES.
REEL_HOST = RAW

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

def nb(t):  # espaces insécables avant ? ! : ; € et entre un nombre et son unité
    t = re.sub(r"(\d) (min|s|j|h|mois|ans?|zones?)\b", "\\1\u00a0\\2", t)
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
    d = ImageDraw.Draw(base); sp = d.textlength(" ", font=fnt); pad = min(fnt.size * 0.14, sp * 0.42)
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
        for j, (w, hl, ww, glue) in enumerate(ln):
            if glue: xx -= sp
            if hl: last = (xx + ww, yy) if j == len(ln) - 1 else None
            elif last and last[1] == yy: last = None
            xx += ww + sp
        yy += fnt.size * lh
    out = sans_draw(base, x, y, lines, fnt, fill, hl_bg, hl_fg, lh, center_w)
    if spark and last:
        lx, ly = last
        if lx + 60 < W - 20:
            sparkle(base, lx + 34, ly + fnt.size * 0.42, 18, spark); sparkle(base, lx + 60, ly + fnt.size * 0.82, 10, spark)
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
    tw_ = int((W - 2 * M) * c.get("tw", 1))
    f, tl = sans_fit(c["title"], BLACK, tw_, 112, 64, 4)
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
    room = W - 2 * M - 230 if c.get("price") else W - 300
    cut, pk = product_cut(src, (255, 255, 255), room, bottom - top - 30)
    if pk:
        px = (W - cut.width) // 2 if not c.get("price") else M + (room - cut.width) // 2; py = top + (bottom - top - cut.height) // 2
        # socle : disque clair + ombre
        sd = ImageDraw.Draw(base); cxm = px + cut.width / 2; ry = 26; rx = min(max(cut.width * 0.55, 150), 300)
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
    if pk and not calls and not c.get("price"): sparkle(base, pbox[2] + 20, pbox[1] + 30, 22, FOREST)
    elif not c.get("price"): sparkle(base, pbox[0] - 10 if pk else M + 30, pbox[1] + 20, 22, FOREST)
    chrome(base, c, fg, sub_on(bg), light_btn=False)
    return base.convert("RGB")

# ── 4. Liste : photo en tête, cartes blanches à icônes
def t_list(c):
    bg = bg_for(c, 1) if bg_for(c, 1) != FOREST else MINTV
    base = rich_bg(bg, c.get("_n", 0) + 1)
    src = load(c["img"]); im, pk = prep(src); ph_h = 520
    if pk and touches_edge(im): pk = False
    if pk:
        cut, _ = product_cut(src, (255, 255, 255), 380, ph_h - 90)
        band = multiply_on(Image.new("RGB", (W, ph_h), CREAM), Image.new("RGB", (W, ph_h), WHITE_A))
        band.paste(multiply_on(Image.new("RGB", cut.size, CREAM), cut), (W - M - cut.width + 10, (ph_h - cut.height) // 2 + 20))
        base.paste(band, (0, 0)); title_fg = INKV; title_w = W - 2 * M - cut.width - 30
    else:
        ph = cover(im, W, ph_h).convert("RGBA"); ph.alpha_composite(gradient(W, ph_h, (8, 18, 12), 0.25, 1, 0, 210))
        base.paste(ph, (0, 0)); title_fg = WHITE_A; title_w = W - 2 * M
    if c.get("stamp"):                                   # tampon MYTHE / FAUX
        st = Image.new("RGBA", (360, 130), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        sd.rounded_rectangle([4, 4, 356, 126], radius=20, fill=(255, 255, 255, 225), outline=CORAL, width=8)
        fs = BLACK(72); tw = sd.textlength(c["stamp"], font=fs); sd.text(((360 - tw) / 2, 18), c["stamp"], font=fs, fill=CORAL)
        st = st.rotate(-12, resample=Image.BICUBIC, expand=True); base.alpha_composite(st, (W - M - st.width + 20, 70))
    f, tl = sans_fit(c["title"], BLACK, title_w, 74, 46, 3 if title_w < W - 2 * M else 2)
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
    chrome(base, c, INKV, GREYV, light_btn=False)
    return base.convert("RGB")

def tb_statement(c):
    n = c.get("_n", 0); base = mesh_bg("forest", n)
    framed_photo(base, load(c["img"]), (W - M - 330, 90, W - M - 10, 470), angle=6)
    d = ImageDraw.Draw(base)
    d.text((M - 6, 120), "“", font=BLACK(260), fill=LIME)
    f, tl = sans_fit(c["title"], BLACK, W - 2 * M, 96, 56, 4)
    bh = (78 if c.get("kicker") else 0) + f.size * (1.04 * len(tl) + 0.18)
    if c.get("sub"): bh += 30 + 92 + 30 * 1.28 * len(wrap(c["sub"], SB(30), W - 2 * M + 20 - 150))
    y = max(520, 520 + (H - 150 - 520 - bh) * 0.4)
    if c.get("kicker"): y = pill_outline(base, M, y, c["kicker"], LIME) + 30
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
    if c.get("stamp"): y += 130
    avail = H - 120 - y; gap = 20; ch = min((avail - gap * (k - 1)) / k, 200)
    stamp_y = y - 150
    y += (avail - (ch * k + gap * (k - 1))) * 0.35
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
        sd.rounded_rectangle([4, 4, 326, 116], radius=20, fill=(255, 255, 255, 225), outline=CORAL, width=8)
        fs = BLACK(66); tw = sd.textlength(c["stamp"], font=fs); sd.text(((330 - tw) / 2, 16), c["stamp"], font=fs, fill=CORAL)
        st = st.rotate(-6, resample=Image.BICUBIC, expand=True); base.alpha_composite(st, (M - 10, int(stamp_y)))
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
        while d.textlength(nb(big), font=fb_) > tw_ - 150: fb_ = BLACK(fb_.size - 6)
        d.text((x + 30, yy + 24), nb(big), font=fb_, fill=LIME)
        icon_disc(d, icon_for(big, small), x + tw_ - 50, yy + 50, 28, LIME, FOREST)
        ls = wrap(small, IM(28), tw_ - 64)
        draw_lines(d, x + 32, yy + th - 34 - 28 * 1.3 * len(ls), ls, IM(28), CREAM, 1.3)
        d.rounded_rectangle([x + 30, yy + th - 22, x + tw_ - 30, yy + th - 14], radius=4, fill=(255, 255, 255, 50))
        d.rounded_rectangle([x + 30, yy + th - 22, x + 30 + (tw_ - 60) * [0.92, 0.7, 0.85, 0.6][i % 4], yy + th - 14], radius=4, fill=LIME)
    chrome(base, c, CREAM, GREYV, light_btn=True)
    return base.convert("RGB")

def under_wave(d, x, y, text, fnt, color):
    """Vague sous un texte, calée sur le bas réel des lettres."""
    l, t, r, b = d.textbbox((x, y), text, font=fnt)
    squiggle(d, l, r, b + 14, color)
    return b + 14

def tb_versus(c):
    base = Image.new("RGBA", (W, H), SANDV + (255,))
    right = mesh_bg("forest", 1); base.paste(right.crop((W // 2, 0, W, H)), (W // 2, 0))
    left = mesh_bg("sand", 0); base.paste(left.crop((0, 0, W // 2, H)), (0, 0))
    d = ImageDraw.Draw(base); fi = SB(42); cw = W // 2 - M - 60
    f, tl = sans_fit(clean(c["title"]), BLACK, W - 2 * M - 80, 80, 50, 2)
    hf = BLACK(60)
    for head, _ in (c["left"], c["right"]):
        while d.textlength(head, font=hf) > cw - 10: hf = BLACK(hf.size - 4)
    def col_h(items): return sum(fi.size * 1.22 * len(wrap(it, fi, cw - 70)) + 46 for it in items)
    title_h = (60 if c.get("kicker") else 0) + f.size * 1.04 * len(tl) + 56
    block = title_h + 140 + hf.size + 70 + max(col_h(c["left"][1]), col_h(c["right"][1]))
    y = max(80, (H - 110 - block) / 2 + 50)
    if c.get("kicker"): kicker_pill(base, 0, y, c["kicker"], LIME, INKV, center=True); y += 60
    # titre sur une étiquette crème (lisible sur les deux moitiés)
    lw = max(d.textlength(" ".join(t[0] for t in ln).replace("  ", " "), font=f) for ln in tl)
    th = f.size * 1.04 * len(tl) + 36
    d.rounded_rectangle([(W - lw) / 2 - 34, y, (W + lw) / 2 + 34, y + th], radius=28, fill=CREAM)
    yy = y + 14
    for ln in tl:
        txt = " ".join(t[0] for t in ln).replace("  ", " "); tw = d.textlength(txt, font=f)
        d.text(((W - tw) / 2, yy), txt, font=f, fill=INKV); yy += f.size * 1.04
    y = int(y + th + 140)
    for side, (head, items) in enumerate([c["left"], c["right"]]):
        x = M - 10 if side == 0 else W // 2 + 60; good = side == 1 or c.get("both_good")
        fg = INKV if side == 0 else CREAM
        d.text((x, y), head, font=hf, fill=fg)
        iy = under_wave(d, x, y, head, hf, FOREST if side == 0 else LIME) + 50
        for it in items:
            icon_disc(d, "check" if good else "xmark", x + 26, iy + 24, 26, (LIME if side else (FOREST if good else CORAL)), (INKV if side else WHITE_A))
            iy = draw_lines(d, x + 70, iy, wrap(it, fi, cw - 70), fi, fg, 1.22) + 46
    vy = y - 72; d.ellipse([W / 2 - 50, vy - 50, W / 2 + 50, vy + 50], fill=LIME, outline=INKV, width=5)
    fv = BLACK(42); l_, t_, r_, b_ = d.textbbox((0, 0), "VS", font=fv); d.text((W / 2 - (l_ + r_) / 2, vy - (t_ + b_) / 2), "VS", font=fv, fill=INKV)
    chrome(base, c, INKV, GREYV, light_btn=True)
    return base.convert("RGB")

TPL_B = {"hero": tb_hero, "statement": tb_statement, "product": tb_product, "list": tb_list, "stats": tb_stats, "versus": tb_versus}
# ───────────────────────────── DA C : « Carnet & tchat » (3e DA)
# Formats natifs : conversation, note cochée, polaroids scotchés, post-it, annotations manuscrites.
PAPER = (250, 246, 238); DOTC = (222, 214, 198); TAPE = (238, 214, 160, 175)
POSTITS = [(232, 246, 178), (247, 222, 176), (214, 236, 222), (250, 216, 204)]
def HAND(s): return F("Caveat-Bold.ttf", s)

def paper_bg(seed=0, tint=None):
    base = Image.new("RGBA", (W, H), (tint or PAPER) + (255,)); d = ImageDraw.Draw(base)
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
    safe_composite(base, lay, (int(x), int(y))); return y + lay.height, x + lay.width

def c_title(base, c, x=M, y=100, maxw=W - 2 * M, start=100, maxlines=3, kicker=True, center=False):
    if kicker and c.get("kicker"): y, _ = hand_note(base, x, y, c["kicker"], 54, CORAL, -2, maxw, center); y += 6
    f, tl = sans_fit(c["title"], BLACK, maxw, start, 56, maxlines)
    return marker_title(base, x, y, tl, f, center_w=maxw if center else None)

def polaroid(src, w, h, caption=None, fy=0.5):
    cap_lines = wrap(clean(caption), HAND(46), w - 60) if caption else []
    bottom = 40 + (int(46 * 1.0 * len(cap_lines)) + 36 if cap_lines else 50)
    im = src; lay = Image.new("RGBA", (w, h), (255, 255, 255, 255)); ph_h = max(h - 28 - bottom, 50)
    pim, pk = prep(src)
    if pk:   # packshot : produit entier, centré sur le blanc du polaroid
        prod = trim(pim); prod = prod.resize(fit_size(prod, int((w - 56) * 0.88), int(ph_h * 0.88)), Image.LANCZOS)
        lay.paste(prod, (28 + (w - 56 - prod.width) // 2, 28 + (ph_h - prod.height) // 2))
    else:
        if (border_px(im).min(axis=1) > 238).mean() > 0.5:
            ww, hh = im.size; k = 0.66; im = im.crop((int(ww * (1 - k) / 2), int(hh * (1 - k) / 2), int(ww * (1 + k) / 2), int(hh * (1 + k) / 2)))
        lay.paste(cover(im, w - 56, ph_h, 0.5, fy), (28, 28))
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
    doodle_star(d, W - 48, top - 34, 26, CORAL); sparkle(base, M - 20, bot - 60, 22, FOREST)
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
    y = max(y + 20, 470); items = c["items"]; k = len(items); stamp_y = y - 40
    if c.get("stamp"): y += 120
    avail = card[3] - 60 - y; ch = min(avail / k, 250); y += (avail - ch * k) * 0.3; d = ImageDraw.Draw(base)
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
        sd.rounded_rectangle([4, 4, 326, 116], radius=20, fill=(255, 255, 255, 230), outline=CORAL, width=8)
        fs = BLACK(66); tw = sd.textlength(c["stamp"], font=fs); sd.text(((330 - tw) / 2, 16), c["stamp"], font=fs, fill=CORAL)
        st = st.rotate(-5, resample=Image.BICUBIC, expand=True); base.alpha_composite(st, (M - 10, int(stamp_y)))
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
    cut, pk = None, False   # en DA C, le produit est toujours posé dans un polaroid
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
        under_wave(d, 34, 56, head, hf, CORAL if side == 0 else LIME)
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


# ───────────────────────────── Formats « mixtes » (nov. 2026)
# Un seul gabarit par format, habillé selon la DA du post : "a" (v5), "b" (Gradient & verre), "c" (Carnet).
# Grand chiffre, quiz, étapes en zigzag, mosaïque de photos, arche, suivi de la semaine, schémas dessinés.
class Th: pass
C_TINTS = {"cream": PAPER, "blush": (252, 240, 234), "sage": (236, 243, 234)}
A_TONES = {"mint": MINTV, "sand": SANDV, "honey": HONEY, "forest": FOREST}
# DA "d" (Nuit) et DA "e" (Pop) : deux palettes de plus, pour sortir des pastels.
NIGHT = (11, 21, 17)
POPS = [CORAL, (233, 172, 74), (108, 170, 138), LIME]

def night_bg(n):
    base = Image.new("RGB", (W, H), NIGHT).convert("RGBA")
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(gl)
    cx, cy = (0.74 if n % 2 else 0.24) * W, (0.22 if n % 3 else 0.78) * H
    for r, a in ((640, 26), (430, 30), (250, 34)):
        gd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(46, 96, 72, a))
    base.alpha_composite(gl.filter(ImageFilter.GaussianBlur(120)))
    return grain(base, 7)

def pop_bg(bg, n):
    base = Image.new("RGB", (W, H), bg).convert("RGBA")
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    tint = tuple(min(255, int(v * 1.14)) for v in bg)
    cx, cy, r = (0.18 if n % 2 else 0.86) * W, (0.84 if n % 2 else 0.16) * H, int(W * 0.56)
    ld.ellipse([cx - r, cy - r, cx + r, cy + r], fill=tint + (150,))
    base.alpha_composite(lay.filter(ImageFilter.GaussianBlur(70)))
    return grain(base, 6)

def theme(c):
    t = Th(); t.da = c.get("da") or "a"; n = c.get("_n", 0); tone = c.get("tone")
    if t.da == "d":
        t.dark = True; t.base = night_bg(n); t.card = (26, 42, 34)
        t.ink = CREAM; t.sub = (176, 200, 186); t.acc = LIME; t.acc_ink = INKV
        t.card_ink = CREAM; t.card_sub = (186, 206, 194)
        return t
    if t.da == "e":
        bg = POPS[n % len(POPS)]; t.dark = bg == CORAL
        t.base = pop_bg(bg, n); t.card = WHITE_A
        t.ink = CREAM if t.dark else INKV; t.sub = (252, 226, 220) if t.dark else (58, 72, 62)
        t.acc = CREAM if t.dark else INKV; t.acc_ink = CORAL if t.dark else (LIME if bg != LIME else CREAM)
        t.card_ink = INKV; t.card_sub = GREYV
        return t
    if t.da == "b":
        kind = tone if tone in ("fresh", "sand", "forest") else ["fresh", "sand", "forest"][n % 3]
        t.dark = kind == "forest"; t.base = mesh_bg(kind, n)
        t.card = None
    elif t.da == "c":
        t.dark = False; t.base = paper_bg(n, C_TINTS.get(tone) or list(C_TINTS.values())[n % 3]); t.card = WHITE_A
    else:
        bg = A_TONES.get(tone) or BGS[n % 4]
        t.dark = bg == FOREST; t.base = rich_bg(bg, n); t.card = WHITE_A
    t.ink = CREAM if t.dark else INKV; t.sub = (200, 214, 204) if t.dark else GREYV
    t.acc = LIME if t.dark else (CORAL if t.da == "c" else FOREST); t.acc_ink = INKV if t.dark else (WHITE_A if t.da == "c" else CREAM)
    t.card_ink = CREAM if (t.da == "b" and t.dark) else INKV
    t.card_sub = (200, 214, 204) if (t.da == "b" and t.dark) else GREYV
    return t

def th_kicker(t, x, y, text, center=False, maxw=W - 2 * M):
    if not text: return y
    if t.da == "b": return pill_outline(t.base, x, y, text, t.acc, center) + 28
    if t.da == "c": return hand_note(t.base, x, y, text, 54, CORAL, -2, maxw, center)[0] + 6
    return kicker_pill(t.base, x, y, text, t.acc, t.acc_ink, center=center) + 26

def th_title(t, x, y, text, maxw=W - 2 * M, start=96, minsize=50, maxlines=3, center=False):
    f, tl = sans_fit(text, BLACK, maxw, start, minsize, maxlines)
    if t.da == "b":
        if not center: return title_b(t.base, x, y, tl, f, t.ink, t.acc)
        d = ImageDraw.Draw(t.base); sp = d.textlength(" ", font=f)
        for ln in tl:
            lw = sum(k[2] for k in ln) + sp * sum(1 for k in ln[1:] if not k[3])
            title_b(t.base, x + (maxw - lw) / 2, y, [ln], f, t.ink, t.acc); y += f.size * 1.04
        return y + f.size * 0.18
    if t.da == "c": return marker_title(t.base, x, y, tl, f, t.ink, LIME, 1.04, maxw if center else None)
    return sans_draw_marks(t.base, x, y, tl, f, t.ink, LIME if t.dark else FOREST, INKV if t.dark else CREAM, 1.02, maxw if center else None)

def th_sub(t, x, y, text, maxw=W - 2 * M, size=32, center=False):
    if not text: return y
    f = IM(size); ls = wrap(text, f, maxw); d = ImageDraw.Draw(t.base)
    for l in ls:
        d.text((x + ((maxw - d.textlength(l, font=f)) / 2 if center else 0), y), l, font=f, fill=t.sub); y += f.size * 1.36
    return y

def th_card(t, box, r=32, fill=None):
    x0, y0, x1, y1 = [int(v) for v in box]
    if fill is None and t.da == "b":
        glass(t.base, (x0, y0, x1, y1), r, (255, 255, 255) if not t.dark else (20, 40, 32), 170 if not t.dark else 150); return
    sh = Image.new("RGBA", t.base.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([x0 + 4, y0 + 12, x1 + 4, y1 + 12], radius=r, fill=(20, 30, 24, 42))
    t.base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    ImageDraw.Draw(t.base).rounded_rectangle([x0, y0, x1, y1], radius=r, fill=fill or t.card)

def contain_card(base, im, box, r=40, bg=WHITE_A):
    """Packshot : produit entier, centré sur une carte blanche arrondie."""
    x0, y0, x1, y1 = [int(v) for v in box]; w, h = x1 - x0, y1 - y0
    card = Image.new("RGB", (w, h), bg); prod = trim(im); prod = prod.resize(fit_size(prod, int(w * 0.84), int(h * 0.84)), Image.LANCZOS)
    card.paste(multiply_on(Image.new("RGB", prod.size, bg), prod), ((w - prod.width) // 2, (h - prod.height) // 2))
    m = Image.new("L", (w, h), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    base.paste(card, (x0, y0), m)

def th_photo(t, ref, box, k=0, fy=0.5, caption=None, tilt=True):
    x0, y0, x1, y1 = [int(v) for v in box]; src = load(ref)
    if t.da == "c":
        paste_rot(t.base, polaroid(src, x1 - x0, y1 - y0, caption, fy), (x0 + x1) / 2, (y0 + y1) / 2, [-3, 2.5, 3, -2][k % 4] if tilt else [-1.2, 1, 1.2, -1][k % 4])
        tape(t.base, (x0 + x1) / 2, y0 + 2, 150, [5, -6, -4, 6][k % 4]); return
    im, pk = prep(src)
    if pk: th_shadow(t, (x0, y0, x1, y1)); contain_card(t.base, im, (x0, y0, x1, y1)); return
    if t.da == "b" and tilt: framed_photo(t.base, src, (x0, y0, x1, y1), angle=[-3, 3, 2, -2][k % 4], fy=fy)
    elif t.da == "b": framed_photo(t.base, src, (x0, y0, x1, y1), angle=0, border=12, fy=fy)
    else: th_shadow(t, (x0, y0, x1, y1)); rounded_photo(t.base, src, (x0, y0, x1, y1), 40, fy)

def th_shadow(t, box, r=40):
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", t.base.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([x0 + 6, y0 + 16, x1 + 6, y1 + 16], radius=r, fill=(20, 30, 24, 50))
    t.base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))

def th_end(t, c):
    chrome(t.base, c, t.ink, t.sub, light_btn=t.dark)
    return t.base.convert("RGB")

# ── Grand chiffre
def x_bignum(c):
    def body(t, y):
        base = t.base
        y = th_kicker(t, M, y, c.get("kicker"))
        big = nb(c["big"]); f = BLACK(400); d = ImageDraw.Draw(base)
        while d.textlength(big, font=f) > W - 2 * M: f = BLACK(f.size - 8)
        l, tp, r, b = d.textbbox((0, 0), big, font=f); y += 6
        if t.da == "c":
            ov = Image.new("RGBA", base.size, (0, 0, 0, 0)); h0 = b - tp
            ImageDraw.Draw(ov).polygon([(M - 20, y + h0 * 0.55), (M + r - l + 24, y + h0 * 0.48), (M + r - l + 30, y + h0 * 1.04), (M - 12, y + h0 * 1.1)], fill=LIME + (235,))
            base.alpha_composite(ov); d = ImageDraw.Draw(base)
        d.text((M - l, y - tp), big, font=f, fill=t.ink if t.da == "c" else t.acc)
        y += b - tp + 18
        if t.da == "b": squiggle(d, M, M + min(r - l, 420), y + 8, LIME if t.dark else HONEY, 9, 8); y += 34
        y = th_title(t, M, y + 14, c["title"], start=70, minsize=44, maxlines=3)
        return th_sub(t, M, y + 6, c.get("sub"), W - 2 * M - 40)
    # Sans photo, le bloc est centré verticalement pour ne pas laisser le bas vide.
    t = theme(c); y = body(t, 100)
    if c.get("img") and H - 120 - y > 300:
        th_photo(t, c["img"], (M + (30 if t.da != "a" else 0), y + 44, W - M - (30 if t.da != "a" else 0), H - 116), c.get("_n", 0), c.get("fy", 0.45))
    elif H - 150 - y > 120:
        t = theme(c); body(t, 100 + (H - 150 - y) * 0.42)
    return th_end(t, c)

# ── Quiz : question + réponses (answer = indice de la bonne réponse, pour la slide de correction)
def x_quiz(c):
    t = theme(c); base = t.base
    y = th_kicker(t, M, 100, c.get("kicker"))
    y = th_title(t, M, y, c["title"], start=84, minsize=50, maxlines=4) + 34
    opts = c["options"]; ans = c.get("answer"); note = c.get("note"); fo = DB(40); gap = 22
    fn = IM(32); nl = wrap(note, fn, W - 2 * M - 110) if note else []
    note_h = (60 + fn.size * 1.36 * len(nl) + 30) if nl else 0
    oh = min(150, (H - 130 - y - note_h - gap * (len(opts) - 1)) / len(opts))
    for i, o in enumerate(opts):
        good = ans == i; box = (M - 10, y, W - M + 10, y + oh)
        if good: th_card(t, box, 34, fill=LIME)
        else: th_card(t, box, 34)
        d = ImageDraw.Draw(base); cy = y + oh / 2
        ink = INKV if good else (t.card_sub if ans is not None else t.card_ink)
        if good: icon_disc(d, "check", M + 58, cy, 36, FOREST, LIME)
        else:
            d.ellipse([M + 22, cy - 36, M + 94, cy + 36], outline=ink, width=4)
            fl = BLACK(36); ch = "ABCD"[i]; l_, t_, r_, b_ = d.textbbox((0, 0), ch, font=fl); d.text((M + 58 - (l_ + r_) / 2, cy - (t_ + b_) / 2), ch, font=fl, fill=ink)
        ls = wrap(o, fo, W - 2 * M - 150)
        draw_lines(d, M + 126, cy - fo.size * 1.16 * len(ls) / 2 - 4, ls, fo, ink, 1.16)
        y += oh + gap
    if nl:
        y += 14; d = ImageDraw.Draw(base); icon_disc(d, "bulb", M + 30, y + 30, 30, t.acc, t.acc_ink)
        draw_lines(d, M + 84, y + 6, nl, fn, t.ink, 1.36)
    return th_end(t, c)

# ── Étapes en zigzag
def x_steps(c):
    t = theme(c); base = t.base
    y = th_kicker(t, M, 100, c.get("kicker"))
    y = th_title(t, M, y, c["title"], start=84, minsize=50, maxlines=3) + 36
    items = c["items"]; k = len(items); gap = 30
    ch = min(250, (H - 130 - y - gap * (k - 1)) / k); cw = int((W - 2 * M + 20) * 0.76)
    y += (H - 130 - y - (ch * k + gap * (k - 1))) * 0.4
    fa = DB(42 if k <= 3 else 38); fb = IR(30 if k <= 3 else 27)
    for i, (a_, b_) in enumerate(items):
        left = i % 2 == 0; x0 = M - 10 if left else W - M + 10 - cw
        th_card(t, (x0, y, x0 + cw, y + ch), 36)
        d = ImageDraw.Draw(base); ncx = (x0 + cw + W - M + 10) / 2 if left else (M - 10 + x0) / 2
        fnb = BLACK(int(min(190, ch * 0.9))); s_ = str(i + c.get("start", 1)); bb = d.textbbox((0, 0), s_, font=fnb)
        d.text((ncx - (bb[0] + bb[2]) / 2, y + ch / 2 - (bb[1] + bb[3]) / 2), s_, font=fnb, fill=t.acc)
        la = wrap(a_, fa, cw - 150); lb = wrap(b_, fb, cw - 150) if b_ else []
        th_ = fa.size * 1.14 * len(la) + (8 + fb.size * 1.32 * len(lb) if lb else 0)
        icon_disc(d, icon_for(a_, b_), x0 + 62, y + ch / 2, 34, FOREST if not (t.da == "b" and t.dark) else LIME, LIME if not (t.da == "b" and t.dark) else INKV)
        ty = draw_lines(d, x0 + 118, y + ch / 2 - th_ / 2 - 4, la, fa, t.card_ink, 1.14)
        if lb: draw_lines(d, x0 + 118, ty + 8, lb, fb, t.card_sub, 1.32)
        y += ch + gap
    return th_end(t, c)

# ── Mosaïque : 2 à 4 photos légendées
def x_mosaic(c):
    t = theme(c); base = t.base
    y = th_kicker(t, M, 100, c.get("kicker"))
    y = th_title(t, M, y, c["title"], start=80, minsize=50, maxlines=2)
    y = th_sub(t, M, y + 4, c.get("sub"), W - 2 * M - 40) + 30
    imgs = c["imgs"]; n = len(imgs); g = 26 if t.da != "c" else 44; x0, x1 = M - 20, W - M + 20; top = int(y); bot = H - 116
    w2 = (x1 - x0 - g) // 2; h2 = (bot - top - g) // 2
    if n == 2: boxes = [(x0, top, x1, top + h2), (x0, top + h2 + g, x1, bot)]
    elif n == 3: boxes = [(x0, top, x0 + w2, bot), (x0 + w2 + g, top, x1, top + h2), (x0 + w2 + g, top + h2 + g, x1, bot)]
    else: boxes = [(x0 + (i % 2) * (w2 + g), top + (i // 2) * (h2 + g), x0 + (i % 2) * (w2 + g) + w2, top + (i // 2) * (h2 + g) + h2) for i in range(4)]
    for i, ((ref, label), bx) in enumerate(zip(imgs, boxes)):
        th_photo(t, ref, bx, i, 0.42, caption=label, tilt=False)
        if t.da != "c" and label:
            d = ImageDraw.Draw(base); pill_box(d, bx[0] + 26, bx[3] - 84, label, SB(28), FOREST, CREAM, 22, 13)
    return th_end(t, c)

# ── Arche : photo dans une arche, texte centré
def x_arch(c):
    t = theme(c); base = t.base
    y = th_kicker(t, M, 96, c.get("kicker"), center=True)
    y = th_title(t, M, y, c["title"], start=86, minsize=50, maxlines=3, center=True)
    y = th_sub(t, M + 40, y + 4, c.get("sub"), W - 2 * M - 80, 32, center=True)
    top = int(y + 44); bot = H - 96; w = int(min(640, (bot - top) * 0.86)); h = bot - top; x0 = (W - w) // 2
    d = ImageDraw.Draw(base); o = 20   # filet d'arche décalé
    d.pieslice([x0 - o, top - o, x0 + w + o, top - o + w + 2 * o], 180, 360, outline=t.acc, width=5)
    d.line([(x0 - o, top + w / 2), (x0 - o, bot)], fill=t.acc, width=5); d.line([(x0 + w + o, top + w / 2), (x0 + w + o, bot)], fill=t.acc, width=5)
    src = load(c["img"]); im, pk = prep(src)
    if pk:
        ph = Image.new("RGB", (w, h), WHITE_A); prod = trim(im); prod = prod.resize(fit_size(prod, int(w * 0.8), int(h * 0.8)), Image.LANCZOS)
        ph.paste(prod, ((w - prod.width) // 2, (h - prod.height) // 2 + 20))
    else: ph = cover(src, w, h, 0.5, c.get("fy", 0.4))
    base.paste(ph, (x0, top), arch_mask(w, h))
    sparkle(base, x0 - 70, top + 120, 24, t.acc); sparkle(base, x0 + w + 74, top + 300, 16, t.acc)
    if c.get("price"): sticker_v4(base, c["price"], x0 + w - 10, bot - 150, r=104, bg=LIME if t.da != "c" else CORAL, fg=INKV if t.da != "c" else WHITE_A, angle=8)
    return th_end(t, c)

# ── Suivi de la semaine : grille à cocher
def x_tracker(c):
    t = theme(c); base = t.base
    y = th_kicker(t, M, 100, c.get("kicker"))
    y = th_title(t, M, y, c["title"], start=84, minsize=50, maxlines=3) + 40
    rows = c.get("rows", ["Matin", "Soir"]); done = c.get("done", 3); days = "LMMJVSD"
    x0, x1 = M - 20, W - M + 20; lab = 150; cw = (x1 - x0 - lab - 30) / 7; rh = 150; hh = 90 + rh * len(rows) + 30
    th_card(t, (x0, y, x1, y + hh), 40); d = ImageDraw.Draw(base)
    for j, ch in enumerate(days):
        cx = x0 + lab + cw * (j + 0.5); f = DB(34); tw = d.textlength(ch, font=f); d.text((cx - tw / 2, y + 34), ch, font=f, fill=t.card_sub)
    for i, rname in enumerate(rows):
        cy = y + 90 + rh * (i + 0.5)
        draw_icon(d, icon_for(rname.lower()), x0 + 46, cy, 34, t.card_ink); d.text((x0 + 76, cy - 18), rname, font=SB(28), fill=t.card_ink)
        for j in range(7):
            cx = x0 + lab + cw * (j + 0.5); r = 40
            if j < done: icon_disc(d, "check", cx, cy, r, FOREST if not (t.da == "b" and t.dark) else LIME, LIME if not (t.da == "b" and t.dark) else INKV)
            else: d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=t.card_sub, width=4)
    y += hh + 40
    y = th_sub(t, M, y, c.get("sub"), W - 2 * M - 20, 34)
    if c.get("img") and H - 120 - y > 240: th_photo(t, c["img"], (M + 20, y + 30, W - M - 20, H - 116), 1, c.get("fy", 0.45))
    return th_end(t, c)

# ── Schémas dessinés (visuels originaux)
def _tooth_pts(cx, cy, s):
    """Contour d'une molaire stylisée (couronne + 2 racines)."""
    P = [(-0.50, -0.42), (-0.44, -0.62), (-0.24, -0.70), (0.0, -0.60), (0.24, -0.70), (0.44, -0.62), (0.50, -0.42),
         (0.46, -0.08), (0.36, 0.22), (0.30, 0.62), (0.20, 0.78), (0.10, 0.60), (0.04, 0.24), (0.0, 0.16),
         (-0.04, 0.24), (-0.10, 0.60), (-0.20, 0.78), (-0.30, 0.62), (-0.36, 0.22), (-0.46, -0.08)]
    return [(cx + x * s, cy + y * s) for x, y in P]

def _smooth(pts, it=3):
    for _ in range(it):
        out = []
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            out += [(0.75 * a[0] + 0.25 * b[0], 0.75 * a[1] + 0.25 * b[1]), (0.25 * a[0] + 0.75 * b[0], 0.25 * a[1] + 0.75 * b[1])]
        pts = out
    return pts

def draw_tooth(base, cx, cy, s, fill=WHITE_A, outline=INKV, width=8, shadow=True):
    pts = _smooth(_tooth_pts(cx, cy, s))
    if shadow:
        sh = Image.new("RGBA", base.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).polygon([(x + 10, y + 22) for x, y in pts], fill=(20, 30, 24, 60))
        base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20)))
    d = ImageDraw.Draw(base); d.polygon(pts, fill=fill)
    d.line(pts + [pts[0]], fill=outline, width=width, joint="curve")
    return d

def label_line(base, p0, p1, text, t, size=34, align="l"):
    d = ImageDraw.Draw(base); d.line([p0, p1], fill=t.ink, width=4); d.ellipse([p0[0] - 9, p0[1] - 9, p0[0] + 9, p0[1] + 9], fill=t.ink)
    f = SB(size); ls = text.split("\n"); w = max(d.textlength(l, font=f) for l in ls); h = f.size * 1.2 * len(ls)
    x = p1[0] + 14 if align == "l" else p1[0] - 14 - w
    d.rounded_rectangle([x - 16, p1[1] - h / 2 - 12, x + w + 16, p1[1] + h / 2 + 12], radius=18, fill=WHITE_A)
    draw_lines(d, x, p1[1] - h / 2 - 2, ls, f, INKV, 1.2)

def x_schema(c):
    t = theme(c); base = t.base; kind = c["kind"]
    y = th_kicker(t, M, 100, c.get("kicker"))
    y = th_title(t, M, y, c["title"], start=84, minsize=50, maxlines=3)
    y = th_sub(t, M, y + 4, c.get("sub"), W - 2 * M - 40)
    top = y + 30; bot = H - 120; cx = W / 2; cy = (top + bot) / 2; S = min(bot - top, W - 2 * M)
    d = ImageDraw.Draw(base); line = t.ink
    if kind == "tooth":      # coupe d'une dent : émail, dentine, pulpe, gencive
        s = min((bot - top) * 0.62, 480); ty = top + (bot - top) * 0.52; gum = (242, 168, 158)
        d.rounded_rectangle([M - 20, ty + s * 0.12, W - M + 20, ty + s * 0.62], radius=70, fill=gum)
        draw_tooth(base, cx, ty, s)
        d = ImageDraw.Draw(base)
        d.polygon(_smooth(_tooth_pts(cx, ty, s * 0.76)), fill=(250, 228, 182))
        d.polygon(_smooth([(cx + x * s, ty + y_ * s) for x, y_ in [(-0.15, -0.28), (0.0, -0.34), (0.15, -0.28), (0.13, 0.0), (0.19, 0.5), (0.13, 0.52), (0.0, 0.06), (-0.13, 0.52), (-0.19, 0.5), (-0.13, 0.0)]]), fill=CORAL)
        label_line(base, (cx - s * 0.44, ty - s * 0.3), (M + 190, ty - s * 0.62), "Émail", t, align="r")
        label_line(base, (cx + s * 0.3, ty - s * 0.22), (W - M - 200, ty - s * 0.62), "Dentine", t)
        label_line(base, (cx + s * 0.05, ty - s * 0.1), (W - M - 200, ty + s * 0.06), "Pulpe", t)
        label_line(base, (M + 120, ty + s * 0.36), (M + 190, ty + s * 0.92), "Gencive", t)
    elif kind == "angle":    # tête de brosse inclinée à 45° vers la gencive
        s = min((bot - top) * 0.46, 330); ty = top + (bot - top) * 0.46; gum = (242, 168, 158)
        d.rounded_rectangle([M - 20, ty + s * 0.3, W - M + 20, bot], radius=70, fill=gum)
        for k_, off in enumerate((-1.02, 0.0, 1.02)): draw_tooth(base, cx - s * 0.35 + off * s * 0.92, ty, s, width=7, shadow=k_ == 1)
        d = ImageDraw.Draw(base)
        gx, gy = cx - s * 0.35 + s * 0.5, ty + s * 0.3      # jonction dent / gencive
        d.line([(gx, gy - s * 1.05), (gx, gy + 70)], fill=t.sub, width=4)   # axe vertical de la dent
        br = Image.new("RGBA", (760, 300), (0, 0, 0, 0)); bd = ImageDraw.Draw(br)
        bd.rounded_rectangle([250, 120, 750, 220], radius=50, fill=(214, 178, 122), outline=INKV, width=7)
        bd.rounded_rectangle([250, 120, 420, 220], radius=50, fill=(236, 214, 176), outline=INKV, width=7)
        for i2 in range(6): bd.rounded_rectangle([268 + i2 * 32, 34, 294 + i2 * 32, 126], radius=12, fill=WHITE_A, outline=INKV, width=5)
        br = br.rotate(45, resample=Image.BICUBIC, expand=True)
        base.alpha_composite(br, (int(gx - 236), int(gy - br.height + 250)))
        d = ImageDraw.Draw(base)
        r2 = 230; d.arc([gx - r2, gy - r2, gx + r2, gy + r2], 225, 270, fill=CORAL, width=9)
        fb_ = BLACK(72); lab = "45°"; tw = d.textlength(lab, font=fb_)
        lx, ly = gx - 300, gy - 330
        d.rounded_rectangle([lx - 24, ly - 10, lx + tw + 24, ly + fb_.size + 18], radius=26, fill=WHITE_A)
        d.text((lx, ly), lab, font=fb_, fill=CORAL)
    elif kind == "plaque":   # plaque -> tartre, 3 dents
        s = min((bot - top) * 0.34, 250); ty = top + (bot - top) * 0.42
        stages = c.get("labels", ["Dent propre", "Plaque", "Tartre"]); cols = [None, (246, 222, 140), (198, 162, 96)]
        for i in range(3):
            tx = M + 20 + (W - 2 * M - 40) * (i + 0.5) / 3
            draw_tooth(base, tx, ty, s, width=7); d = ImageDraw.Draw(base)
            if cols[i]:
                for k_ in range(7 + 6 * i):
                    a_ = k_ * 2.4 + i; px = tx + s * 0.34 * math.cos(a_); py = ty - s * 0.1 + s * 0.3 * math.sin(a_ * 1.7); rr = 15 + 6 * i + (k_ % 3) * 5
                    d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=cols[i], outline=INKV, width=3)
            f = DB(34); tw = d.textlength(stages[i], font=f)
            by = ty + s * 0.74
            d.rounded_rectangle([tx - tw / 2 - 22, by, tx + tw / 2 + 22, by + 64], radius=32, fill=WHITE_A); d.text((tx - tw / 2, by + 12), stages[i], font=f, fill=INKV)
            if i < 2: doodle_arrow(base, (tx + s * 0.6, ty - s * 0.78), (tx + s * 1.05, ty - s * 0.78), t.acc, -0.5, 6)
    elif kind == "zones":    # 4 zones de brossage, 30 s chacune
        r = S * 0.46; cols = [LIME, MINTV, HONEY, (250, 216, 204)]; names = c.get("labels", ["Haut gauche", "Haut droite", "Bas droite", "Bas gauche"])
        for i, a0 in enumerate([180, 270, 0, 90]):
            d.pieslice([cx - r, cy - r, cx + r, cy + r], a0, a0 + 90, fill=cols[i], outline=INKV, width=6)
            am = math.radians(a0 + 45); px, py = cx + r * 0.58 * math.cos(am), cy + r * 0.58 * math.sin(am)
            f1 = BLACK(64); s1 = "30 s"; tw = d.textlength(nb(s1), font=f1); d.text((px - tw / 2, py - 56), nb(s1), font=f1, fill=INKV)
            f2 = SB(27); tw = d.textlength(names[i], font=f2); d.text((px - tw / 2, py + 18), names[i], font=f2, fill=INKV)
        d.ellipse([cx - 78, cy - 78, cx + 78, cy + 78], fill=FOREST, outline=INKV, width=6); draw_icon(d, "stopwatch", cx, cy, 64, LIME)
    elif kind == "angle":    # tête de brosse inclinée à 45° vers la gencive
        s = S * 0.62; tx, ty = cx - s * 0.32, cy + s * 0.12; gum = (240, 150, 140)
        d.rounded_rectangle([M - 20, ty - s * 0.2, W - M + 20, ty - s * 0.2 + 120], radius=60, fill=gum)
        draw_tooth(base, tx, ty + s * 0.42, s * 0.9); d = ImageDraw.Draw(base)
        gx, gy = tx + s * 0.4, ty + s * 0.12     # point de contact dent / gencive
        br = Image.new("RGBA", (int(s * 1.5), 260), (0, 0, 0, 0)); bd = ImageDraw.Draw(br)
        bd.rounded_rectangle([110, 100, br.width - 10, 190], radius=45, fill=(214, 178, 122), outline=INKV, width=6)
        for i in range(7): bd.rounded_rectangle([130 + i * 34, 20, 154 + i * 34, 106], radius=10, fill=WHITE_A, outline=INKV, width=4)
        br = br.rotate(-45, resample=Image.BICUBIC, expand=True)
        base.alpha_composite(br, (int(gx - 20), int(gy - br.height + 150))); d = ImageDraw.Draw(base)
        d.arc([gx - 170, gy - 170, gx + 170, gy + 170], 315, 360, fill=CORAL, width=8)
        d.line([(gx, gy), (gx + 250, gy)], fill=CORAL, width=5)
        fb_ = BLACK(84); d.text((gx + 196, gy - 128), "45°", font=fb_, fill=CORAL if not t.dark else LIME)
    elif kind == "plaque":   # plaque -> tartre, 3 dents
        s = S * 0.34; stages = c.get("labels", ["Dent propre", "Plaque", "Tartre"]); cols = [None, (246, 226, 150), (196, 160, 96)]
        for i in range(3):
            tx = M + 40 + (W - 2 * M - 80) * (i + 0.5) / 3; ty = cy - 30
            draw_tooth(base, tx, ty, s * 1.9, width=7); d = ImageDraw.Draw(base)
            if cols[i]:
                for k_ in range(6 + 5 * i):
                    a_ = k_ * 2.4 + i; px = tx + s * 0.62 * math.cos(a_) * 0.9; py = ty - s * 0.2 + s * 0.42 * math.sin(a_ * 1.7); rr = 20 + 10 * i + (k_ % 3) * 6
                    d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=cols[i], outline=INKV, width=3)
            f = DB(36); tw = d.textlength(stages[i], font=f)
            d.rounded_rectangle([tx - tw / 2 - 22, ty + s * 1.7, tx + tw / 2 + 22, ty + s * 1.7 + 64], radius=32, fill=WHITE_A); d.text((tx - tw / 2, ty + s * 1.7 + 10), stages[i], font=f, fill=INKV)
            if i < 2: doodle_arrow(base, (tx + s * 1.05, ty - s * 1.3), (tx + s * 1.7, ty - s * 1.3), t.acc, -0.35, 6)
    elif kind == "calendar": # 12 mois, un changement de tête tous les 3 mois
        months = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]; g = 20; cw = (W - 2 * M + 40 - 3 * g) / 4; chh = min(190, (bot - top - 2 * g) / 3)
        y0 = cy - (3 * chh + 2 * g) / 2
        for i, m_ in enumerate(months):
            x = M - 20 + (i % 4) * (cw + g); yy = y0 + (i // 4) * (chh + g); hit = i % 3 == 0
            th_card(t, (x, yy, x + cw, yy + chh), 30, fill=LIME if hit else None); d = ImageDraw.Draw(base)
            d.text((x + 24, yy + 16), m_, font=BLACK(54), fill=INKV if hit else t.card_ink)
            if hit: draw_icon(d, "rotate", x + cw - 62, yy + chh - 62, 60, FOREST)
    return th_end(t, c)

# ───────────────────────────── Gabarits « réponse au client » (nov. 2026)
# Quatre mises en page qui cassent l'habitude carte + titre : produit annoté,
# mot barré corrigé à la main, crainte/réponse en deux blocs, mise en page magazine.

def light_bg(c):
    """Fond « studio » du post : clair sur les DA a/b/c, nuit sur la d, saturé sur la e."""
    n = c.get("_n", 0); da = c.get("da") or "a"
    if da == "d": return night_bg(n).convert("RGBA")
    if da == "e": return pop_bg(POPS[n % len(POPS)], n).convert("RGBA")
    if da == "c": return paper_bg(n, PAPER).convert("RGBA")
    tints = {"a": (238, 246, 240), "b": (240, 243, 248)}
    base = Image.new("RGB", (W, H), tints[da]).convert("RGBA")
    v = Image.linear_gradient("L").resize((W, H))
    return Image.composite(Image.new("RGB", (W, H), (255, 255, 255)).convert("RGBA"), base,
                           v.point(lambda p: 255 - p)).convert("RGBA")

def leader(d, x0, y0, x1, y1, color, r=11):
    """Pastille + trait de rappel vers un détail du produit."""
    d.ellipse([x0 - r, y0 - r, x0 + r, y0 + r], fill=WHITE_A, outline=color, width=4)
    d.ellipse([x0 - 4, y0 - 4, x0 + 4, y0 + 4], fill=color)
    d.line([x0 + r, y0, x1, y1], fill=color, width=3)

def strike_line(d, x, y, w, color, h):
    d.line([x - 8, y + h * 0.54, x + w + 8, y + h * 0.46], fill=color, width=max(6, int(h * 0.09)))

# ── Produit annoté : le produit en grand, des rappels vers les détails qui comptent
def x_callout(c):
    base = light_bg(c); t = theme_on(base, c); d = ImageDraw.Draw(base)
    acc, hand_c = t.acc, (LIME if t.dark else CORAL)
    y = 92
    if c.get("kicker"):
        if c.get("da") == "c": y, _ = hand_note(base, M, y, c["kicker"], 52, hand_c, -2); y += 4
        else: y = kicker_pill(base, M, y, c["kicker"], acc, t.acc_ink) + 22
    pw_max, ph_max = int(W * 0.40), int(H * 0.37)
    px, py = M - 10, int(H * 0.15)
    prod, ok = product_cut(load(c["img"]), base.convert("RGB").getpixel((200, int(H * 0.3))), pw_max, ph_max)
    if ok:
        pw, ph = prod.size
        soft_shadow(base, (px + 30, py + ph - 50, px + pw - 30, py + ph), 60, 28)
        base.paste(prod, (px, py))
    else:
        pw, ph = pw_max, ph_max; rounded_photo(base, load(c["img"]), (px, py, px + pw, py + ph), 36, c.get("fy", 0.45))
    d = ImageDraw.Draw(base)
    # rappels : (libellé, fraction horizontale, fraction verticale du produit)
    # triés par hauteur d'ancrage : les traits de rappel ne se croisent jamais
    notes = sorted(c.get("notes", [])[:2], key=lambda n: n[2]); tx = px + pw + 54; f = IM(30)
    rows = [py + ph * k for k in ([0.26] if len(notes) == 1 else [0.16, 0.66])]
    for (lab, fx, fy), ry in zip(notes, rows):
        ax, ay = px + pw * fx, py + ph * fy
        leader(d, ax, ay, tx - 16, ry, acc)
        for j, ln in enumerate(wrap(lab, f, W - M - tx)):
            d.text((tx, ry - f.size * 0.62 + j * f.size * 1.3), ln, font=f, fill=t.ink)
    # correction manuscrite : le mot rayé, et le bon mot au-dessus
    ty = max(int(H * 0.57), int(py + ph + 46))
    if c.get("strike"):
        bad, good = c["strike"]; f = BLACK(72)
        while d.textlength(bad.upper(), font=f) > W - 2 * M - 260: f = BLACK(f.size - 4)
        hand_note(base, M + 16, ty - 86, good, 64, hand_c, -7)
        d = ImageDraw.Draw(base); d.text((M, ty), bad.upper(), font=f, fill=(104, 122, 112) if t.dark else (150, 162, 154))
        strike_line(d, M, ty, d.textlength(bad.upper(), font=f), hand_c, f.size); ty += f.size * 1.18
    f, tl = sans_fit(c["title"], BLACK, W - 2 * M, 72, 42, 2)
    ty = sans_draw_marks(base, M, ty, tl, f, t.ink, acc, t.acc_ink, 1.02)
    if c.get("sub"):
        f2 = IM(29); d = ImageDraw.Draw(base)
        for ln in wrap(c["sub"], f2, W - 2 * M - 40):
            d.text((M, ty + 10), ln, font=f2, fill=t.sub); ty += f2.size * 1.32
    if c.get("cta"):
        f3 = BOLD(29); d = ImageDraw.Draw(base)
        tw = d.textlength(c["cta"].upper(), font=f3); bw = tw + 134
        bx, by = M, H - 178
        d.rounded_rectangle([bx, by, bx + bw, by + 80], radius=40, outline=t.ink, width=3)
        d.text((bx + 38, by + 25), c["cta"].upper(), font=f3, fill=t.ink)
        d.ellipse([bx + bw - 72, by + 13, bx + bw - 12, by + 73], fill=t.ink)
        d.text((bx + bw - 55, by + 22), "→", font=ARR(32), fill=NIGHT if t.dark else CREAM)
    return base.convert("RGB")

# ── Mot barré : on corrige à voix haute ce que le client croit
def x_note(c):
    base = light_bg(c); t = theme_on(base, c); hand_c = LIME if t.dark else CORAL
    d = ImageDraw.Draw(base); y = 120
    if c.get("kicker"):
        if c.get("da") == "c": y, _ = hand_note(base, M, y, c["kicker"], 54, hand_c, -2); y += 10
        else: y = kicker_pill(base, M, y, c["kicker"], t.acc, t.acc_ink) + 34
    f, tl = sans_fit(c["bad"], BLACK, W - 2 * M, 84, 48, 3); d = ImageDraw.Draw(base)
    for ln in tl:
        txt = " ".join(k[0] for k in ln); w = d.textlength(txt, font=f)
        d.text((M, y), txt, font=f, fill=(104, 122, 112) if t.dark else (154, 166, 158))
        strike_line(d, M, y, w, hand_c, f.size); y += f.size * 1.08
    y, _ = hand_note(base, M + 30, y + 4, c.get("hand", "en vrai :"), 72, hand_c, -4)
    y = th_title(t, M, y + 10, c["good"], start=92, minsize=52, maxlines=3)
    top = H - 120   # haut de la vignette, calculé avant d'écrire le sous-titre
    if c.get("img"):
        bg = base.convert("RGB").getpixel((W - 200, H - 300))
        prod, ok = product_cut(load(c["img"]), bg, int(W * 0.40), int(H * 0.28))
        if ok:
            bx, by = W - M - prod.width, H - 120 - prod.height
            soft_shadow(base, (bx + 20, by + prod.height - 40, bx + prod.width - 20, by + prod.height), 55, 26)
            base.paste(prod, (bx, by)); top = by
        else:   # photo d'ambiance : vignette arrondie, jamais de blanc collé
            pw, ph = int(W * 0.40), int(H * 0.24); bx, by = W - M - pw, H - 120 - ph
            soft_shadow(base, (bx + 14, by + ph - 34, bx + pw - 14, by + ph), 50, 24)
            rounded_photo(base, load(c["img"]), (bx, by, bx + pw, by + ph), 32, c.get("fy", 0.45)); top = by
    if c.get("sub"):
        d = ImageDraw.Draw(base); f2 = IM(32); ls = wrap(c["sub"], f2, W - 2 * M - 60)
        while y + 14 + len(ls) * f2.size * 1.36 > top - 26 and f2.size > 23:
            f2 = IM(f2.size - 2); ls = wrap(c["sub"], f2, W - 2 * M - 60)
        for ln in ls:
            d.text((M, y + 14), ln, font=f2, fill=t.sub); y += f2.size * 1.36
    return base.convert("RGB")

def theme_on(base, c):
    """Réutilise les helpers de titre sur un fond déjà dessiné, avec les encres de la DA."""
    t = Th(); da = c.get("da") or "a"; t.da = da; t.base = base; n = c.get("_n", 0)
    t.dark = da == "d" or (da == "e" and POPS[n % len(POPS)] == CORAL)
    t.ink = CREAM if t.dark else INKV
    t.sub = (186, 206, 194) if da == "d" else ((252, 226, 220) if t.dark else GREYV)
    t.acc = LIME if t.dark else (CORAL if da == "c" else FOREST)
    t.acc_ink = INKV if t.dark else (WHITE_A if da == "c" else CREAM)
    t.card = (26, 42, 34) if t.dark else WHITE_A
    t.card_ink = t.ink; t.card_sub = t.sub
    return t

# ── Crainte / réponse : deux blocs pleine largeur, rien d'autre
def x_fear(c):
    n = c.get("_n", 0); da = c.get("da") or "a"; cut = int(H * 0.47)
    # Haut : la crainte, sur fond sombre ou saturé. Bas : la réponse, sur fond clair.
    if da == "d":
        top, low, rule = night_bg(n).convert("RGBA"), rich_bg(MINTV, n).convert("RGBA"), LIME
        top_ink, k1, k2 = CREAM, LIME, FOREST
    elif da == "e":
        bg = POPS[n % len(POPS)]; dark = bg == CORAL
        top = pop_bg(bg, n).convert("RGBA"); low = Image.new("RGB", (W, H), CREAM).convert("RGBA")
        rule = INKV if not dark else CREAM
        top_ink, k1, k2 = (CREAM if dark else INKV), (CREAM if dark else INKV), FOREST
    else:
        top = mesh_bg("forest", n).convert("RGBA")
        low = rich_bg(SANDV if da == "c" else MINTV, n).convert("RGBA")
        rule, top_ink, k1, k2 = LIME, CREAM, LIME, FOREST
    base = Image.new("RGBA", (W, H), FOREST); base.alpha_composite(top, (0, 0))
    base.paste(low.crop((0, cut, W, H)), (0, cut))
    d = ImageDraw.Draw(base); d.line([0, cut, W, cut], fill=rule, width=5)
    q = c["fear"] if c["fear"].lstrip().startswith("«") else "« " + c["fear"] + " »"
    f0 = BOLD(28); f, tl = sans_fit(q, BLACK, W - 2 * M, 72, 42, 4)
    y = max(104, (cut - (56 + f.size * 1.06 * len(tl))) / 2)
    d.text((M, y), (c.get("kicker") or "TU TE DIS").upper(), font=f0, fill=k1); y += 56
    for ln in tl:
        d.text((M, y), " ".join(k[0] for k in ln), font=f, fill=top_ink); y += f.size * 1.06
    # bloc du bas mesuré d'abord, pour le centrer dans sa bande
    t = theme_on(base, c); t.dark = False; t.ink = INKV; t.sub = GREYV; t.acc = FOREST; t.acc_ink = CREAM
    probe = Th(); probe.__dict__.update(t.__dict__); probe.base = base.copy()
    end = th_title(probe, M, cut + 118, c["answer"], start=68, minsize=40, maxlines=3)
    f2 = IM(30); subl = wrap(c["sub"], f2, W - 2 * M - 40) if c.get("sub") else []
    end += 12 + f2.size * 1.34 * len(subl)
    yy = cut + 60 + max(0, (H - 120 - end) * 0.45)
    d.text((M, yy), (c.get("kicker2") or "EN VRAI").upper(), font=BOLD(28), fill=k2); yy += 54
    yy = th_title(t, M, yy, c["answer"], start=68, minsize=40, maxlines=3)
    for ln in subl:
        d.text((M, yy + 12), ln, font=f2, fill=GREYV); yy += f2.size * 1.34
    chrome(base, c, CREAM, GREYV, light_btn=False)
    return base.convert("RGB")

# ── Magazine : photo bord à bord, titre en bas, aucune carte
def x_editorial(c):
    base = light_bg(c); ph = int(H * 0.56)
    im = cover(load(c["img"]), W, ph, 0.5, c.get("fy", 0.45))
    base.paste(im.convert("RGBA"), (0, 0))
    d = ImageDraw.Draw(base)
    t = theme_on(base, c)
    if c.get("over"):
        f0 = BOLD(27); tw = d.textlength(c["over"].upper(), font=f0)
        d.rounded_rectangle([M, ph - 96, M + tw + 56, ph - 28], radius=34, fill=NIGHT if t.dark else CREAM)
        d.text((M + 28, ph - 82), c["over"].upper(), font=f0, fill=CREAM if t.dark else INKV)
    y = ph + 54
    if c.get("kicker"):
        f0 = BOLD(26); txt = " ".join(c["kicker"].upper())
        d.text((M, y), txt, font=f0, fill=LIME if t.dark else (CORAL if c.get("da") == "c" else FOREST)); y += 52
        d.line([M, y, W - M, y], fill=(58, 78, 68) if t.dark else (206, 214, 206), width=2); y += 34
    y = th_title(t, M, y, c["title"], start=86, minsize=48, maxlines=3)
    if c.get("sub"):
        maxw = W - 2 * M - (150 if c.get("swipe") else 30); f2 = IM(32)
        ls = wrap(c["sub"], f2, maxw)
        while len(ls) * f2.size * 1.36 + y + 16 > H - 150 and f2.size > 24:
            f2 = IM(f2.size - 2); ls = wrap(c["sub"], f2, maxw)
        for ln in ls:
            d.text((M, y + 16), ln, font=f2, fill=t.sub); y += f2.size * 1.36
    chrome(base, c, t.ink, t.sub, light_btn=t.dark)
    return base.convert("RGB")

# ── Ticket de caisse : le détail d'un prix, ligne par ligne
def x_ticket(c):
    t = theme(c); base = t.base
    y = th_kicker(t, M, 96, c.get("kicker"))
    y = th_title(t, M, y + 6, c["title"], start=76, minsize=46, maxlines=2) + 26
    lines = c["lines"]; tot = c.get("total")
    tw, pad = W - 2 * M - 40, 42
    fN = IM(26); note_l = wrap(c["note"], fN, tw - 2 * pad) if c.get("note") else []
    th_ = pad * 2 + 54 + len(lines) * 58 + (104 if tot else 0) + int(len(note_l) * fN.size * 1.3)
    tx = M + 20; ty = int(y + max(0, (H - 150 - y - th_) * 0.40))
    tick = Image.new("RGBA", (tw, th_), (255, 255, 255, 255)); td = ImageDraw.Draw(tick)
    fL, fV, fS = IM(31), BOLD(31), BOLD(25)
    td.text((pad, pad - 6), (c.get("head") or "PULSE CARE").upper(), font=fS, fill=GREYV)
    yy = pad + 44
    for lab, val in lines:
        td.text((pad, yy), lab, font=fL, fill=INKV)
        vw = td.textlength(val, font=fV)
        for dx in range(int(pad + td.textlength(lab, font=fL)) + 16, int(tw - pad - vw) - 12, 11):
            td.ellipse([dx, yy + 20, dx + 3, yy + 23], fill=(190, 198, 192))
        td.text((tw - pad - vw, yy), val, font=fV, fill=INKV); yy += 58
    if tot:
        for dx in range(pad, tw - pad, 14): td.line([dx, yy + 10, dx + 7, yy + 10], fill=(176, 186, 178), width=3)
        yy += 36; fT = BLACK(58)
        td.text((pad, yy), tot[0].upper(), font=BOLD(30), fill=GREYV)
        td.text((tw - pad - td.textlength(nb(tot[1]), font=fT), yy - 16), nb(tot[1]), font=fT, fill=INKV); yy += 76
    for j, ln in enumerate(note_l): td.text((pad, yy - 10 + j * fN.size * 1.3), ln, font=fN, fill=GREYV)
    # bord bas dentelé, comme un vrai ticket
    m = Image.new("L", (tw, th_), 255); md = ImageDraw.Draw(m)
    for i in range(0, tw, 26): md.ellipse([i - 2, th_ - 13, i + 24, th_ + 13], fill=0)
    tick.putalpha(m)
    lay = tick.rotate(-1.4, resample=Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle([tx + 6, ty + 16, tx + lay.width, ty + lay.height + 10], fill=(18, 30, 24, 60))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    base.alpha_composite(lay, (tx, ty))
    return th_end(t, c)

# ── Écran coupé : la photo d'un côté, l'argument de l'autre
def x_split(c):
    t = theme(c); base = t.base; left = c.get("side") != "right"
    cx = int(W * 0.46)
    bx0, bx1 = (0, cx) if left else (W - cx, W)
    rounded_photo(base, load(c["img"]), (bx0 - 40 if left else bx0, 0, bx1 if left else bx1 + 40, H), 0, c.get("fy", 0.5))
    pan = Image.new("RGBA", (W - cx, H), (FOREST if t.dark or c.get("dark") else CREAM) + (242,))
    base.alpha_composite(pan, (cx if left else 0, 0))
    ink = CREAM if (t.dark or c.get("dark")) else INKV
    sub = (198, 214, 204) if ink == CREAM else GREYV
    x = cx + 54 if left else 54; w = W - cx - 100
    d = ImageDraw.Draw(base); y = 130
    if c.get("kicker"):
        f0 = BOLD(26); d.text((x, y), " ".join(c["kicker"].upper()), font=f0, fill=LIME if ink == CREAM else CORAL); y += 54
    f, tl = sans_fit(c["title"], BLACK, w, 68, 40, 4)
    for ln in tl:
        d.text((x, y), " ".join(k[0] for k in ln), font=f, fill=ink); y += f.size * 1.04
    y += 18
    for it in c.get("items", [])[:4]:
        icon_disc(d, icon_for(it), x + 20, y + 20, 20, LIME if ink == CREAM else FOREST, INKV if ink == CREAM else CREAM)
        f2 = IM(29)
        for j, ln in enumerate(wrap(it, f2, w - 58)):
            d.text((x + 56, y + j * f2.size * 1.26), ln, font=f2, fill=ink);
        y += max(50, len(wrap(it, f2, w - 58)) * f2.size * 1.26 + 16)
    if c.get("price"):
        f3 = BLACK(62); d.text((x, H - 230), nb(c["price"]), font=f3, fill=LIME if ink == CREAM else FOREST)
        if c.get("sub"):
            f4 = IM(27)
            for j, ln in enumerate(wrap(c["sub"], f4, w)):
                d.text((x, H - 152 + j * f4.size * 1.3), ln, font=f4, fill=sub)
    return th_end(t, c)

# ── Clôture : le produit en grand, le prix, trois garanties
def x_offer(c):
    t = theme(c); base = t.base
    y = th_kicker(t, M, 92, c.get("kicker"), center=True)
    y = th_title(t, M, y + 4, c["title"], start=76, minsize=44, maxlines=2, center=True) + 10
    bg = base.convert("RGB").getpixel((W // 2, int(H * 0.52)))
    top, bot = int(y) + 10, H - 262          # bande photo, bornée par la rangée de garanties
    prod, ok = product_cut(load(c["img"]), bg, int(W * 0.62), bot - top)
    if ok:
        px = (W - prod.width) // 2; py = top + (bot - top - prod.height) // 2
        soft_shadow(base, (px + 40, py + prod.height - 50, px + prod.width - 40, py + prod.height), 60, 30)
        base.paste(prod, (px, py))
    else:
        px0, px1 = M + 30, W - M - 30
        th_shadow(t, (px0, top, px1, bot)); rounded_photo(base, load(c["img"]), (px0, top, px1, bot), 40, c.get("fy", 0.45))
    if c.get("price"):
        sticker_v4(base, nb(c["price"]), W - M - 22, top + 78, 90, LIME, INKV, -12)
    d = ImageDraw.Draw(base); perks = c.get("perks", [])[:3]
    if perks:
        cw = (W - 2 * M) / len(perks); yy = H - 188
        for i, p_ in enumerate(perks):
            cxp = M + cw * (i + 0.5)
            icon_disc(d, icon_for(p_), cxp, yy, 26, t.acc, t.acc_ink)
            f = IM(26); ls = wrap(p_, f, cw - 24)
            for j, ln in enumerate(ls):
                d.text((cxp - d.textlength(ln, font=f) / 2, yy + 40 + j * f.size * 1.24), ln, font=f, fill=t.ink)
    return th_end(t, c)

# ── Formats « natifs » : ce qui ressemble à ce qu'on voit sur son téléphone (conversation, notes, question, avis)
def phone_card(base, box, r=56):
    soft_shadow(base, (box[0] + 20, box[3] - 40, box[2] - 20, box[3] + 10), 60, 40)
    ImageDraw.Draw(base).rounded_rectangle(box, radius=r, fill=(255, 255, 255))

def x_chatpost(c):
    t = theme(c); base = t.base; d = ImageDraw.Draw(base)
    y = th_kicker(t, M, 90, c.get("kicker")) if c.get("kicker") else 90
    box = (M, y + 20, W - M, H - 150); phone_card(base, box)
    cx = W / 2; d.ellipse([cx - 38, box[1] + 26, cx + 38, box[1] + 102], fill=(200, 204, 210))
    ini = c["contact"][0].upper(); fi = BOLD(38); d.text((cx - d.textlength(ini, font=fi) / 2, box[1] + 38), ini, font=fi, fill=(255, 255, 255))
    fn_ = IM(28); d.text((cx - d.textlength(c["contact"], font=fn_) / 2, box[1] + 110), c["contact"], font=fn_, fill=(40, 40, 40))
    d.line([box[0], box[1] + 160, box[2], box[1] + 160], fill=(230, 230, 233), width=2)
    yy = box[1] + 190; fnt = IM(40)
    for side, txt in c["msgs"]:
        out = side == "out"; ls = wrap(txt, fnt, 560)
        w = max(d.textlength(l, font=fnt) for l in ls) + 60; h = len(ls) * fnt.size * 1.26 + 36
        x = box[2] - 34 - w if out else box[0] + 34
        d.rounded_rectangle([x, yy, x + w, yy + h], radius=36, fill=(36, 96, 72) if out else (234, 234, 236))
        for i, l in enumerate(ls): d.text((x + 30, yy + 16 + i * fnt.size * 1.26), l, font=fnt, fill=(250, 247, 240) if out else (20, 20, 20))
        yy += h + 22
    if c.get("caption_end"):
        f2 = BOLD(44); ls = wrap(c["caption_end"], f2, box[2] - box[0] - 80)
        yy = box[3] - 50 - len(ls) * f2.size * 1.2
        for l in ls: d.text((box[0] + 40, yy), l, font=f2, fill=(36, 96, 72)); yy += f2.size * 1.2
    return th_end(t, c)

def x_notespost(c):
    base = Image.new("RGB", (W, H), (252, 250, 243)).convert("RGBA"); d = ImageDraw.Draw(base)
    d.text((M, 90), "‹ Notes", font=MED(36), fill=(214, 160, 20))
    d.text((M, 170), c["title"], font=BLACK(78), fill=(20, 20, 20))
    y = 320; fnt = IM(52)
    for txt, mode in c["items"]:
        if mode == "total":
            d.line([M, y, W - M, y], fill=(210, 205, 190), width=3); y += 26
            f2 = BLACK(66); d.text((M, y), txt, font=f2, fill=(36, 96, 72)); y += f2.size * 1.5; continue
        ls = wrap("– " + txt, fnt, W - 2 * M)
        for l in ls:
            d.text((M, y), l, font=fnt, fill=(140, 140, 140) if mode == "barre" else (20, 20, 20))
            if mode == "barre": d.line([M, y + fnt.size * 0.62, M + d.textlength(l, font=fnt), y + fnt.size * 0.62], fill=(226, 108, 92), width=6)
            y += fnt.size * 1.32
        y += 14
    d.rectangle([M, y + 4, M + 4, y + 60], fill=(214, 160, 20))
    if c.get("img"):
        # photo collée dans la note, comme une pièce jointe
        top = int(y + 100); bw, bh = W - 2 * M, H - 90 - top
        if bh > 220:
            ph = ImageOps.fit(load(c["img"]).convert("RGB"), (bw, bh), centering=(0.5, c.get("fy", 0.5)))
            mk = Image.new("L", (bw, bh), 0); ImageDraw.Draw(mk).rounded_rectangle([0, 0, bw, bh], 36, fill=255)
            base.paste(ph, (M, top), mk)
    return base.convert("RGB")

def x_commentpost(c):
    t = theme(c); base = t.base; d = ImageDraw.Draw(base)
    if c.get("img"):
        th_photo(t, c["img"], (0, 0, W, int(H * 0.52)), c.get("_n", 0), c.get("fy", 0.45))
    fnt = IM(42); ls = wrap(c["comment"], fnt, W - 2 * M - 160)
    ch_ = 110 + len(ls) * fnt.size * 1.3; y0 = int(H * 0.52) - ch_ / 2 if c.get("img") else 260
    box = (M, y0, W - M, y0 + ch_); phone_card(base, box, 40); d = ImageDraw.Draw(base)
    d.ellipse([box[0] + 30, box[1] + 30, box[0] + 100, box[1] + 100], fill=(210, 214, 218))
    d.text((box[0] + 124, box[1] + 30), c.get("who", "Une question qu'on reçoit souvent"), font=BOLD(30), fill=(30, 30, 30))
    for i, l in enumerate(ls): d.text((box[0] + 124, box[1] + 76 + i * fnt.size * 1.3), l, font=fnt, fill=(30, 30, 30))
    y = box[3] + (60 if c.get("img") else 130)
    if c.get("kicker2"):
        d.text((M, y), c["kicker2"].upper(), font=BOLD(28), fill=t.acc); y += 54
    y = th_title(t, M, y, c["answer"], start=72, minsize=42, maxlines=3)
    if c.get("sub"): th_sub(t, M, y + 6, c["sub"], W - 2 * M - 40)
    return th_end(t, c)

def x_reviewpost(c):
    t = theme(c); base = t.base; d = ImageDraw.Draw(base)
    y = th_kicker(t, M, 90, c.get("kicker"))
    y = th_title(t, M, y + 4, c["title"], start=74, minsize=44, maxlines=2) + 20
    for q in c["quotes"]:
        f2 = IM(40); ls = wrap("« " + q + " »", f2, W - 2 * M - 80); h = 96 + len(ls) * f2.size * 1.3
        phone_card(base, (M, y, W - M, y + h), 36); d = ImageDraw.Draw(base)
        for k in range(5):
            cx, cy, r = M + 50 + k * 46, y + 44, 18
            pts = [(cx + (r if j % 2 == 0 else r * 0.45) * math.cos(math.radians(-90 + j * 36)), cy + (r if j % 2 == 0 else r * 0.45) * math.sin(math.radians(-90 + j * 36))) for j in range(10)]
            d.polygon(pts, fill=(255, 190, 40))
        for i, l in enumerate(ls): d.text((M + 36, y + 78 + i * f2.size * 1.3), l, font=f2, fill=(30, 30, 30))
        y += h + 24
    d.text((M, y + 6), c.get("source", "Avis clients publiés sur la fiche produit, mot pour mot."), font=IM(30), fill=t.sub)
    return th_end(t, c)

TPLX = {"bignum": x_bignum, "quiz": x_quiz, "steps": x_steps, "mosaic": x_mosaic, "arch": x_arch, "tracker": x_tracker, "schema": x_schema,
        "callout": x_callout, "note": x_note, "fear": x_fear, "editorial": x_editorial,
        "ticket": x_ticket, "split": x_split, "offer": x_offer,
        "chatpost": x_chatpost, "notespost": x_notespost, "commentpost": x_commentpost, "reviewpost": x_reviewpost}

DA_B_ALL = "--da-b" in sys.argv     # aperçu : tout en DA B
DA_C_ALL = "--da-c" in sys.argv     # aperçu : tout en DA C
def pick_tpl(sl):
    """La DA vient du post ("a" v5, "b" dégradé, "c" carnet, "d" nuit, "e" pop).
    Les formats mixtes s'habillent seuls ; les six gabarits historiques retombent
    sur l'habillage le plus proche."""
    if sl["tpl"] in TPLX: return TPLX[sl["tpl"]]
    da = sl.get("da")
    if DA_C_ALL or da == "c": return TPL_C[sl["tpl"]]
    if da == "d": sl.setdefault("tone", "forest"); return TPL_B[sl["tpl"]]
    return (TPL_B if (DA_B_ALL or da == "b") else TPL)[sl["tpl"]]

# ───────────────────────────── Reels 1080x1920
RW, RH, FPS, XF = 1080, 1920, 30, 0.32   # transitions glissées : la scène suivante pousse la précédente

def ease(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3

# Clips vidéo libres de droits (Mixkit, licence gratuite pour usage commercial, sans attribution).
# Chaque nom pointe vers l'identifiant Mixkit du plan.
CLIPS = {
    "fille-matin": 48136, "ado-miroir": 48137, "peignoir": 48174, "ado-salle-de-bain": 48135, "fillette": 48134,
    "homme-miroir": 50758, "femme-brosse": 24705, "homme-gros-plan": 36105, "dentifrice": 48930,
    "sourire": 48173, "dentiste-geste": 8975, "dentiste-radio": 9027,
    "cafe-gorgee": 46568, "cafe-fumant": 43935, "valise-zip": 45509, "valise-timelapse": 45506,
    "valise-pliage": 45511, "valise-stopmotion": 46338, "chocolat": 10373,
}

def clip_path(name):
    os.makedirs(os.path.join(CACHE, "clips"), exist_ok=True)
    fn = os.path.join(CACHE, "clips", name + ".mp4")
    if os.path.exists(fn) and os.path.getsize(fn) > 10000: return fn
    vid = CLIPS[name]
    for q in ("720", "1080", "360"):
        try:
            req = urllib.request.Request(f"https://assets.mixkit.co/videos/{vid}/{vid}-{q}.mp4", headers={"User-Agent": "pulse-care-media/1.0"})
            data = urllib.request.urlopen(req, timeout=90).read()
            if len(data) > 10000: open(fn, "wb").write(data); return fn
        except Exception as e:
            print("clip", name, q, e)
    raise RuntimeError("clip introuvable : " + name)

class ClipBG:
    """Plan vidéo recadré en 9:16, lu image par image à la demande (boucle si trop court)."""
    def __init__(self, name, fx=0.5, speed=1.0):
        self.name, self.fx, self.speed, self.proc, self.idx, self.last = name, fx, speed, None, -1, None
    def _open(self):
        if FAKE: return
        src = clip_path(self.name)
        vf = (f"setpts=PTS/{self.speed},scale={RW}:{RH}:force_original_aspect_ratio=increase,"
              f"crop={RW}:{RH}:(iw-{RW})*{self.fx}:(ih-{RH})/2,fps={FPS}")
        self.proc = subprocess.Popen(["ffmpeg", "-v", "error", "-stream_loop", "-1", "-i", src, "-vf", vf, "-an",
                                      "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    def at(self, t):
        want = int(t * FPS)
        if FAKE:
            g = np.zeros((RH, RW, 3), np.uint8); g[..., 0] = 90 + int(60 * math.sin(t)); g[..., 1] = 120; g[..., 2] = 110 + int(40 * math.cos(t * 1.3))
            im = Image.fromarray(g); ImageDraw.Draw(im).ellipse([300 + 200 * math.sin(t * 2), 700, 800 + 200 * math.sin(t * 2), 1200], fill=(230, 220, 200)); return im
        if self.proc is None: self._open()
        while self.idx < want or self.last is None:
            buf = self.proc.stdout.read(RW * RH * 3)
            if len(buf) < RW * RH * 3: break
            self.last = Image.frombytes("RGB", (RW, RH), buf); self.idx += 1
        return self.last
    def close(self):
        if self.proc: self.proc.kill(); self.proc = None

def make_bg(ref, w=RW, h=RH, zoom=(1.0, 1.16), pan=(0.0, 0.15)):
    """Fond d'une scène : un clip (« clip:nom ») ou une photo animée."""
    if isinstance(ref, str) and ref.startswith("clip:"):
        name, _, fx = ref[5:].partition("@"); return ClipBG(name, float(fx) if fx else 0.5)
    return KenBurns(ref, w, h, zoom, pan)

def bg_at(bg, t, dur):
    return bg.at(t) if isinstance(bg, ClipBG) else bg.at(min(1, t / dur))
def ease_io(x): x = min(max(x, 0), 1); return 3 * x * x - 2 * x * x * x
def back(x, k=1.7):  # dépasse un peu sa cible puis revient : un rebond
    x = min(max(x, 0), 1); return 1 + (k + 1) * (x - 1) ** 3 + k * (x - 1) ** 2

class Layer:
    """Élément pré-rendu (RGBA), animé en opacité / translation."""
    def __init__(self, im, x, y, t0, dur=0.3, dx=0, dy=40):
        self.im, self.x, self.y, self.t0, self.dur, self.dx, self.dy = im, x, y, t0, dur, dx, dy
        self.arr = np.array(im); self.txt = bool(im.info.get("txt"))
    def draw(self, frame, t):
        q = (t - self.t0) / self.dur
        if q <= 0: return
        p = back(q); o = ease(q * 1.6)
        a = self.arr.copy(); a[..., 3] = (a[..., 3] * min(1, o)).astype(np.uint8)
        pos = (int(self.x + self.dx * (1 - p)), int(self.y + self.dy * (1 - p)))
        if self.txt: safe_composite(frame, Image.fromarray(a, "RGBA"), pos)
        else: frame.alpha_composite(Image.fromarray(a, "RGBA"), pos)

def text_layer(lines, fnt, fill, lh=1.15, w=RW - 140, center=False):
    h = int(text_h(lines, fnt, lh) + fnt.size * 0.4)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    y = 0
    for l in lines:
        x = (w - d.textlength(l, font=fnt)) / 2 if center else 0
        d.text((x, y), l, font=fnt, fill=fill); y += fnt.size * lh
    im.info["txt"] = 1
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

# Palettes des vidéos : une par vidéo, pour que deux vidéos ne se ressemblent pas.
PALS = {
    "foret":  dict(bg=(18, 36, 29),  bg2=(30, 58, 47),   ink=(243, 238, 228), acc=(196, 158, 98), sub=(198, 214, 204), mark=(196, 158, 98), pop=(196, 158, 98)),
    "nuit":   dict(bg=(11, 21, 17),  bg2=(26, 42, 34),   ink=(243, 238, 228), acc=(214, 240, 120), sub=(176, 200, 186), mark=(214, 240, 120), pop=(214, 240, 120)),
    "corail": dict(bg=(178, 62, 50), bg2=(156, 50, 40), ink=(255, 247, 240), acc=(255, 214, 120),   sub=(255, 228, 220), mark=(255, 214, 120), pop=(240, 122, 104)),
    "ocre":   dict(bg=(233, 172, 74), bg2=(216, 152, 56), ink=(16, 28, 22),   acc=(24, 52, 40),   sub=(70, 60, 30),    mark=(16, 28, 22), pop=(240, 182, 84)),
    "creme":  dict(bg=(246, 241, 232), bg2=(221, 232, 223), ink=(18, 36, 29), acc=(176, 60, 48), sub=(74, 88, 80),    mark=(176, 60, 48), pop=(246, 241, 232)),
    "lime":   dict(bg=(214, 240, 120), bg2=(194, 222, 98), ink=(16, 28, 22),  acc=(24, 52, 40),   sub=(52, 70, 44),    mark=(24, 52, 40), pop=(214, 240, 120)),
}

def kinetic_words(text, fnt, maxw):
    """Découpe en lignes et renvoie [(ligne, [(mot, x)])] pour une apparition mot par mot."""
    d = ImageDraw.Draw(Image.new("L", (1, 1))); out = []
    for ln in wrap(text, fnt, maxw):
        x = 0; ws = []
        for w_ in ln.split(" "):
            ws.append((w_, x)); x += d.textlength(w_ + " ", font=fnt)
        out.append((ln, ws, d.textlength(ln, font=fnt)))
    return out

def hl_spans(title):
    """Indices (dans le titre sans astérisques) des caractères à surligner."""
    out, idx, on = set(), 0, False
    for ch in title:
        if ch == "*": on = not on; continue
        if on: out.add(idx)
        idx += 1
    return out

class HL:
    """Suit la position de chaque mot affiché dans le titre, pour surligner exactement les mots entre astérisques."""
    def __init__(self, title):
        self.clean = title.replace("*", ""); self.spans = hl_spans(title); self.cur = 0
    def reset(self): self.cur = 0
    def __call__(self, word):
        w = word.replace("\u00a0", " "); i = self.clean.find(w, self.cur)
        if i < 0: return False
        self.cur = i + len(w)
        core = [k for k in range(i, i + len(w)) if self.clean[k].isalnum()]
        return bool(core) and all(k in self.spans for k in core)

def kinetic_draw(f, t, lines, fnt, x0, y0, hl, ink, mark, markink, step=0.06):
    d = ImageDraw.Draw(f); k = 0; y = y0; hl.reset()
    for ln, ws, lw in lines:
        for w_, x in ws:
            q = back((t - k * step) / 0.3); k += 1
            if q <= 0: continue
            col = ink
            if hl(w_):
                ww = d.textlength(w_, font=fnt)
                d.rounded_rectangle([x0 + x - 10, y + 40 * (1 - q) + fnt.size * 0.14, x0 + x + ww * min(1, q) + 10, y + 40 * (1 - q) + fnt.size * 1.04], radius=12, fill=mark)
                col = markink
            lay = Image.new("RGBA", (int(d.textlength(w_, font=fnt)) + 10, int(fnt.size * 1.3)), (0, 0, 0, 0))
            ImageDraw.Draw(lay).text((0, 0), w_, font=fnt, fill=col + (int(255 * min(1, q)),))
            safe_composite(f, lay, (int(x0 + x), int(y + 40 * (1 - q))))
        y += fnt.size * 1.04

HL_SCENES = {'hook', 'burst', 'card', 'grid', 'comment'}   # scènes qui savent surligner les *marques*

class Scene:
    def __init__(self, c, idx, pal=None):
        self.c, self.dur, self.idx = c, c["dur"], idx
        if c["t"] not in HL_SCENES:   # ces scènes n'ont pas de surlignage : on retire les *marques*
            c = self.c = {k: (v.replace("*", "") if isinstance(v, str) else v) for k, v in c.items()}
        self.P = PALS.get(pal or c.get("pal") or "foret", PALS["foret"])
        self.kb = None
        bgref = c.get("clip") and "clip:" + c["clip"] or (c.get("img") if c["t"] not in ("photo", "split", "card") else None)
        if bgref:
            # Fond filmé ou photo : la vraie vie plutôt qu'un aplat. Texte clair, accents de la palette.
            self.kb = make_bg(bgref, RW, RH, (1.0, 1.16), ((-1) ** idx * 0.5, 0.15))
            self.shade = Image.new("RGBA", (RW, RH), (8, 16, 12, 92))
            self.shade.alpha_composite(gradient(RW, RH, (8, 16, 12), 0.25, 1.0, 0, 175))
            self.shade.alpha_composite(gradient(RW, 260, (8, 16, 12), 0, 1, 110, 0), (0, 0))
            pop = self.P["pop"]
            self.P = dict(self.P, ink=(250, 247, 240), sub=(226, 232, 226), acc=pop, bg=(16, 28, 22), bg2=(250, 247, 240), mark=pop)
        getattr(self, "setup_" + c["t"])()
    def bgframe(self, t, alt=False):
        if self.kb:
            f = bg_at(self.kb, t, self.dur).convert("RGBA"); f.alpha_composite(self.shade); return f
        P = self.P; f = Image.new("RGBA", (RW, RH), (P["bg2"] if alt else P["bg"]) + (255,))
        d = ImageDraw.Draw(f)  # grand disque qui respire, pour que le fond ne soit jamais figé
        r = 560 + 30 * math.sin(t * 1.3 + self.idx); cx = RW * (1.08 if self.idx % 2 else -0.08); cy = RH * (0.06 if self.idx % 2 else 0.96)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(P["bg2"] if not alt else P["bg"]) + (255,))
        return f
    def brand(self, f): pass   # pas de logo en haut à gauche des vidéos

    # accroche : typographie plein écran, mot par mot
    def setup_hook(self):
        c = self.c; self.f = BLACK(132 if len(c["title"]) < 34 else 112)
        self.lines = kinetic_words(c["title"].replace("*", ""), self.f, RW - 150)
        self.hl = HL(c["title"])
        h = len(self.lines) * self.f.size * 1.04
        self.y0 = (RH - h) / 2 - 40
        self.layers = []
        if c.get("kicker"): self.layers.append(Layer(pill_layer(c["kicker"].upper(), MED(30), self.P["acc"], self.P["bg"]), 75, self.y0 - 110, 0.05, dx=-60, dy=0))
        if c.get("sub"):
            sl = wrap(c["sub"], REG(44), RW - 150)
            self.layers.append(Layer(text_layer(sl, REG(46), self.P["sub"], 1.3), 75, self.y0 + h + 50, 0.15 + 0.06 * sum(len(w) for _, w, _ in self.lines), dy=30))
    def frame_hook(self, t):
        f = self.bgframe(t); d = ImageDraw.Draw(f); self.brand(f)
        k = 0; y = self.y0; self.hl.reset()
        for ln, ws, lw in self.lines:
            for w_, x in ws:
                p = ease((t - 0.08 - k * 0.06) / 0.2); k += 1
                if p <= 0: continue
                col = self.P["ink"]
                if self.hl(w_):
                    ww = d.textlength(w_ + (" " if w_ != ws[-1][0] else ""), font=self.f)
                    d.rectangle([75 + x - 8, y + 40 * (1 - p) + self.f.size * 0.18, 75 + x + ww * p + 8, y + 40 * (1 - p) + self.f.size * 1.02], fill=self.P["mark"])
                    col = self.P["bg"] if self.P["mark"] != self.P["ink"] else self.P["bg"]
                lay = Image.new("RGBA", (int(d.textlength(w_, font=self.f)) + 10, int(self.f.size * 1.3)), (0, 0, 0, 0))
                ImageDraw.Draw(lay).text((0, 0), w_, font=self.f, fill=col + (int(255 * p),))
                safe_composite(f, lay, (int(75 + x), int(y + 40 * (1 - p))))
            y += self.f.size * 1.04
        for l in self.layers: l.draw(f, t)
        return f

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
            self.layers.append(Layer(pill_layer(c["kicker"].upper(), MED(30), self.P["acc"] if self.P["acc"] != (16, 28, 22) else BAMBOO, DEEP), 70, y - 100, 0.15, dx=-80, dy=0))
        for i, l in enumerate(tl):
            self.layers.append(Layer(text_layer([l], tf, CREAM), 70, y + i * tf.size * 1.15, 0.3 + i * 0.12))
        y += text_h(tl, tf)
        if sl: self.layers.append(Layer(text_layer(sl, REG(42), (226, 232, 226), 1.35), 70, y + 30, 0.75, dy=30))
    def frame_photo(self, t):
        f = self.kb.at(t / self.dur).convert("RGBA"); f.alpha_composite(self.grad)
        for l in self.layers: l.draw(f, t)
        return f

    # moitié photo / moitié panneau
    def setup_split(self):
        c = self.c; P = self.P
        self.kb = KenBurns(c["img"], RW, 1060, (1.04, 1.14), (0.3, 0.0))
        self.top_grad = gradient(RW, 300, DEEP, 0, 1, 130, 0)
        self.layers = [Layer(pill_layer(c["kicker"].upper(), MED(30), P["acc"], P["bg"]), 70, 1080, 0.35, dx=-60, dy=0)]
        y = 1190
        for i, (a_, b_) in enumerate(c["items"]):
            im = Image.new("RGBA", (RW - 140, 230), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            d.ellipse([0, 10, 60, 70], fill=P["acc"]); d.text((15, 14), "→", font=ARR(34), fill=P["bg"])
            yy = draw_lines(d, 90, 0, wrap(a_, BOLD(52), RW - 240), BOLD(52), P["ink"], 1.12)
            if b_: draw_lines(d, 90, yy + 4, wrap(b_, REG(38), RW - 240), REG(38), P["sub"], 1.3)
            self.layers.append(Layer(im, 70, y, 0.6 + i * 0.35, dx=80, dy=0)); y += 250
    def frame_split(self, t):
        f = Image.new("RGBA", (RW, RH), self.P["bg"] + (255,))
        f.paste(self.kb.at(t / self.dur), (0, 0)); f.alpha_composite(self.top_grad, (0, 0))
        p = ease(t / 0.55); top = int(RH - (RH - 1000) * p)
        ImageDraw.Draw(f).rounded_rectangle([0, top, RW, RH + 60], radius=60, fill=self.P["bg"])
        for l in self.layers: l.draw(f, t)
        return f

    # liste : gros intitulés qui arrivent un par un, centrés dans l'écran
    def setup_list(self):
        c = self.c; P = self.P; blocks = []
        for i, (a_, b_) in enumerate(c["items"]):
            fa = BLACK(118 if len(c["items"]) == 1 else 92)
            im = Image.new("RGBA", (RW - 150, 520), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            yy = draw_lines(d, 0, 0, wrap(nb(a_), fa, RW - 150), fa, P["ink"], 1.04)
            if b_: yy = draw_lines(d, 0, yy + 14, wrap(b_, REG(50), RW - 150), REG(50), P["sub"], 1.3)
            blocks.append(im.crop((0, 0, RW - 150, int(yy) + 16)))
        gap = 90; total = sum(b_.height for b_ in blocks) + gap * (len(blocks) - 1) + 120
        y = (RH - total) / 2 + 60
        self.layers = [Layer(pill_layer(c["kicker"].upper(), MED(30), P["acc"], P["bg"]), 75, y - 60, 0.05, dx=-60, dy=0)]
        y += 60
        span = max(0.3, min(0.9, (self.dur - 1.0) / max(1, len(blocks))))
        for i, im in enumerate(blocks):
            self.layers.append(Layer(im, 75, y, 0.25 + i * span, dx=0, dy=60)); y += im.height + gap
        self.bar = (y - 60 - (RH - total) / 2)
    def frame_list(self, t):
        f = self.bgframe(t); d = ImageDraw.Draw(f)
        self.brand(f)
        for l in self.layers: l.draw(f, t)
        return f

    # compteur animé
    def setup_counter(self):
        c = self.c; P = self.P
        self.layers = [Layer(text_layer(wrap(c["kicker"].upper(), MED(40), RW - 160), MED(40), P["acc"] if P["acc"] != P["bg"] else P["ink"], center=True), 70, 470, 0.1, dy=30),
                       Layer(text_layer(wrap(c["label"], MED(54), RW - 160), MED(54), P["ink"], center=True), 70, 1330, 1.2, dy=40)]
    def frame_counter(self, t):
        c = self.c; P = self.P
        f = self.bgframe(t, alt=True); d = ImageDraw.Draw(f)
        r = 300 + 40 * ease(t / 1.5)
        d.ellipse([RW / 2 - r, 940 - r, RW / 2 + r, 940 + r], outline=P["mark"], width=6)
        v = int(round(c["value"] * ease(t / 1.6)))
        s_ = f"{v:,}".replace(",", " ") + c.get("suffix", "")
        fnt = BLACK(230 if len(s_) < 6 else (180 if len(s_) < 8 else 150))
        tw = d.textlength(s_, font=fnt); d.text(((RW - tw) / 2, 940 - fnt.size * 0.62), s_, font=fnt, fill=P["ink"])
        self.brand(f)
        for l in self.layers: l.draw(f, t)
        return f

    # minuteur circulaire
    def setup_timer(self):
        c = self.c; P = self.P
        self.layers = [Layer(text_layer([c["kicker"].upper()], MED(38), P["acc"] if P["acc"] != P["bg"] else P["ink"], center=True), 70, 420, 0.1, dy=30),
                       Layer(text_layer([nb(c["title"])], BLACK(120), P["ink"], center=True), 70, 880, 0.3, dy=40),
                       Layer(text_layer(wrap(c["sub"], REG(44), RW - 200), REG(44), P["sub"], 1.35, center=True), 70, 1450, 0.8, dy=30)]
    def frame_timer(self, t):
        P = self.P; f = self.bgframe(t); d = ImageDraw.Draw(f)
        cx, cy, r = RW / 2, 960, 360
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=P["bg2"], width=26)
        p = ease_io(t / (self.dur - 0.3))
        d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * p, fill=P["mark"], width=26)
        for q in range(4):
            a_ = math.radians(-90 + q * 90); on = p >= q / 4 + 0.001
            x, y = cx + r * math.cos(a_), cy + r * math.sin(a_)
            d.ellipse([x - 24, y - 24, x + 24, y + 24], fill=P["ink"] if on else P["bg2"])
        self.brand(f)
        for l in self.layers: l.draw(f, t)
        return f

    # comparatif 2 colonnes
    def setup_compare(self):
        c = self.c; P = self.P; cw = (RW - 170) // 2; self.layers = []
        for i, (head, rows) in enumerate([c["left"], c["right"]]):
            dark = i == 1
            im = Image.new("RGBA", (cw, 860), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            d.rounded_rectangle([0, 0, cw, 860], radius=44, fill=P["ink"] if dark else P["bg2"])
            d.text((40, 50), head, font=BLACK(56), fill=P["bg"] if dark else P["ink"])
            y = 190
            for r_ in rows:
                y = draw_lines(d, 40, y, wrap(("+ " if dark else "× ") + nb(r_), MED(46), cw - 80), MED(46), P["bg"] if dark else P["sub"], 1.3) + 40
            self.layers.append(Layer(im, 70 + i * (cw + 30), 560, 0.2 + i * 0.6, dx=(-120 if i == 0 else 120), dy=0))
    def frame_compare(self, t):
        f = self.bgframe(t); self.brand(f)
        for l in self.layers: l.draw(f, t)
        return f

    # carton de fin
    def setup_end(self):
        c = self.c; P = self.P
        tl = wrap(c["title"], BLACK(92), RW - 160)
        self.layers = [Layer(text_layer(tl, BLACK(92), P["ink"], 1.06, RW - 160, True), 80, 800, 0.35, dy=40),
                       Layer(text_layer([c.get("sub", "")], MED(42), P["acc"] if P["acc"] != P["bg"] else P["ink"], center=True), 70, 800 + text_h(tl, BLACK(92), 1.06) + 80, 0.75, dy=20)]
    def frame_end(self, t):
        P = self.P; f = self.bgframe(t, alt=True); d = ImageDraw.Draw(f)
        s_ = 0.9 + 0.1 * ease(t / 0.6)
        fnt = MED(int(64 * s_)); tw = d.textlength("PULSE CARE", font=fnt)
        x = (RW - tw) / 2 + 30
        d.ellipse([x - 64 * s_, 560 + 20 * s_, x - 30 * s_, 560 + 54 * s_], fill=P["mark"])
        d.text((x, 560), "PULSE CARE", font=fnt, fill=P["ink"])
        ln = 180 * ease((t - 0.2) / 0.6); d.line([(RW / 2 - ln / 2, 690), (RW / 2 + ln / 2, 690)], fill=P["mark"], width=5)
        for l in self.layers: l.draw(f, t)
        return f
    # rafale : 2 à 4 photos coupées sec, zoom « punch » à chaque coupe, légende en bas
    def setup_burst(self):
        c = self.c; P = self.P
        self.kbs = [make_bg(r_, RW, RH, (1.18, 1.02), ((-1) ** i * 0.4, 0.1)) for i, r_ in enumerate(c["shots"])]
        self.shade = gradient(RW, RH, (8, 16, 12), 0.5, 1.0, 0, 225)
        self.shade.alpha_composite(gradient(RW, 320, (8, 16, 12), 0, 1, 140, 0), (0, 0))
        title = c["title"]; self.f = BLACK(108 if len(title) < 28 else 90)
        self.lines = kinetic_words(title.replace("*", ""), self.f, RW - 150)
        self.hl = HL(title)
        self.y0 = RH - 330 - len(self.lines) * self.f.size * 1.04
        pop = P["pop"]; self.P = dict(P, ink=(250, 247, 240), mark=pop, bg=(16, 28, 22))
        self.layers = [Layer(pill_layer(c["kicker"].upper(), MED(30), pop, (16, 28, 22)), 75, self.y0 - 100, 0.05, dx=-60, dy=0)] if c.get("kicker") else []
    def frame_burst(self, t):
        n = len(self.kbs); seg = self.dur / n; i = min(n - 1, int(t / seg)); lt = (t - i * seg) / seg
        kb = self.kbs[i]
        f = (kb.at(lt * seg) if isinstance(kb, ClipBG) else kb.at(min(1.0, 0.65 * ease(lt * 4) + 0.35 * lt))).convert("RGBA")
        if i > 0 and lt * seg < 0.08:  # éclair blanc très bref à la coupe
            f.alpha_composite(Image.new("RGBA", (RW, RH), (255, 255, 255, int(150 * (1 - lt * seg / 0.08)))))
        f.alpha_composite(self.shade)
        d = ImageDraw.Draw(f); k = 0; y = self.y0; self.hl.reset()
        for ln, ws, lw in self.lines:
            for w_, x in ws:
                p = ease((t - 0.05 - k * 0.05) / 0.18); k += 1
                if p <= 0: continue
                col = self.P["ink"]
                if self.hl(w_):
                    ww = d.textlength(w_ + (" " if w_ != ws[-1][0] else ""), font=self.f)
                    d.rectangle([75 + x - 8, y + 30 * (1 - p) + self.f.size * 0.18, 75 + x + ww * p + 8, y + 30 * (1 - p) + self.f.size * 1.02], fill=self.P["mark"])
                    col = (16, 28, 22)
                lay = Image.new("RGBA", (int(d.textlength(w_, font=self.f)) + 10, int(self.f.size * 1.3)), (0, 0, 0, 0))
                ImageDraw.Draw(lay).text((0, 0), w_, font=self.f, fill=col + (int(255 * p),))
                safe_composite(f, lay, (int(75 + x), int(y + 30 * (1 - p))))
            y += self.f.size * 1.04
        for l in self.layers: l.draw(f, t)
        return f

    # carte : la photo dans une carte qui arrive en rebond, inclinée, sur un fond de couleur qui bouge
    def setup_card(self):
        c = self.c; P = self.P
        cw, ch = 860, 980
        self.cardclip = ClipBG(c["clip"]) if c.get("clip") else None
        ph = cover(load(c["img"]), cw, ch, 0.5, c.get("fy", 0.45)).convert("RGBA") if c.get("img") else Image.new("RGBA", (cw, ch), (200, 200, 200, 255))
        m = Image.new("L", (cw, ch), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, cw, ch], radius=56, fill=255)
        frame_ = Image.new("RGBA", (cw + 28, ch + 28), (255, 255, 255, 255))
        mm = Image.new("L", frame_.size, 0); ImageDraw.Draw(mm).rounded_rectangle([0, 0, frame_.width, frame_.height], radius=68, fill=255)
        frame_.putalpha(mm); frame_.paste(ph, (14, 14), m)
        self.card = frame_; self.tilt = -5 if self.idx % 2 else 5; self.cmask = m; self.cwh = (cw, ch)
        self.shadow = Image.new("RGBA", (frame_.width + 120, frame_.height + 120), (0, 0, 0, 0))
        ImageDraw.Draw(self.shadow).rounded_rectangle([60, 80, frame_.width + 60, frame_.height + 80], radius=68, fill=(0, 0, 0, 90))
        self.shadow = self.shadow.filter(ImageFilter.GaussianBlur(28))
        tf = BLACK(92 if len(c["title"]) < 30 else 78)
        self.f = tf; self.lines = kinetic_words(c["title"].replace("*", ""), tf, RW - 150); self.hl = HL(c["title"])
        self.y0 = 150 if c.get("kicker") else 120
        self.layers = []
        if c.get("kicker"): self.layers.append(Layer(pill_layer(c["kicker"].upper(), MED(30), P["acc"], P["bg"]), 75, self.y0 - 20, 0.0, dx=-80, dy=0)); self.y0 += 70
        self.cy = self.y0 + len(self.lines) * tf.size * 1.04 + 40
        if c.get("sub"):
            self.layers.append(Layer(text_layer(wrap(c["sub"], REG(44), RW - 160), REG(44), P["ink"], 1.3, RW - 160, True), 80, RH - 250, 0.55, dy=40))
    def frame_card(self, t):
        P = self.P; f = Image.new("RGBA", (RW, RH), P["bg"] + (255,)); d = ImageDraw.Draw(f)
        for k_ in range(3):  # trois formes qui dérivent
            r = 260 + 90 * k_; ang = t * (0.6 + 0.25 * k_) + k_ * 2.1
            cx = RW * (0.5 + 0.42 * math.cos(ang)); cy = RH * (0.55 + 0.35 * math.sin(ang * 0.8))
            d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=P["bg2"])
        self.brand(f)
        p = back((t - 0.15) / 0.55); o = min(1, ease((t - 0.15) / 0.3))
        if o > 0:
            sc = 0.82 + 0.18 * p; ang = self.tilt * (1 - p) + self.tilt * 0.35 + math.sin(t * 1.4) * 0.8
            if self.cardclip:  # le clip joue à l'intérieur de la carte
                fr_ = self.cardclip.at(t).resize((RW, RH)); cw, ch = self.cwh
                fr_ = fr_.crop(((RW - cw * RH / ch) / 2, 0, (RW + cw * RH / ch) / 2, RH)).resize((cw, ch))
                self.card.paste(fr_, (14, 14), self.cmask)
            cd = self.card.resize((int(self.card.width * sc), int(self.card.height * sc)), Image.BILINEAR).rotate(ang, Image.BICUBIC, expand=True)
            sh = self.shadow.resize((int(self.shadow.width * sc), int(self.shadow.height * sc))).rotate(ang, Image.BICUBIC, expand=True)
            cx = RW / 2 + 22 * math.sin(t * 0.9); cy = self.cy + cd.height / 2 + 140 * (1 - p)
            if o < 1: cd.putalpha(cd.getchannel("A").point(lambda v: int(v * o)))
            f.alpha_composite(sh, (int(cx - sh.width / 2), int(cy - sh.height / 2)))
            f.alpha_composite(cd, (int(cx - cd.width / 2), int(cy - cd.height / 2)))
        d = ImageDraw.Draw(f); k = 0; y = self.y0; self.hl.reset()
        for ln, ws, lw in self.lines:
            for w_, x in ws:
                q = back((t - 0.05 - k * 0.06) / 0.3); k += 1
                if q <= 0: continue
                col = P["ink"]
                if self.hl(w_):
                    ww = d.textlength(w_, font=self.f)
                    d.rounded_rectangle([75 + x - 10, y + 50 * (1 - q) + self.f.size * 0.14, 75 + x + ww * min(1, q) + 10, y + 50 * (1 - q) + self.f.size * 1.04], radius=14, fill=P["mark"])
                    col = P["bg"]
                lay = Image.new("RGBA", (int(d.textlength(w_, font=self.f)) + 10, int(self.f.size * 1.3)), (0, 0, 0, 0))
                ImageDraw.Draw(lay).text((0, 0), w_, font=self.f, fill=col + (int(255 * min(1, q)),))
                safe_composite(f, lay, (int(75 + x), int(y + 50 * (1 - q))))
            y += self.f.size * 1.04
        for l in self.layers: l.draw(f, t)
        return f

    # grille : 2 à 4 photos qui pop une par une, titre en haut
    def setup_grid(self):
        c = self.c; P = self.P; shots = c["shots"][:4]; n = len(shots)
        cols = 2; rows_ = (n + 1) // 2; gap = 26; top = 470
        cw = (RW - 2 * 70 - gap) // 2; chh = min(560, (RH - top - 200 - gap * (rows_ - 1)) // rows_)
        self.tiles = []
        for i, r_ in enumerate(shots):
            w = cw if not (n == 3 and i == 2) else RW - 140
            im = cover(load(r_), w, chh, 0.5, 0.45).convert("RGBA")
            m = Image.new("L", (w, chh), 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, w, chh], radius=36, fill=255); im.putalpha(m)
            x = 70 + (i % cols) * (cw + gap) if not (n == 3 and i == 2) else 70; y = top + (i // cols) * (chh + gap)
            self.tiles.append((im, x, y, 0.2 + i * 0.22))
        tf = BLACK(84 if len(c["title"]) < 30 else 70)
        self.f = tf; self.lines = kinetic_words(c["title"].replace("*", ""), tf, RW - 150); self.hl = HL(c["title"])
        self.layers = [Layer(pill_layer(c["kicker"].upper(), MED(30), P["acc"], P["bg"]), 75, 170, 0.0, dx=-80, dy=0)] if c.get("kicker") else []
        self.labels = c.get("labels", [])
    def frame_grid(self, t):
        P = self.P; f = self.bgframe(t); self.brand(f); d = ImageDraw.Draw(f)
        for i, (im, x, y, t0) in enumerate(self.tiles):
            q = (t - t0) / 0.42
            if q <= 0: continue
            sc = 0.55 + 0.45 * back(q); w, h = int(im.width * sc), int(im.height * sc)
            tile = im.resize((max(1, w), max(1, h)), Image.BILINEAR)
            f.alpha_composite(tile, (int(x + (im.width - w) / 2), int(y + (im.height - h) / 2 + 6 * math.sin(t * 2 + i))))
            if i < len(self.labels) and q > 0.8:
                pl = pill_layer(self.labels[i].upper(), MED(28), P["mark"], P["bg"]); f.alpha_composite(pl, (x + 18, y + im.height - pl.height - 18))
        k = 0; y = 250; self.hl.reset()
        for ln, ws, lw in self.lines:
            for w_, x in ws:
                q = back((t - 0.05 - k * 0.06) / 0.3); k += 1
                if q <= 0: continue
                col = P["ink"]
                if self.hl(w_):
                    ww = d.textlength(w_, font=self.f)
                    d.rounded_rectangle([75 + x - 10, y + 40 * (1 - q) + self.f.size * 0.14, 75 + x + ww * min(1, q) + 10, y + 40 * (1 - q) + self.f.size * 1.04], radius=12, fill=P["mark"])
                    col = P["bg"]
                lay = Image.new("RGBA", (int(d.textlength(w_, font=self.f)) + 10, int(self.f.size * 1.3)), (0, 0, 0, 0))
                ImageDraw.Draw(lay).text((0, 0), w_, font=self.f, fill=col + (int(255 * min(1, q)),))
                safe_composite(f, lay, (int(75 + x), int(y + 40 * (1 - q))))
            y += self.f.size * 1.04
        for l in self.layers: l.draw(f, t)
        return f

    # POV : plan filmé + texte natif en haut, comme un créateur qui poste
    def setup_pov(self):
        c = self.c; f_ = BOLD(58); lines = wrap(c["title"], f_, RW - 220)
        w = max(ImageDraw.Draw(Image.new("L", (1, 1))).textlength(l, font=f_) for l in lines) + 60
        h = len(lines) * f_.size * 1.22 + 40
        box = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0)); d = ImageDraw.Draw(box)
        d.rounded_rectangle([0, 0, w, h], radius=22, fill=(255, 255, 255, 245))
        for i, l in enumerate(lines):
            d.text(((w - d.textlength(l, font=f_)) / 2, 18 + i * f_.size * 1.22), l, font=f_, fill=(16, 16, 16))
        self.box = box; self.layers = []
        if c.get("sub"):
            self.layers.append(Layer(text_layer(wrap(c["sub"], BOLD(54), RW - 160), BOLD(54), (255, 255, 255), 1.2, RW - 160, True), 80, RH - 520, 0.9, dy=40))
        self.shade = gradient(RW, RH, (8, 16, 12), 0.6, 1.0, 0, 200)
    def frame_pov(self, t):
        f = self.bgframe(t)
        q = back(t / 0.35); bw, bh = int(self.box.width * (0.7 + 0.3 * q)), int(self.box.height * (0.7 + 0.3 * q))
        if q > 0: f.alpha_composite(self.box.resize((max(1, bw), max(1, bh))), (int((RW - bw) / 2), int(300 - (bh - self.box.height) / 2)))
        for l in self.layers: l.draw(f, t)
        return f

    # conversation SMS : les bulles arrivent une par une, avec « … » avant chaque réponse
    def setup_chat(self):
        c = self.c; self.msgs = []; fnt = IM(56); maxw = 840
        for side, txt in c["msgs"]:
            ls = wrap(txt, fnt, maxw - 80); w = max(ImageDraw.Draw(Image.new("L", (1, 1))).textlength(l, font=fnt) for l in ls) + 80
            h = len(ls) * fnt.size * 1.26 + 50
            im = Image.new("RGBA", (int(w), int(h)), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
            out = side == "out"; bg = (36, 96, 72) if out else (234, 234, 236); fg = (250, 247, 240) if out else (20, 20, 20)
            d.rounded_rectangle([0, 0, w, h], radius=48, fill=bg)
            for i, l in enumerate(ls): d.text((40, 20 + i * fnt.size * 1.26), l, font=fnt, fill=fg)
            self.msgs.append((out, im))
        n = len(self.msgs); span = max(0.6, (self.dur - 1.0) / n)
        self.times = [0.35 + i * span for i in range(n)]
    def frame_chat(self, t):
        c = self.c; P = self.P
        f = Image.new("RGBA", (RW, RH), P["bg"] + (255,)); d = ImageDraw.Draw(f)
        x0, y0, x1, y1 = 50, 150, RW - 50, RH - 120
        d.rounded_rectangle([x0, y0, x1, y1], radius=60, fill=(255, 255, 255))
        y = y0 + 220; items = []
        for (out, im), t0 in zip(self.msgs, self.times):
            if not out and t0 - 0.5 < t < t0:   # l'autre est en train d'écrire
                dots = Image.new("RGBA", (150, 86), (0, 0, 0, 0)); dd = ImageDraw.Draw(dots)
                dd.rounded_rectangle([0, 0, 150, 86], radius=40, fill=(234, 234, 236))
                for k in range(3):
                    a_ = 120 + int(100 * (0.5 + 0.5 * math.sin(t * 9 - k)))
                    dd.ellipse([30 + k * 34, 32, 52 + k * 34, 54], fill=(150, 150, 155, a_))
                items.append((False, dots, 1.0))
            elif t >= t0:
                items.append((out, im, back((t - t0) / 0.3)))
        total = sum(it[1].height + 30 for it in items); scroll = max(0, y + total - (y1 - 40))
        y -= scroll
        for out, im, q in items:
            sc = 0.6 + 0.4 * min(1.05, q); w, h = int(im.width * sc), int(im.height * sc)
            x = (x1 - 40 - w) if out else (x0 + 40)
            if y + im.height > y0 + 190:
                f.alpha_composite(im.resize((max(1, w), max(1, h))), (int(x), int(y + (im.height - h))))
            y += im.height + 30
        # en-tête redessiné par-dessus, pour que les bulles qui remontent passent dessous
        d = ImageDraw.Draw(f)
        d.rounded_rectangle([x0, y0, x1, y0 + 200], radius=60, fill=(255, 255, 255)); d.rectangle([x0, y0 + 120, x1, y0 + 200], fill=(255, 255, 255))
        d.rectangle([x0, y0 + 198, x1, y0 + 200], fill=(226, 226, 230))
        cx = RW / 2; d.ellipse([cx - 44, y0 + 30, cx + 44, y0 + 118], fill=(200, 204, 210))
        ini = c.get("contact", "?")[0].upper(); fi = BOLD(44); d.text((cx - d.textlength(ini, font=fi) / 2, y0 + 44), ini, font=fi, fill=(255, 255, 255))
        fn_ = IM(30); nm = c.get("contact", ""); d.text((cx - d.textlength(nm, font=fn_) / 2, y0 + 132), nm, font=fn_, fill=(40, 40, 40))
        return f

    # question reçue + réponse : une carte « commentaire » en haut, la réponse en grand dessous
    def setup_comment(self):
        c = self.c; fnt = IM(46); ls = wrap(c["comment"], fnt, RW - 300)
        h = 120 + len(ls) * fnt.size * 1.3; card = Image.new("RGBA", (RW - 140, int(h)), (0, 0, 0, 0)); d = ImageDraw.Draw(card)
        d.rounded_rectangle([0, 0, RW - 140, h], radius=36, fill=(255, 255, 255, 250))
        d.ellipse([30, 30, 100, 100], fill=(210, 214, 218))
        d.text((120, 32), c.get("who", "Une question qu'on reçoit souvent"), font=BOLD(30), fill=(30, 30, 30))
        for i, l in enumerate(ls): d.text((120, 80 + i * fnt.size * 1.3), l, font=fnt, fill=(30, 30, 30))
        self.card = card
        tf = BLACK(96 if len(c["title"]) < 30 else 80); self.f = tf
        self.lines = kinetic_words(c["title"].replace("*", ""), tf, RW - 150); self.hl = HL(c["title"])
        self.y0 = RH - 360 - len(self.lines) * tf.size * 1.04
        self.layers = [Layer(text_layer(wrap(c["sub"], REG(42), RW - 160), REG(42), self.P["sub"] if self.kb else self.P["ink"], 1.3), 75, RH - 330, 1.0, dy=30)] if c.get("sub") else []
    def frame_comment(self, t):
        f = self.bgframe(t); self.brand(f); P = self.P
        q = back(t / 0.4)
        if q > 0:
            w, h = int(self.card.width * (0.75 + 0.25 * q)), int(self.card.height * (0.75 + 0.25 * q))
            f.alpha_composite(self.card.resize((max(1, w), max(1, h))), (int((RW - w) / 2), int(230 - 80 * (1 - q))))
        kinetic_draw(f, t - 0.6, self.lines, self.f, 75, self.y0, self.hl, P["ink"], P["mark"], P["bg"])
        for l in self.layers: l.draw(f, t)
        return f

    # avis client : étoiles qui se remplissent, citation qui s'écrit
    def setup_review(self):
        c = self.c; self.qf = BLACK(78); self.q = c["quote"]
        self.layers = [Layer(pill_layer(c.get("kicker", "Avis vérifié").upper(), MED(30), self.P["mark"], self.P["bg"]), 75, 300, 0.0, dx=-60, dy=0)]
    def frame_review(self, t):
        P = self.P; f = self.bgframe(t); self.brand(f); d = ImageDraw.Draw(f)
        for k in range(5):  # étoiles
            q = back((t - 0.2 - k * 0.12) / 0.3)
            if q <= 0: continue
            cx, cy, r = 130 + k * 120, 470, 46 * min(1.1, q)
            pts = [(cx + (r if j % 2 == 0 else r * 0.45) * math.cos(math.radians(-90 + j * 36)), cy + (r if j % 2 == 0 else r * 0.45) * math.sin(math.radians(-90 + j * 36))) for j in range(10)]
            d.polygon(pts, fill=(255, 196, 46))
        n = int(max(0, (t - 0.9)) * 28); txt = "« " + self.q[:n] + (" »" if n >= len(self.q) else "")
        ls = wrap(txt, self.qf, RW - 150); y = 600
        for l in ls: d.text((75, y), l, font=self.qf, fill=P["ink"]); y += self.qf.size * 1.12
        if n >= len(self.q):
            d.text((75, y + 30), self.c.get("source", "Avis client publié sur la fiche produit"), font=IM(36), fill=P["sub"])
        for l in self.layers: l.draw(f, t)
        return f

    # notes : une liste qui s'écrit ligne par ligne, comme dans l'appli Notes du téléphone
    def setup_notes(self):
        self.title = self.c["title"]; self.items = self.c["items"]
        span = max(0.4, (self.dur - 0.9) / max(1, len(self.items)))
        self.times = [0.35 + i * span for i in range(len(self.items))]
        self.cps = max(40, max(len(x) for x, _ in self.items) / (span * 0.7))   # vitesse de frappe : chaque ligne finit avant la suivante
    def frame_notes(self, t):
        f = Image.new("RGBA", (RW, RH), (252, 250, 243, 255)); d = ImageDraw.Draw(f)
        d.text((60, 120), "‹ Notes", font=MED(40), fill=(214, 160, 20))
        d.text((60, 260), self.title, font=BLACK(96), fill=(20, 20, 20))
        y = 460; fnt = IM(66)
        for (txt, mode), t0 in zip(self.items, self.times):
            if t < t0: break
            n = int((t - t0) * self.cps); shown = txt[:n]
            bold = mode == "total"; fx = BLACK(80) if bold else fnt
            if bold: d.line([60, y - 10, RW - 60, y - 10], fill=(210, 205, 190), width=3); y += 10
            d.text((60, y), ("" if bold else "– ") + shown, font=fx, fill=(20, 20, 20) if mode != "barre" else (140, 140, 140))
            if mode == "barre" and n >= len(txt):
                w = d.textlength("– " + txt, font=fx); p = ease((t - t0 - len(txt) / self.cps) / 0.3)
                d.line([60, y + fx.size * 0.62, 60 + w * p, y + fx.size * 0.62], fill=(226, 108, 92), width=7)
            y += fx.size * 1.5
        if int(t * 2) % 2 == 0: d.rectangle([60, y + 6, 64, y + 60], fill=(214, 160, 20))   # curseur
        return f

    def frame(self, t):
        return getattr(self, "frame_" + self.c["t"])(t)

SCENE_V = "11"   # à incrémenter quand le dessin des scènes change : force le re-rendu des vidéos

def audio_len(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                       capture_output=True, text=True)
    return float(r.stdout.strip())

def fit_scenes(scenes_spec, total):
    """Répartit la durée de la voix entre les scènes, au prorata de la phrase lue sur chacune."""
    w = [max(len(c.get("say", "")), 12) for c in scenes_spec]
    span = total + XF * (len(scenes_spec) - 1)
    out = []
    for c, wi in zip(scenes_spec, w):
        out.append(dict(c, dur=max(2.2, span * wi / sum(w))))
    return out

def music_path(name):
    """Musique de fond téléchargée par fetch_music.py ; à défaut, n'importe quelle autre piste présente."""
    if not name: return None
    d = os.path.join(ROOT, "media", "music"); slug_ = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    p = os.path.join(d, slug_ + ".mp3")
    if os.path.exists(p): return p
    alt = sorted(f for f in os.listdir(d) if f.endswith(".mp3")) if os.path.isdir(d) else []
    return os.path.join(d, alt[sum(map(ord, name)) % len(alt)]) if alt else None

MUSIC_VOL = 0.16   # sous la voix : présente mais jamais devant

def render_reel(scenes_spec, out, audio=None, pal=None, music=None):
    CTX[0] = "vidéo " + os.path.basename(out)
    if audio: scenes_spec = fit_scenes(scenes_spec, audio_len(audio) + 0.9)
    scenes = [Scene(c, i, pal) for i, c in enumerate(scenes_spec)]
    starts, t = [], 0.0
    for i, sc in enumerate(scenes):
        starts.append(t); t += sc.dur - (XF if i < len(scenes) - 1 else 0)
    total = t; n = int(total * FPS)
    if music:
        # voix devant, musique en boucle dessous, qui monte au début et s'éteint à la fin
        vin = ["-i", audio] if audio else ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
        fo = max(0.0, total - 1.4)
        aud = [*vin, "-stream_loop", "-1", "-i", music, "-filter_complex",
               f"[1:a]aresample=48000,apad[v];[2:a]aresample=48000,volume={MUSIC_VOL if audio else 0.5},afade=t=in:d=0.6,afade=t=out:st={fo:.2f}:d=1.4[m];"
               f"[v][m]amix=inputs=2:duration=first:normalize=0,atrim=0:{total:.2f},loudnorm=I=-14:TP=-1.5:LRA=11[a]", "-map", "0:v", "-map", "[a]"]
    else:
        aud = ["-i", audio, "-af", "apad"] if audio else ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{RW}x{RH}", "-r", str(FPS), "-i", "-",
           *aud, "-shortest",
           "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p", "-preset", "medium", "-crf", "21",
           "-maxrate", "4500k", "-bufsize", "9000k", "-g", "60", "-keyint_min", "60", "-sc_threshold", "0",
           "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-movflags", "+faststart", out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for k in range(n):
        tt = k / FPS
        act = [i for i, s0 in enumerate(starts) if s0 <= tt < s0 + scenes[i].dur]
        i = act[-1]; fr = scenes[i].frame(tt - starts[i])
        if len(act) > 1:  # la nouvelle scène pousse l'ancienne hors du cadre
            j = act[0]; a = ease_io((tt - starts[i]) / XF)
            old = scenes[j].frame(tt - starts[j]).convert("RGBA"); comp = Image.new("RGBA", (RW, RH))
            if i % 2:
                off = int(RW * a); comp.paste(old, (-off, 0)); comp.paste(fr, (RW - off, 0))
            else:
                off = int(RH * a); comp.paste(old, (0, -off)); comp.paste(fr, (0, RH - off))
            fr = comp
        d = ImageDraw.Draw(fr); d.rectangle([0, 0, int(RW * (k + 1) / n), 8], fill=scenes[i].P["mark"])  # barre de progression
        p.stdin.write(fr.convert("RGB").tobytes())
    p.stdin.close(); p.wait()
    if p.returncode: raise RuntimeError("ffmpeg failed")
    # miniature pour l'aperçu
    Scene(scenes_spec[0], 0, pal).frame(min(2.4, scenes_spec[0]["dur"] - 0.1)).convert("RGB").save(out.replace(".mp4", "-cover.jpg"), quality=88)
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
        refs += [r for x in p.get("slides", []) for r, _ in x.get("imgs", [])]
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
    for r in REELS:
        cap = r["caption"].replace("[CTA]", CTA_IG)
        if len(re.findall(r"#\w+", cap)) > 5: errs.append(r["date"] + " reel >5 hashtags")
        if len(cap) > 2200: errs.append(r["date"] + " reel légende trop longue")
        if not os.path.exists(os.path.join(ROOT, "media", "reels", r["date"] + ".mp4")): errs.append(r["date"] + " vidéo absente")
        for w in FORBIDDEN:
            if w in cap.lower(): errs.append(f"{r['date']} reel mot interdit « {w.strip()} »")
    taken = {r["date"] for r in REELS}
    for v in VIDEOS:
        if v["date"] in taken: errs.append(v["date"] + " deux vidéos le même jour")
        taken.add(v["date"])
        cap = v["caption"].replace("[CTA]", CTA_IG)
        if not re.search(r"brosses? à dents électriques?", cap.split("\n")[0].lower()): errs.append(v["id"] + " mot-clé 1re ligne")
        if len(re.findall(r"#\w+", cap)) > 5: errs.append(v["id"] + " >5 hashtags")
        screen = json.dumps([{k: x for k, x in sc.items() if k != "say"} for sc in v["scenes"]], ensure_ascii=False).lower()
        for w in FORBIDDEN:
            if w in cap.lower() or w in screen or w in vo_text(v).lower(): errs.append(f"{v['id']} mot interdit « {w.strip()} »")
    return errs, used

def render_videos():
    """Vidéos de test avec voix off : rendues seulement si la voix est là, et une seule fois."""
    import hashlib
    for v in VIDEOS:
        if ONLY and v["date"] not in ONLY: continue
        vo = os.path.join(ROOT, "media", "vo", v["id"] + ".mp3")
        mus = music_path(v.get("music"))
        if not os.path.exists(vo) and mus:
            # Pas de voix mais une musique : format texte + musique, programmé. Re-rendu tout seul si la voix arrive.
            rel = f"media/reels/{v['date']}.mp4"; out = os.path.join(ROOT, rel)
            sig = hashlib.sha1((json.dumps(v["scenes"], ensure_ascii=False) + str(v.get("pal")) + "musique:" + os.path.basename(mus) + SCENE_V).encode()).hexdigest()
            stamp = out.replace(".mp4", ".sig")
            if not (os.path.exists(out) and os.path.exists(stamp) and open(stamp).read() == sig):
                est = sum(len(sc.get("say", "")) for sc in v["scenes"]) / 15.5 + 0.9
                t0 = time.time(); dur = render_reel(fit_scenes(v["scenes"], est), out, pal=v.get("pal"), music=mus)
                open(stamp, "w").write(sig); print(f"{v['date']} vidéo {v['id']} (musique seule) {dur:.1f}s ({time.time() - t0:.0f}s)")
            ig = v["caption"].replace("[CTA]", CTA_IG); fb = v["caption"].replace("[CTA]", CTA_FB)
            post = {"type": "reel", "video_url": REEL_HOST + rel, "thumb_offset": 1200, "caption": ig, "fb_message": fb}
            json.dump({"post": post}, open(os.path.join(ROOT, "planning", v["date"] + "-reel.json"), "w"), ensure_ascii=False, indent=2)
            continue
        if not os.path.exists(vo):
            # Pas encore de voix : aperçu muet (durées estimées sur le texte), jamais programmé.
            prev = os.path.join(ROOT, "media", "previews", v["id"] + ".mp4"); os.makedirs(os.path.dirname(prev), exist_ok=True)
            sig = hashlib.sha1((json.dumps(v["scenes"], ensure_ascii=False) + str(v.get("pal")) + os.path.basename(music_path(v.get("music")) or "") + SCENE_V).encode()).hexdigest()
            stamp = prev.replace(".mp4", ".sig")
            if not (os.path.exists(prev) and os.path.exists(stamp) and open(stamp).read() == sig):
                est = sum(len(sc.get("say", "")) for sc in v["scenes"]) / 15.5 + 0.9
                render_reel(fit_scenes(v["scenes"], est), prev, pal=v.get("pal"), music=music_path(v.get("music"))); open(stamp, "w").write(sig)
            print(v["date"], v["id"], "voix off absente : aperçu muet, vidéo non programmée"); continue
        rel = f"media/reels/{v['date']}.mp4"; out = os.path.join(ROOT, rel)
        sig = hashlib.sha1((json.dumps(v["scenes"], ensure_ascii=False) + str(v.get("pal")) + str(os.path.getsize(vo)) + os.path.basename(music_path(v.get("music")) or "") + SCENE_V).encode()).hexdigest()
        stamp = out.replace(".mp4", ".sig")
        if not (os.path.exists(out) and os.path.exists(stamp) and open(stamp).read() == sig):
            t0 = time.time(); dur = render_reel(v["scenes"], out, audio=vo, pal=v.get("pal"), music=music_path(v.get("music")))
            open(stamp, "w").write(sig); print(f"{v['date']} vidéo {v['id']} {dur:.1f}s ({time.time() - t0:.0f}s)")
        ig = v["caption"].replace("[CTA]", CTA_IG); fb = v["caption"].replace("[CTA]", CTA_FB)
        post = {"type": "reel", "video_url": REEL_HOST + rel, "thumb_offset": 1200, "caption": ig, "fb_message": fb}
        json.dump({"post": post}, open(os.path.join(ROOT, "planning", v["date"] + "-reel.json"), "w"), ensure_ascii=False, indent=2)

def main():
    if "--fetch-only" in sys.argv:   # télécharge les photos sources (utile hors GitHub Actions)
        refs = sorted({x["img"] for p in ALL for x in p.get("slides", []) if x.get("img")} | {r_ for p in ALL for x in p.get("slides", []) for r_, _ in x.get("imgs", [])})
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
          CTX[0] = "post " + date
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
                  for k_ in ("da", "tone"):
                      if p.get(k_) and not sl.get(k_): sl[k_] = p[k_]
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
    for r in REELS:
        if ONLY and r["date"] not in ONLY: continue
        ig = r["caption"].replace("[CTA]", CTA_IG); fb = r["caption"].replace("[CTA]", CTA_FB)
        rel = f"media/reels/{r['date']}.mp4"
        post = {"type": "reel", "video_url": REEL_HOST + rel, "thumb_offset": r.get("cover", 0), "caption": ig, "fb_message": fb}
        json.dump({"post": post}, open(os.path.join(ROOT, "planning", r["date"] + "-reel.json"), "w"), ensure_ascii=False, indent=2)
        print(f"{r['date']} reel")
        cov = os.path.join(ROOT, f"media/reels/{r['date']}-cover.jpg")
        if not os.path.exists(cov):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(r.get("cover", 0) / 1000), "-i", os.path.join(ROOT, rel),
                            "-frames:v", "1", "-vf", "scale=540:-1", cov], check=False)
        gallery.append((r["date"] + " · vidéo", "reel", [f"media/reels/{r['date']}-cover.jpg"], rel, ig))
    render_videos()
    rep = Counter((c, k) for c, k, _ in AUDIT)
    with open(os.path.join(ROOT, "media", "audit-contraste.txt"), "w") as fh:
        fh.write("Corrections automatiques de lisibilité (flat = couleur du texte corrigée, busy = halo ajouté)\n")
        for (c, k), n in sorted(rep.items()): fh.write(f"{c}\t{k}\t{n}\n")
    print("audit contraste :", len(rep), "éléments corrigés")
    for v in VIDEOS:
        rel = f"media/reels/{v['date']}.mp4"
        if os.path.exists(os.path.join(ROOT, rel)):
            gallery.append((v["date"] + " · vidéo " + v["axis"], "reel", [rel.replace(".mp4", "-cover.jpg")], rel, v["caption"]))
    gallery.sort(key=lambda g: g[0])
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
