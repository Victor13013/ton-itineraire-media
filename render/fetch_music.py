# -*- coding: utf-8 -*-
"""Musiques de fond libres de droit (licence Mixkit : usage commercial gratuit, sans attribution).
Lit les pages de catalogue Mixkit, repère chaque morceau (titre + mp3) et télécharge ceux que les vidéos demandent
dans media/music/<slug>.mp3. Tout ce qui a été trouvé est listé dans media/music/index.json."""
import json, os, re, sys, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tests_axes import VIDEOS

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "media", "music"); os.makedirs(OUT, exist_ok=True)
PAGES = ["https://mixkit.co/free-stock-music/tag/lifestyle/", "https://mixkit.co/free-stock-music/mood/lively/",
         "https://mixkit.co/free-stock-music/mood/uplifting/", "https://mixkit.co/free-stock-music/mood/positive/",
         "https://mixkit.co/free-stock-music/pop/"]
UA = {"User-Agent": "Mozilla/5.0 (pulse-care-media)"}

def slug(t): return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")

def get(url, timeout=40):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()

idx_path = os.path.join(OUT, "index.json")
found = json.load(open(idx_path)) if os.path.exists(idx_path) else {}
wanted = {slug(v["music"]) for v in VIDEOS if v.get("music")}
if not all(os.path.exists(os.path.join(OUT, w + ".mp3")) for w in wanted):
    for page in PAGES:
        try: html = get(page).decode("utf-8", "ignore")
        except Exception as e: print("musique : page illisible", page, e); continue
        mp3s = [(m.start(), m.group(0)) for m in re.finditer(r"https://assets\.mixkit\.co/[^\"' >]+?\.mp3", html)]
        titles = [(m.start(), re.sub(r"\s+", " ", m.group(1)).strip()) for m in re.finditer(r"__title[^>]*>\s*(?:<a[^>]*>)?\s*([^<]{2,60}?)\s*<", html)]
        for pos, url in mp3s:
            before = [t for p_, t in titles if p_ < pos]
            if before: found.setdefault(slug(before[-1]), url)
        print("musique :", page, len(mp3s), "mp3,", len(titles), "titres")
    json.dump(found, open(idx_path, "w"), indent=1, sort_keys=True)
for w in sorted(wanted):
    out = os.path.join(OUT, w + ".mp3")
    if os.path.exists(out): continue
    if w not in found: print("musique introuvable :", w); continue
    try: data = get(found[w], 60); open(out, "wb").write(data); print("musique", w, len(data), "octets")
    except Exception as e: print("musique", w, "échec :", e)
