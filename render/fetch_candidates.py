"""Télécharge une liste de photos candidates dans render/.cache (taille réduite), pour les contrôler avant usage."""
import io, os, re, sys, time, urllib.request
from PIL import Image, ImageOps
HERE = os.path.dirname(os.path.abspath(__file__)); CACHE = os.path.join(HERE, ".cache"); os.makedirs(CACHE, exist_ok=True)
SHOP = "https://cdn.shopify.com/s/files/1/0906/8147/5446/files/"
for ref in open(os.path.join(HERE, "candidates.txt")).read().split():
    fn = os.path.join(CACHE, re.sub(r"[^a-zA-Z0-9.-]", "_", ref) + ".bin")
    if os.path.exists(fn): continue
    k, v = ref.split(":", 1)
    url = SHOP + v + "?width=2000" if k == "s" else f"https://images.unsplash.com/photo-{v}?w=2000&q=85&fm=jpg"
    for i in range(3):
        try:
            data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "pulse-care-media/1.0"}), timeout=60).read()
            im = ImageOps.exif_transpose(Image.open(io.BytesIO(data)))
            if im.mode in ("RGBA", "LA", "P"):
                im = im.convert("RGBA"); bg = Image.new("RGB", im.size, (255, 255, 255)); bg.paste(im, mask=im.split()[3]); im = bg
            im = im.convert("RGB"); im.thumbnail((1600, 1600)); im.save(fn, "JPEG", quality=88); print("ok", ref); break
        except Exception as e:
            print("retry", ref, e); time.sleep(2)
    else: print("ECHEC", ref)
