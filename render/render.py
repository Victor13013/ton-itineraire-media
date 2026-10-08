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

FAKE = "--fake" in sys.argv
ONLY = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
RAW = "https://raw.githubusercontent.com/Victor13013/pulse-care-media/main/"
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

# ───────────────────────────── v3 : affiches graphiques, sans cadre
GOLD = (226, 199, 150); BRONZE = (168, 120, 58); OLIVE = (122, 140, 98)
THEMES = [  # fond, texte, accent italique, forme déco, texte secondaire
    dict(bg=DEEP,  fg=CREAM, acc=GOLD,   deco=BAMBOO, sub=(206, 216, 206), dark=True),
    dict(bg=SAGE,  fg=INK,   acc=BRONZE, deco=CREAM,  sub=(64, 84, 72),    dark=False),
    dict(bg=SAND,  fg=INK,   acc=BRONZE, deco=SAGE,   sub=(92, 96, 82),    dark=False),
    dict(bg=GREEN, fg=CREAM, acc=GOLD,   deco=(52, 86, 70), sub=(206, 216, 206), dark=True),
]
def theme(c, default=0):
    return THEMES[c.get("theme_i", c.get("_n", default)) % len(THEMES)]

def canvas(t):
    return Image.new("RGBA", (W, H), t["bg"] + (255,))

def shape_photo(base, src, box, shape="arch", fx=0.5, fy=0.5):
    x0, y0, x1, y1 = box; w, h = x1 - x0, y1 - y0
    im, pk = prep(src)
    if pk:
        prod = trim(im); prod = prod.resize(fit_size(prod, int(w * 0.78), int(h * 0.74)), Image.LANCZOS)
        pad = Image.new("RGB", (w, h), WHITE); pad.paste(prod, ((w - prod.width) // 2, (h - prod.height) // 2 + int(h * 0.05)))
        ph = multiply_on(Image.new("RGB", (w, h), CREAM), pad)
    else:
        if (border_px(im).min(axis=1) > 238).mean() > 0.5:
            ww, hh = im.size; k = 0.6
            im = im.crop((int(ww * (1 - k) / 2), int(hh * (1 - k) / 2), int(ww * (1 + k) / 2), int(hh * (1 + k) / 2)))
        ph = cover(im, w, h, fx, fy)
    m = Image.new("L", (w, h), 0); md = ImageDraw.Draw(m)
    if shape == "arch":
        md.rectangle([0, w // 2, w, h], fill=255); md.ellipse([0, 0, w, w], fill=255)
    elif shape == "circle":
        md.ellipse([0, 0, w, h], fill=255)
    elif shape == "pill":
        md.rounded_rectangle([0, 0, w, h], radius=min(w, h) // 2, fill=255)
    else:
        md.rounded_rectangle([0, 0, w, h], radius=48, fill=255)
    base.paste(ph, (x0, y0), m)
    return pk

def disc(base, cx, cy, r, color, alpha=255):
    ov = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (alpha,))
    base.alpha_composite(ov)

def sticker(base, text, cx, cy, r, bg, fg, angle=-12):
    """Pastille ronde inclinée (prix, mot-clé)."""
    s_ = Image.new("RGBA", (2 * r + 4, 2 * r + 4), (0, 0, 0, 0)); d = ImageDraw.Draw(s_)
    d.ellipse([2, 2, 2 * r + 2, 2 * r + 2], fill=bg)
    lines = text.split("\n"); f = SERIF(int(r * 0.42) if len(lines) == 1 else int(r * 0.30), True, 600)
    yy = r + 2 - f.size * 0.62 * len(lines)
    for ln in lines:
        tw = d.textlength(nb(ln), font=f); d.text((r + 2 - tw / 2, yy), nb(ln), font=f, fill=fg); yy += f.size * 1.1
    s_ = s_.rotate(angle, resample=Image.BICUBIC, expand=True)
    base.alpha_composite(s_, (int(cx - s_.width / 2), int(cy - s_.height / 2)))

def foot3(d, t, page=None, swipe=False):
    f = MED(22)
    if page:
        tw = d.textlength(page, font=f); d.text((W - M - tw, H - 92), page, font=f, fill=t["sub"])
    if swipe:
        tracked(d, M, H - 92, "SWIPE", f, t["acc"], 0.3)
        d.text((M + 104, H - 96), "→", font=ARR(28), fill=t["acc"])

# ── 1. Affiche : arche photo + gros titre
def t_hero(c):
    t = theme(c); base = canvas(t); src = load(c["img"])
    flip = c.get("_n", 0) % 2 == 1
    size, tl = rich_fit(c["title"], W - 2 * M, 108, 62, 3)
    sl = wrap(c["sub"], REG(31), W - 2 * M - 60) if c.get("sub") else []
    block = (62 if c.get("kicker") else 0) + size * 1.04 * len(tl) + (18 + text_h(sl, REG(31), 1.42) if sl else 0)
    top = H - 150 - block
    disc(base, (W - 250 if flip else 250), 250, 190, t["deco"], 255 if not t["dark"] else 120)
    ax0 = 70 if flip else 330; box = (ax0, 120, ax0 + 680, int(top - 40))
    shape_photo(base, src, box, "arch", 0.5, c.get("fy", 0.4))
    d = ImageDraw.Draw(base)
    brand(d, M, 70, t["fg"])
    y = top
    if c.get("kicker"): kicker(d, M, y, c["kicker"], t["acc"]); y += 62
    y = rich_draw(d, M, y, tl, size, t["fg"], t["acc"], 1.04)
    if sl: draw_lines(d, M, y + 18, sl, REG(31), t["sub"], 1.42)
    if c.get("price"):
        sticker(base, c["price"], (ax0 + 680 - 40) if not flip else (ax0 + 40), int(top - 140), 112, BAMBOO, DEEP)
    foot3(ImageDraw.Draw(base), t, c.get("page"), c.get("swipe"))
    return grain(base, 3).convert("RGB")

# ── 2. Phrase choc : titre géant + photo ronde
def t_statement(c):
    t = theme(c, 0); base = canvas(t)
    disc(base, W - 120, H - 220, 260, t["deco"], 110 if t["dark"] else 255)
    shape_photo(base, load(c["img"]), (W // 2 - 170, 150, W // 2 + 170, 490), "circle")
    d = ImageDraw.Draw(base)
    brand(d, 0, 70, t["fg"], W)
    y = 560
    if c.get("kicker"): kicker(d, 0, y, c["kicker"], t["acc"], center_w=W); y += 70
    size, tl = rich_fit(c["title"], W - 2 * M, 104, 58, 4)
    y = rich_draw(d, 0, y, tl, size, t["fg"], t["acc"], 1.06, center_w=W)
    if c.get("sub"):
        draw_lines(d, 0, y + 28, wrap(c["sub"], REG(32), W - 2 * M - 60), REG(32), t["sub"], 1.45, anchor_center=True, W=W)
    foot3(d, t, c.get("page"), c.get("swipe"))
    return grain(base, 3).convert("RGB")

# ── 3. Produit : grande arche crème sur fond couleur
def t_product(c):
    t = theme(c, 1); base = canvas(t)
    disc(base, 200, 330, 170, t["deco"], 255 if not t["dark"] else 120)
    disc(base, W - 150, 860, 90, BAMBOO, 255)
    shape_photo(base, load(c["img"]), (190, 130, 890, 900), "arch")
    d = ImageDraw.Draw(base)
    brand(d, 0, 70, t["fg"], W)
    y = 950
    if c.get("kicker"): kicker(d, 0, y, c["kicker"], t["acc"], center_w=W); y += 58
    size, tl = rich_fit(c["title"], W - 2 * M, 76, 50, 2)
    y = rich_draw(d, 0, y, tl, size, t["fg"], t["acc"], 1.06, center_w=W)
    if c.get("sub"):
        draw_lines(d, 0, y + 14, wrap(c["sub"], REG(30), W - 2 * M - 80), REG(30), t["sub"], 1.42, anchor_center=True, W=W)
    if c.get("price"): sticker(base, c["price"], 860, 230, 118, DEEP if not t["dark"] else BAMBOO, CREAM if not t["dark"] else DEEP)
    foot3(ImageDraw.Draw(base), t, c.get("page"), c.get("swipe"))
    return grain(base, 3).convert("RGB")

# ── 4. Liste : photo ronde en débord + grands numéros
def t_list(c):
    t = theme(c, 2); base = canvas(t)
    shape_photo(base, load(c["img"]), (W - 470, -120, W + 110, 460), "circle")
    disc(base, W - 470, 420, 70, BAMBOO, 255)
    d = ImageDraw.Draw(base)
    brand(d, M, 70, t["fg"])
    size, tl = rich_fit(c["title"], 520, 74, 50, 3)
    y = rich_draw(d, M, 190, tl, size, t["fg"], t["acc"], 1.06)
    y = max(y + 50, 560)
    n = len(c["items"]); fa = 40 if n <= 3 else 35; fb = 29 if n <= 3 else 27
    for i, (a_, b_) in enumerate(c["items"]):
        num = f"{c.get('start', 1) + i:02d}" if c.get("numbered") else f"{i + 1:02d}"
        d.text((M, y - 18), num, font=SERIF(78 if n <= 3 else 64, True, 500), fill=t["acc"])
        yy = draw_lines(d, M + 150, y, wrap(a_, MED(fa), W - 2 * M - 150), MED(fa), t["fg"], 1.2)
        if b_: yy = draw_lines(d, M + 150, yy + 2, wrap(b_, REG(fb), W - 2 * M - 150), REG(fb), t["sub"], 1.38)
        y = yy + (52 if n <= 3 else 30)
    foot3(d, t, c.get("page"), c.get("swipe"))
    return grain(base, 3).convert("RGB")

# ── 5. Chiffres : énormes chiffres + photo pilule
def t_stats(c):
    t = THEMES[0] if c.get("_n", 0) % 2 == 0 else THEMES[3]; base = canvas(t)
    shape_photo(base, load(c["img"]), (W - 330, 110, W - 70, 620), "pill")
    d = ImageDraw.Draw(base)
    brand(d, M, 70, t["fg"])
    size, tl = rich_fit(c["title"], 560, 92, 60, 2)
    rich_draw(d, M, 170, tl, size, t["fg"], t["acc"])
    cw = (W - 2 * M) // 2
    for i, (big, small) in enumerate(c["items"]):
        x = M + (i % 2) * cw; y = [680, 680, 960, 960][i]
        f = SERIF(124, False, 600)
        while d.textlength(nb(big), font=f) > cw - 40: f = SERIF(f.size - 6, False, 600)
        d.text((x, y), nb(big), font=f, fill=GOLD if i in (0, 3) else t["fg"])
        draw_lines(d, x, y + 152, wrap(small, REG(29), cw - 60), REG(29), t["sub"], 1.4)
    foot3(d, t, c.get("page"), c.get("swipe"))
    return grain(base, 3).convert("RGB")

TPL = {"hero": t_hero, "statement": t_statement, "product": t_product, "list": t_list, "stats": t_stats}

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
             "40 000", "massage", "brosse en bambou", "manche en bambou", "dupont", "tynex", " vous ", " vos ", "votre"]

def check():
    errs, used = [], Counter()
    for p in POSTS:
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
    errs, used = check()
    if errs:
        print("\n".join(errs)); sys.exit(1)
    print(f"Contrôles OK · {len(POSTS)} posts · {len(used)} visuels sources uniques")
    for d_ in ("media/posts", "media/reels", "planning"): os.makedirs(os.path.join(ROOT, d_), exist_ok=True)
    gallery = []
    for p in POSTS:
        if ONLY and p["date"] not in ONLY: continue
        date = p["date"]; cap = p["caption"]
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
                sl = dict(sl, _n=POSTS.index(p) + i - 1)
                TPL[sl["tpl"]](sl).save(os.path.join(ROOT, rel), "JPEG", quality=90, optimize=True, progressive=False)
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
