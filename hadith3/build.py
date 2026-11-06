import json, html, sys
W = sys.argv[1]  # work dir
OUT = sys.argv[2]
cues = json.load(open(f"{W}/cues.json"))
DUR = 375.70

def esc(s): return html.escape(s, quote=True)

def star(size, stroke, fill="none", sw=2):
    # 8-point star (two overlapping squares) + inner circle
    return f'''<svg width="{size}" height="{size}" viewBox="-50 -50 100 100">
<g fill="{fill}" stroke="{stroke}" stroke-width="{sw}">
<rect x="-32" y="-32" width="64" height="64"/>
<rect x="-32" y="-32" width="64" height="64" transform="rotate(45)"/>
<circle r="17"/></g><circle r="7" fill="{stroke}"/></svg>'''

# seamless geometric tile (8-point star lattice)
TILE = ("data:image/svg+xml;utf8," +
  "<svg xmlns='http://www.w3.org/2000/svg' width='120' height='120' viewBox='0 0 120 120'>"
  "<g fill='none' stroke='%23ffffff' stroke-width='1.6'>"
  "<rect x='35' y='35' width='50' height='50'/>"
  "<rect x='35' y='35' width='50' height='50' transform='rotate(45 60 60)'/>"
  "<circle cx='60' cy='60' r='14'/>"
  "<path d='M0 0 L25 25 M120 0 L95 25 M0 120 L25 95 M120 120 L95 95'/>"
  "</g></svg>")
TILE_BG = TILE.replace("%23ffffff", "%231f5c96")

cue_html = []
for i, c in enumerate(cues):
    st, du = c["start"], round(c["end"] - c["start"], 2)
    k = c["kind"]
    inner = ""
    if c["ar"]:
        ar = c["ar"]
        if k == "q":
            inner += f'<div class="ar quran">﴿{esc(ar)}﴾</div>'
        else:
            inner += f'<div class="ar">{esc(ar)}</div>'
        inner += '<div class="sep"></div>'
    cls = "ms" if c["ar"] else "ms solo"
    inner += f'<div class="{cls}">{esc(c["ms"])}</div>'
    if c["ref"]:
        inner += f'<div class="ref {"qref" if k=="q" else ""}">{esc(c["ref"])}</div>'
    cue_html.append(
        f'<div class="clip cue k-{k}" id="c{i}" data-start="{st}" data-duration="{du}" data-track-index="3">'
        f'<div class="fit">{inner}</div></div>')

doc = f'''<!doctype html>
<html lang="ms">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=1080, height=1350" />
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Amiri+Quran&family=Noto+Naskh+Arabic:wght@500;700&family=Plus+Jakarta+Sans:wght@500;700;800&display=block" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>
:root {{
  --navy:#0d3b6e; --navy2:#15558f; --gold:#c9a24a; --gold2:#e3c26f;
  --ink:#10294a; --muted:#5f7590; --paper:#ffffff; --ground:#e9f0f7;
}}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:1080px; height:1350px; overflow:hidden; background:var(--ground); }}
#root {{ position:relative; width:1080px; height:1350px; overflow:hidden; font-family:'Plus Jakarta Sans',sans-serif; background:var(--ground); }}
.bgpat {{ position:absolute; left:-120px; top:-120px; width:1320px; height:1590px; background-image:url("{TILE_BG}"); background-size:120px 120px; opacity:.10; }}
/* header */
#hdr {{ position:absolute; left:0; top:0; width:1080px; height:248px; overflow:hidden;
  background:linear-gradient(135deg,var(--navy) 0%,var(--navy2) 100%); }}
#hdrpat {{ position:absolute; left:-120px; top:-120px; width:1440px; height:488px; background-image:url("{TILE}"); background-size:120px 120px; opacity:.09; }}
#hdr .glow {{ position:absolute; right:-160px; top:-160px; width:520px; height:520px; border-radius:50%;
  background:radial-gradient(circle, rgba(227,194,111,.22) 0%, rgba(227,194,111,0) 70%); }}
#emb {{ position:absolute; left:46px; top:52px; width:104px; height:104px; }}
#emb svg {{ display:block; }}
#title {{ position:absolute; left:178px; right:40px; top:48px; color:#fff; font-weight:800; font-size:44px; letter-spacing:.2px; line-height:1.1; }}
#gline {{ position:absolute; left:178px; top:128px; width:110px; height:4px; border-radius:2px; background:linear-gradient(90deg,var(--gold),var(--gold2)); transform-origin:left center; }}
#spk {{ position:absolute; left:178px; right:40px; top:150px; color:#eaf1fa; font-size:29px; font-weight:700; line-height:1.4; white-space:nowrap; }}
#spk .arn {{ font-family:'Noto Naskh Arabic',serif; font-weight:700; font-size:31px; }}
#hdr .rule {{ position:absolute; left:0; bottom:0; width:1080px; height:5px; background:linear-gradient(90deg,var(--gold),var(--gold2),var(--gold)); }}
/* video */
#vframe {{ position:absolute; left:24px; top:272px; width:1032px; height:581px; border-radius:20px; overflow:hidden;
  box-shadow:0 10px 30px rgba(13,59,110,.22); border:3px solid #fff; background:#000; }}
#vid {{ position:absolute; left:0; top:0; width:100%; height:100%; object-fit:cover; }}
/* subtitle card */
#card {{ position:absolute; left:24px; top:880px; width:1032px; height:438px; background:var(--paper); border-radius:20px;
  box-shadow:0 10px 30px rgba(13,59,110,.14); }}
.corner {{ position:absolute; width:46px; height:46px; border-color:var(--gold); border-style:solid; border-width:0; }}
.tl {{ left:18px; top:18px; border-top-width:4px; border-left-width:4px; border-top-left-radius:8px; }}
.tr {{ right:18px; top:18px; border-top-width:4px; border-right-width:4px; border-top-right-radius:8px; }}
.bl {{ left:18px; bottom:18px; border-bottom-width:4px; border-left-width:4px; border-bottom-left-radius:8px; }}
.br {{ right:18px; bottom:18px; border-bottom-width:4px; border-right-width:4px; border-bottom-right-radius:8px; }}
.cue {{ position:absolute; left:24px; top:880px; width:1032px; height:438px; display:flex; align-items:center; justify-content:center; padding:44px 64px; }}
.fit {{ width:100%; text-align:center; }}
.ar {{ font-family:'Amiri',serif; font-weight:700; direction:rtl; color:var(--navy); font-size:44px; line-height:1.65; white-space:pre-line; }}
.ar.quran {{ font-family:'Amiri Quran','Amiri',serif; font-weight:400; color:#0b4a3f; font-size:44px; line-height:1.9; }}
.sep {{ width:90px; height:3px; margin:14px auto 16px; background:linear-gradient(90deg,var(--gold),var(--gold2)); border-radius:2px; }}
.ms {{ color:var(--ink); font-weight:700; font-size:35px; line-height:1.36; }}
.ms.solo {{ font-size:44px; line-height:1.36; }}
.ref {{ margin-top:14px; color:var(--muted); font-weight:700; font-size:23px; }}
.ref.qref {{ color:#a07f2c; }}
/* progress */
#prog {{ position:absolute; left:24px; top:1334px; width:1032px; height:5px; border-radius:3px; background:rgba(13,59,110,.12); overflow:hidden; }}
#progfill {{ position:absolute; left:0; top:0; width:1032px; height:5px; background:linear-gradient(90deg,var(--navy2),var(--gold)); transform-origin:left center; }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="1080" data-height="1350" data-fps="25">
  <div class="bgpat" id="bgpat"></div>
  <div id="hdr">
    <div id="hdrpat"></div>
    <div class="glow"></div>
    <div id="emb">{star(104, "#e3c26f", "rgba(227,194,111,0.10)", 3)}</div>
    <div id="title">SYARAH HADITH 40 (HADITH KETIGA)</div>
    <div id="gline"></div>
    <div id="spk">Dr. Othman Alkamees - <span class="arn">الشيخ الدكتور عثمان الخميس</span></div>
    <div class="rule"></div>
  </div>
  <div id="vframe">
    <video id="vid" class="clip" src="assets/src.mp4" data-start="0" data-duration="{DUR}" data-has-audio="true" data-track-index="1" playsinline></video>
  </div>
  <div id="card">
    <div class="corner tl"></div><div class="corner tr"></div><div class="corner bl"></div><div class="corner br"></div>
  </div>
  {"".join(cue_html)}
  <div id="prog"><div id="progfill"></div></div>
</div>
<script>
  // Fit long cues inside the card (deterministic, runs once at load)
  function fitAll() {{
    var probe = document.createElement('div');
    probe.style.cssText = 'position:absolute;left:-5000px;top:0;width:1032px;padding:0 64px;box-sizing:border-box;visibility:hidden;';
    document.body.appendChild(probe);
    var maxH = 438 - 80;
    document.querySelectorAll('.cue .fit').forEach(function(orig) {{
      var f = orig.cloneNode(true); probe.innerHTML = ''; probe.appendChild(f);
      var ar = f.querySelector('.ar'), ms = f.querySelector('.ms');
      var a0 = ar ? parseFloat(getComputedStyle(ar).fontSize) : 0;
      var m0 = parseFloat(getComputedStyle(ms).fontSize), s = 1.0;
      while (f.offsetHeight > maxH && s > 0.55) {{
        s -= 0.03;
        if (ar) ar.style.fontSize = (a0 * s) + 'px';
        ms.style.fontSize = (m0 * Math.max(s, 0.74)) + 'px';
      }}
      if (s < 1) {{
        var oa = orig.querySelector('.ar'), om = orig.querySelector('.ms');
        if (oa) oa.style.fontSize = ar.style.fontSize;
        om.style.fontSize = ms.style.fontSize;
      }}
    }});
    probe.remove();
  }}
  window.__timelines = window.__timelines || {{}};
  const tl = gsap.timeline({{ paused: true }});
  const D = {DUR};
  // intro: header elements settle in (0–1.2s); subtitles are never delayed
  tl.from('#title', {{ opacity: 0, x: -30, duration: 0.8, ease: 'power3.out' }}, 0.1);
  tl.from('#gline', {{ scaleX: 0, duration: 0.8, ease: 'power3.out' }}, 0.35);
  tl.from('#spk', {{ opacity: 0, y: 12, duration: 0.8, ease: 'power3.out' }}, 0.5);
  tl.from('#emb', {{ opacity: 0, scale: 0.6, duration: 0.9, ease: 'back.out(1.6)' }}, 0.0);
  // slow ambient motion for whole film
  tl.to('#emb svg', {{ rotation: 360 * 4, duration: D, ease: 'none', transformOrigin: '50% 50%' }}, 0);
  tl.to('#hdrpat', {{ x: 120, y: 120, duration: D, ease: 'none' }}, 0);
  tl.to('#bgpat', {{ y: 120, duration: D, ease: 'none' }}, 0);
  tl.fromTo('#progfill', {{ scaleX: 0 }}, {{ scaleX: 1, duration: D, ease: 'none' }}, 0);
  // gentle gold shimmer on the header line every ~12s
  for (let t = 12; t < D - 2; t += 12) {{
    tl.to('#gline', {{ scaleX: 1.35, duration: 0.9, ease: 'sine.inOut', yoyo: true, repeat: 1 }}, t);
  }}
  window.__timelines['main'] = tl;
  if (document.fonts && document.fonts.ready) {{ document.fonts.ready.then(fitAll); }} else {{ fitAll(); }}
  tl.seek(0);
</script>
</body>
</html>
'''
open(OUT, "w").write(doc)
print("cues:", len(cues))
