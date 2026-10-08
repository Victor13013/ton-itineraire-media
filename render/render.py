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
ONLY = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
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

# ───────────────────────────── visuels 1080x1350
W, H = 1080, 1350

def t_hero(c):
    base = cover(load(c["img"]), W, H, 0.5, c.get("fy", 0.45)).convert("RGBA")
    base.alpha_composite(gradient(W, H, DEEP, 0.30, 0.92, 0, 238))
    base.alpha_composite(gradient(W, 260, DEEP, 0, 1, 120, 0), (0, 0))
    d = ImageDraw.Draw(base)
    wordmark(d, 70, 64, CREAM)
    tf = fit(c["title"], BOLD, W - 140, 92, 56, 4)
    tl = wrap(c["title"], tf, W - 140)
    sl = wrap(c["sub"], REG(36), W - 140) if c.get("sub") else []
    bottom = H - 150
    y = bottom - text_h(sl, REG(36), 1.35) - (24 if sl else 0) - text_h(tl, tf)
    if c.get("kicker"):
        pill(d, 70, y - 84, c["kicker"].upper(), MED(26), BAMBOO, DEEP)
    y = draw_lines(d, 70, y, tl, tf, CREAM)
    if sl: draw_lines(d, 70, y + 24, sl, REG(36), (226, 232, 226), 1.35)
    if c.get("price"): price_badge(base, c["price"])
    footer(d, W, H, CREAM, c.get("page"), c.get("swipe"))
    return base.convert("RGB")

def price_badge(base, price):
    d = ImageDraw.Draw(base); r = 118; cx, cy = W - 70 - r, 70 + r
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BAMBOO)
    f = BOLD(54) if len(price) < 7 else BOLD(46)
    tw = d.textlength(nb(price), font=f)
    d.text((cx - tw / 2, cy - 38), nb(price), font=f, fill=DEEP)

def t_statement(c):
    ph = cover(load(c["img"]), W, H).filter(ImageFilter.GaussianBlur(3)).convert("RGBA")
    ov = Image.new("RGBA", (W, H), GREEN + (205,)); ph.alpha_composite(ov)
    d = ImageDraw.Draw(ph)
    wordmark(d, 70, 64, CREAM)
    tf = fit(c["title"], BOLD, W - 160, 100, 58, 5)
    tl = wrap(c["title"], tf, W - 160)
    sl = wrap(c["sub"], REG(40), W - 160) if c.get("sub") else []
    total = text_h(tl, tf) + (30 + text_h(sl, REG(40), 1.4) if sl else 0) + 90
    y = (H - total) / 2 + 40
    if c.get("kicker"):
        f = MED(28); k = c["kicker"].upper(); tw = d.textlength(k, font=f)
        d.text(((W - tw) / 2, y), k, font=f, fill=BAMBOO)
        d.line([(W / 2 - 40, y + 52), (W / 2 + 40, y + 52)], fill=BAMBOO, width=3)
    y += 90
    y = draw_lines(d, 0, y, tl, tf, CREAM, anchor_center=True, W=W)
    if sl: draw_lines(d, 0, y + 30, sl, REG(40), (226, 232, 226), 1.4, anchor_center=True, W=W)
    footer(d, W, H, CREAM, c.get("page"), c.get("swipe"))
    return ph.convert("RGB")

def t_product(c):
    base = Image.new("RGBA", (W, H), CREAM + (255,))
    d = ImageDraw.Draw(base)
    d.ellipse([W - 420, -260, W + 260, 420], fill=MINT)
    wordmark(d, 70, 64, GREEN)
    ph = cover(load(c["img"]), 900, 760)
    shadow_paste(base, ph, 90, 150)
    d = ImageDraw.Draw(base)
    y = 960
    if c.get("kicker"):
        d.text((90, y), c["kicker"].upper(), font=MED(28), fill=BAMBOO); y += 52
    tf = fit(c["title"], BOLD, W - 180 - (240 if c.get("price") else 0), 66, 44, 2)
    tl = wrap(c["title"], tf, W - 180 - (240 if c.get("price") else 0))
    y = draw_lines(d, 90, y, tl, tf, GREEN, 1.12)
    if c.get("sub"):
        draw_lines(d, 90, y + 10, wrap(c["sub"], REG(32), W - 180), REG(32), GREEN, 1.35)
    if c.get("price"):
        f = BOLD(44); p = nb(c["price"]); tw = d.textlength(p, font=f)
        d.rounded_rectangle([W - 90 - tw - 56, 980, W - 90, 1062], radius=41, fill=GREEN)
        d.text((W - 90 - tw - 28, 990), p, font=f, fill=CREAM)
    footer(d, W, H, GREEN, c.get("page"), c.get("swipe"))
    return base.convert("RGB")

def t_list(c):
    bg = MINT if c.get("alt") else CREAM
    base = Image.new("RGBA", (W, H), bg + (255,))
    ph = cover(load(c["img"]), W, 520).convert("RGBA")
    ph.alpha_composite(gradient(W, 520, DEEP, 0, 1, 90, 0))
    base.paste(ph, (0, 0))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle([0, 470, W, 560], radius=50, fill=bg)
    wordmark(d, 70, 64, CREAM)
    tf = fit(c["title"], BOLD, W - 140, 60, 44, 2)
    y = draw_lines(d, 70, 530, wrap(c["title"], tf, W - 140), tf, GREEN, 1.12) + 30
    n = len(c["items"]); fs = 40 if n <= 3 else 36
    for i, (a, b) in enumerate(c["items"]):
        cy = y + 6
        d.ellipse([70, cy, 70 + 56, cy + 56], fill=BAMBOO if not c.get("alt") else GREEN)
        mark = str(i + 1) if c.get("numbered") else "→"
        f = BOLD(28) if c.get("numbered") else ARR(28)
        tw = d.textlength(mark, font=f)
        d.text((98 - tw / 2, cy + 8), mark, font=f, fill=DEEP if not c.get("alt") else CREAM)
        y = draw_lines(d, 150, y, wrap(a, MED(fs), W - 220), MED(fs), GREEN, 1.18)
        if b: y = draw_lines(d, 150, y + 2, wrap(b, REG(fs - 8), W - 220), REG(fs - 8), (70, 92, 82), 1.3)
        y += 28 if n <= 3 else 18
    footer(d, W, H, GREEN, c.get("page"), c.get("swipe"))
    return base.convert("RGB")

def t_stats(c):
    base = cover(load(c["img"]), W, H).convert("RGBA")
    base.alpha_composite(Image.new("RGBA", (W, H), DEEP + (150,)))
    base.alpha_composite(gradient(W, H, DEEP, 0.2, 1, 40, 220))
    d = ImageDraw.Draw(base)
    wordmark(d, 70, 64, CREAM)
    d.text((70, 170), nb(c["title"]), font=BOLD(70), fill=CREAM)
    tw_, th_, gap = (W - 140 - 30) // 2, 380, 30
    y0 = 340
    glass = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(glass)
    for i in range(4):
        x = 70 + (i % 2) * (tw_ + gap); y = y0 + (i // 2) * (th_ + gap)
        g.rounded_rectangle([x, y, x + tw_, y + th_], radius=34, fill=(255, 255, 255, 34), outline=(255, 255, 255, 70), width=2)
    base.alpha_composite(glass); d = ImageDraw.Draw(base)
    for i, (big, small) in enumerate(c["items"]):
        x = 70 + (i % 2) * (tw_ + gap); y = y0 + (i // 2) * (th_ + gap)
        fb = BOLD(96)
        while d.textlength(nb(big), font=fb) > tw_ - 70: fb = BOLD(fb.size - 6)
        d.text((x + 36, y + 70), nb(big), font=fb, fill=CREAM)
        d.line([(x + 38, y + 210), (x + 98, y + 210)], fill=BAMBOO, width=4)
        draw_lines(d, x + 36, y + 236, wrap(small, REG(32), tw_ - 72), REG(32), (226, 232, 226), 1.3)
    footer(d, W, H, CREAM, c.get("page"), c.get("swipe"))
    return base.convert("RGB")

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
        if ONLY and p["date"] != ONLY: continue
        date = p["date"]; ig = p["caption"].replace("[CTA]", CTA_IG); fb = p["caption"].replace("[CTA]", CTA_FB)
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
