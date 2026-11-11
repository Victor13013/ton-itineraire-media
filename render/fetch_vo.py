# -*- coding: utf-8 -*-
"""Télécharge les voix off ElevenLabs listées dans render/vo.json vers media/vo/<id>.mp3.
Les liens ElevenLabs expirent au bout de quelques heures : seuls les fichiers absents sont téléchargés."""
import json, os, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
src = os.path.join(ROOT, "render", "vo.json")
os.makedirs(os.path.join(ROOT, "media", "vo"), exist_ok=True)
for vid, url in (json.load(open(src)) if os.path.exists(src) else {}).items():
    out = os.path.join(ROOT, "media", "vo", vid + ".mp3")
    if os.path.exists(out): continue
    try:
        data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "pulse-care-media/1.0"}), timeout=60).read()
        open(out, "wb").write(data); print("voix off", vid, len(data), "octets")
    except Exception as e:
        print("voix off", vid, "échec :", e)
