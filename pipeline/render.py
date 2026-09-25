"""Ton Itinéraire — générateur de carrousels Instagram 1080x1350.
Usage : python3 render.py post.json outdir
post.json = {"slug":..., "slides":[{"type":..., ...}, ...]}
Types post (1080x1350) : cover, photo, fact, myth, cta. Un post simple = 1 seule slide (cover ou fact).
Story (1080x1920) : spec {"slug":..., "format":"story", "slides":[{"type":"story", ...}]}
"""
import json, sys, os, base64, html, pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).parent
PHOTOS = pathlib.Path(os.environ.get("TI_PHOTOS", ROOT.parent / "photos"))

def b64(path, mime):
    return f"data:{mime};base64," + base64.b64encode(open(path, "rb").read()).decode()

FONTS = f"""
@font-face{{font-family:'Bricolage';src:url({b64(ROOT/'fonts/bricolage.woff2','font/woff2')}) format('woff2');font-weight:200 800;}}
@font-face{{font-family:'Jakarta';src:url({b64(ROOT/'fonts/plus-jakarta-sans-latin-500-normal.woff2','font/woff2')}) format('woff2');font-weight:500;}}
@font-face{{font-family:'Jakarta';src:url({b64(ROOT/'fonts/plus-jakarta-sans-latin-700-normal.woff2','font/woff2')}) format('woff2');font-weight:700;}}
"""

LOGO_SVG = """<svg viewBox="0 0 58 58" width="{s}" height="{s}" fill="none" style="color:{c}">
<circle cx="8" cy="46" r="2.2" fill="none" stroke="currentColor" stroke-width="2"/>
<circle cx="17" cy="38" r="2.5" fill="currentColor"/><circle cx="26" cy="29" r="3" fill="currentColor"/>
<circle cx="36" cy="20" r="3.5" fill="currentColor"/>
<circle cx="47" cy="12" r="4" fill="none" stroke="currentColor" stroke-width="2.4" opacity="0.35"/>
<circle cx="47" cy="12" r="6.2" fill="currentColor"/></svg>"""

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#FDF6E9;--deep:#F5E7C9;--ink:#1F3A3D;--soft:#4A6467;--accent:#FF7A5C;--gold:#FFB238}
body{width:1080px;height:1350px;overflow:hidden;font-family:'Jakarta',sans-serif;color:var(--ink);background:var(--bg)}
.s{position:relative;width:1080px;height:1350px;overflow:hidden}
.top{position:absolute;top:56px;left:64px;right:64px;display:flex;justify-content:space-between;align-items:center;z-index:5}
.logo{display:flex;align-items:center;gap:14px;font-family:'Bricolage';font-weight:800;font-size:34px;letter-spacing:-.5px}
.logo .acc{color:var(--accent)}
.num{font-family:'Bricolage';font-weight:700;font-size:26px;padding:10px 20px;border-radius:40px}
.dots{position:absolute;bottom:52px;left:0;right:0;display:flex;justify-content:center;gap:12px;z-index:5}
.dots i{width:12px;height:12px;border-radius:50%;background:currentColor;opacity:.3}
.dots i.on{opacity:1;width:36px;border-radius:8px}
.pill{display:inline-block;font-family:'Bricolage';font-weight:800;font-size:28px;letter-spacing:1.5px;text-transform:uppercase;padding:14px 28px;border-radius:40px;background:var(--accent);color:#12141C}
h1{font-family:'Bricolage';font-weight:800;line-height:1.02;letter-spacing:-2px}
h2{font-family:'Bricolage';font-weight:800;line-height:1.06;letter-spacing:-1px}
p{font-weight:500;line-height:1.45}
/* cover */
.cover img.bg,.photo img.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.cover .shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(18,20,28,.45) 0%,rgba(18,20,28,0) 28%,rgba(18,20,28,0) 42%,rgba(18,20,28,.88) 100%)}
.cover .txt{position:absolute;left:64px;right:64px;bottom:140px;color:#FAFAF8}
.cover h1{font-size:104px;margin:28px 0 24px}
.cover p{font-size:36px;opacity:.92}
/* photo slide */
.photo .imgwrap{position:absolute;left:0;right:0;top:0;height:720px}
.photo .imgwrap img{width:100%;height:100%;object-fit:cover}
.photo .imgwrap:after{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(18,20,28,.6) 0%,rgba(18,20,28,0) 32%)}
.photo .panel{position:absolute;left:0;right:0;top:660px;bottom:0;background:var(--bg);border-radius:48px 48px 0 0;padding:64px 64px 0}
.photo .kicker{font-family:'Bricolage';font-weight:800;color:var(--accent);font-size:36px;letter-spacing:1px;text-transform:uppercase}
.photo h2{font-size:80px;margin:18px 0 30px}
.photo p{font-size:40px;color:var(--soft)}
/* fact */
.fact{background:var(--bg)}
.fact .band{position:absolute;left:64px;right:64px;top:160px;height:470px;border-radius:36px;overflow:hidden}
.fact .band img{width:100%;height:100%;object-fit:cover}
.fact .flow{position:absolute;left:64px;right:64px;top:670px}
.fact .big{font-family:'Bricolage';font-weight:800;font-size:150px;color:var(--accent);line-height:1}
.fact h2{font-size:64px;margin:18px 0 26px}
.fact p{font-size:38px;color:var(--soft)}
/* myth */
.myth{background:var(--bg)}
.myth .band{position:absolute;left:0;right:0;top:0;height:470px}
.myth .band img{width:100%;height:100%;object-fit:cover}
.myth .band:after{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(18,20,28,.6),rgba(18,20,28,.1) 45%)}
.myth .box{position:absolute;left:64px;right:64px}
.myth .lab{font-family:'Bricolage';font-weight:800;font-size:28px;letter-spacing:2px;text-transform:uppercase}
.myth .flow{position:absolute;left:64px;right:64px;top:530px}
.myth .m{}.myth .m .lab{color:var(--soft)}
.myth .m h2{font-size:60px;color:var(--soft);text-decoration:line-through;text-decoration-color:var(--accent);text-decoration-thickness:5px;margin-top:14px}
.myth .r{margin-top:48px;background:#fff;border-left:12px solid var(--accent);border-radius:28px;padding:44px 48px}
.myth .box{position:static}
.myth .r .lab{color:var(--accent)}
.myth .r h2{font-size:58px;margin:14px 0 18px}
.myth .r p{font-size:36px;color:var(--soft)}
/* cta */
.cta{background:var(--ink);color:#FAFAF8}
.cta .glow{position:absolute;width:900px;height:900px;border-radius:50%;right:-300px;top:-250px;background:radial-gradient(circle,rgba(255,122,92,.35),rgba(255,122,92,0) 70%)}
.cta .txt{position:absolute;left:64px;right:64px;top:300px}
.cta h1{font-size:92px;margin:30px 0 36px}
.cta h1 em{font-style:normal;color:var(--accent)}
.cta ul{list-style:none;margin-bottom:60px}
.cta li{font-size:38px;font-weight:500;padding:14px 0;display:flex;gap:18px;align-items:center}
.cta li svg{flex:none}
.cta .btn{display:inline-block;background:var(--accent);color:#12141C;font-family:'Bricolage';font-weight:800;font-size:38px;padding:26px 44px;border-radius:60px}
[hidden]{display:none!important}
.credit{position:absolute;right:64px;bottom:96px;font-size:18px;opacity:.75;z-index:5}
"""

CHECK = '<svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="#FF7A5C" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg>'

def e(t):
    return html.escape(t or "")

def photo(name):
    return b64(PHOTOS / name, "image/jpeg")

def chrome(i, n, dark):
    c = "#FAFAF8" if dark else "#1F3A3D"
    numbg = "rgba(18,20,28,.35)" if dark else "rgba(31,58,61,.08)"
    acc = "#FAFAF8" if dark else "#FF7A5C"
    top = f"""<div class="top"><div class="logo" style="color:{c}">{LOGO_SVG.format(s=44,c='#FF7A5C')}<span>Ton <span class="acc" style="color:{acc}">Itinéraire</span></span></div>
<div class="num" style="color:{c};background:{numbg}">{i}/{n}</div></div>"""
    dots = f'<div class="dots" style="color:{c}">' + "".join(f'<i class="{"on" if k==i else ""}"></i>' for k in range(1, n+1)) + "</div>"
    return top, dots

def slide_html(s, i, n):
    t = s["type"]
    dark = t in ("cover", "cta")
    top, dots = chrome(i, n, dark)
    if n == 1:
        top = top.replace('class="num"', 'class="num" hidden'); dots = ""
    credit = f'<div class="credit" style="color:{"#FAFAF8" if dark else "#4A6467"}">Photo : {e(s["credit"])} / Unsplash</div>' if s.get("credit") else ""
    if t == "cover":
        body = f"""<div class="s cover"><img class="bg" src="{photo(s['photo'])}"><div class="shade"></div>
<div class="txt"><span class="pill">{e(s['badge'])}</span><h1>{e(s['title'])}</h1><p>{e(s.get('sub'))}</p></div>"""
    elif t == "photo":
        body = f"""<div class="s photo"><div class="imgwrap"><img src="{photo(s['photo'])}"></div>
<div class="panel"><div class="kicker">{e(s['kicker'])}</div><h2>{e(s['title'])}</h2><p>{e(s['text'])}</p></div>"""
        top, _ = chrome(i, n, True)
    elif t == "fact":
        body = f"""<div class="s fact"><div class="band"><img src="{photo(s['photo'])}"></div>
<div class="flow"><div class="big">{e(s['big'])}</div><h2>{e(s['title'])}</h2><p>{e(s['text'])}</p></div>"""
    elif t == "myth":
        body = f"""<div class="s myth"><div class="band"><img src="{photo(s['photo'])}"></div>
<div class="flow"><div class="box m"><div class="lab">Mythe</div><h2>{e(s['myth'])}</h2></div>
<div class="box r"><div class="lab">Réalité</div><h2>{e(s['title'])}</h2><p>{e(s['text'])}</p></div></div>"""
        top, _ = chrome(i, n, True)
    elif t == "cta":
        lis = "".join(f"<li>{CHECK}<span>{e(x)}</span></li>" for x in s["points"])
        body = f"""<div class="s cta"><div class="glow"></div><div class="txt"><span class="pill">{e(s.get('badge','Votre voyage'))}</span>
<h1>{s['title_html']}</h1><ul>{lis}</ul><span class="btn">{e(s.get('button','Lien en bio'))}</span></div>"""
    else:
        raise ValueError(t)
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{FONTS}{CSS}</style></head><body>{body}{top}{dots}{credit}</div></body></html>"

STORY_CSS = """
body.st{width:1080px;height:1920px}
.story{position:relative;width:1080px;height:1920px;overflow:hidden;color:#FAFAF8}
.story img.bg{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}
.story .shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(18,20,28,.55) 0%,rgba(18,20,28,0) 22%,rgba(18,20,28,0) 45%,rgba(18,20,28,.9) 100%)}
.story .top{top:120px}
.story .txt{position:absolute;left:72px;right:72px;bottom:330px}
.story h1{font-size:112px;margin:30px 0 28px}
.story p{font-size:44px;opacity:.94}
.story .q{position:absolute;left:72px;right:72px;bottom:200px;font-family:'Bricolage';font-weight:800;font-size:40px;display:flex;gap:16px;align-items:center}
.story .q span{background:#FAFAF8;color:#1F3A3D;padding:18px 30px;border-radius:50px}
.story .credit{bottom:140px;right:72px;color:#FAFAF8}
"""

def story_html(s):
    top = f"""<div class="top"><div class="logo" style="color:#FAFAF8">{LOGO_SVG.format(s=52,c='#FF7A5C')}<span style="font-size:40px">Ton <span>Itinéraire</span></span></div></div>"""
    credit = f'<div class="credit">Photo : {e(s["credit"])} / Unsplash</div>' if s.get("credit") else ""
    q = f'<div class="q"><span>{e(s["cta"])}</span></div>' if s.get("cta") else ""
    body = f"""<div class="story"><img class="bg" src="{photo(s['photo'])}"><div class="shade"></div>{top}
<div class="txt"><span class="pill">{e(s['badge'])}</span><h1>{e(s['title'])}</h1><p>{e(s.get('text'))}</p></div>{q}{credit}</div>"""
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{FONTS}{CSS}{STORY_CSS}</style></head><body class='st'>{body}</body></html>"

def render(spec, outdir):
    if spec.get("format") == "story":
        return render_story(spec, outdir)
    os.makedirs(outdir, exist_ok=True)
    n = len(spec["slides"])
    files, problems = [], []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1350})
        for i, s in enumerate(spec["slides"], 1):
            h = slide_html(s, i, n)
            assert "{{" not in h, "placeholder oublié"
            pg.set_content(h)
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(300)
            # contrôle débordement : aucun texte ne sort du cadre ni ne chevauche le bas (dots)
            over = pg.evaluate("""()=>[...document.querySelectorAll('h1,h2,p,li,.pill,.btn')].filter(el=>{const r=el.getBoundingClientRect();return r.right>1080-40||r.bottom>1350-90||r.left<40}).map(el=>el.textContent.slice(0,40))""")
            if over:
                problems.append((i, over))
            f = os.path.join(outdir, f"{spec['slug']}-{i:02d}.jpg")
            pg.screenshot(path=f, type="jpeg", quality=92)
            files.append(f)
        b.close()
    return files, problems

def render_story(spec, outdir):
    os.makedirs(outdir, exist_ok=True)
    files, problems = [], []
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1080, "height": 1920})
        for i, s in enumerate(spec["slides"], 1):
            h = story_html(s)
            assert "{{" not in h, "placeholder oublié"
            pg.set_content(h); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
            over = pg.evaluate("""()=>[...document.querySelectorAll('h1,p,.pill,.q span')].filter(el=>{const r=el.getBoundingClientRect();return r.right>1080-40||r.bottom>1920-120||r.left<40||r.top<250}).map(el=>el.textContent.slice(0,40))""")
            if over: problems.append((i, over))
            f = os.path.join(outdir, f"{spec['slug']}-{i:02d}.jpg")
            pg.screenshot(path=f, type="jpeg", quality=92); files.append(f)
        b.close()
    return files, problems

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    files, problems = render(spec, sys.argv[2])
    print("\n".join(files))
    print("PROBLEMES:", problems if problems else "aucun")
