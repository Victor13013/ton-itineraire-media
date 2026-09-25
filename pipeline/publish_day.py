"""Prépare la publication d'un jour : rend le post + la story, écrit planning/DATE.json.
Usage : python3 pipeline/publish_day.py item.json 2026-09-28 <github_user>
item.json = {"post": spec, "caption": "...", "story": spec_story, "topic": "..."}
"""
import json, sys, os, shutil, pathlib, datetime
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from render import render

REPO = pathlib.Path(__file__).resolve().parent.parent
item = json.load(open(sys.argv[1]))
date = sys.argv[2]
user = sys.argv[3]
base = f"https://raw.githubusercontent.com/{user}/ton-itineraire-media/main/media/{date}"
out = REPO / "media" / date
if out.exists():
    shutil.rmtree(out)

post_files, p1 = render(item["post"], str(out))
story_files, p2 = render(item["story"], str(out))
problems = p1 + p2

# règles automatiques
cap = item["caption"]
tags = [w for w in cap.split() if w.startswith("#")]
errs = []
if len(tags) > 5: errs.append(f"{len(tags)} hashtags (max 5)")
if len(cap) > 2200: errs.append("légende > 2200 caractères")
if len(post_files) > 10: errs.append("carrousel > 10 visuels")
BANNED = ["paradisiaque", "magique", "incroyable", "inoubliable", "époustouflant", "pépite", "n'hésitez pas",
          "voyage de rêve", "havre de paix", "à couper le souffle", "must-see", "incontournable", " tu ", " ton voyage"]
low = " " + cap.lower() + " "
for b in BANNED:
    if b in low: errs.append(f"mot interdit : {b.strip()}")
if problems: errs.append(f"débordement de texte : {problems}")
if errs:
    print("ERREURS :", errs); sys.exit(1)

urls = [f"{base}/{os.path.basename(f)}" for f in post_files]
plan = {
    "date": date,
    "topic": item.get("topic"),
    "post": {
        "type": "carousel" if len(urls) > 1 else "photo",
        "caption": cap,
        "image_url": urls[0],
        "media": [{"media_type": "IMAGE", "url": u} for u in urls],
    },
    "story": {"image_url": f"{base}/{os.path.basename(story_files[0])}"},
}
(REPO / "planning").mkdir(exist_ok=True)
json.dump(plan, open(REPO / "planning" / f"{date}.json", "w"), ensure_ascii=False, indent=1)

# historique (sujets + photos utilisées) pour varier
hp = REPO / "history.json"
hist = json.load(open(hp)) if hp.exists() else []
photos = sorted({s["photo"] for s in item["post"]["slides"] + item["story"]["slides"] if s.get("photo")})
hist.append({"date": date, "topic": item.get("topic"), "format": plan["post"]["type"], "slides": len(urls), "photos": photos})
json.dump(hist, open(hp, "w"), ensure_ascii=False, indent=1)
print("OK", date, plan["post"]["type"], len(urls), "visuels + 1 story")
