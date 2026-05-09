import streamlit as st
import streamlit.components.v1 as components

# Video IDs — all free 4K Utah drone footage from YouTube
# 0: Utah Mountains / Wasatch & Uinta Backcountry 4K
# 1: Salt Lake City 4K Cinematic (golden hour → night, Little Cottonwood Canyon)
# 2: Winter Wasatch Mountain Landscapes
# 3: Best of Utah 4K (southern Utah, arches, canyons)
_VIDEOS = [
    ("37Q9p5CfvMg", "Wasatch Backcountry"),
    ("2U4Qbo0YXlY", "Salt Lake City"),
    ("HpX0l1xNBLY", "Wasatch Front"),
    ("_KxyKph-YpU", "Southern Utah"),
]

def _yt(vid_id: str) -> str:
    return (
        "https://www.youtube-nocookie.com/embed/"
        + vid_id
        + "?autoplay=1&mute=1&controls=0&loop=1&playlist="
        + vid_id
        + "&rel=0&playsinline=1&modestbranding=1&disablekb=1&iv_load_policy=3&fs=0&start=10"
    )

_SLOTS = "\n".join(
    f'<div class="yt-slot{"  active" if i == 0 else ""}" id="v{i}">'
    f'<iframe src="{_yt(vid)}" allow="autoplay; encrypted-media; fullscreen" frameborder="0" allowfullscreen></iframe>'
    f'</div>'
    for i, (vid, _) in enumerate(_VIDEOS)
)

_SCENE_DATA = str([[vid, lbl] for vid, lbl in _VIDEOS]).replace("'", '"')

_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<script>
// Make this iframe fill the entire parent viewport immediately
(function go() {{
    try {{
        var frames = window.parent.document.querySelectorAll('iframe');
        for (var i = 0; i < frames.length; i++) {{
            if (frames[i].contentWindow === window) {{
                frames[i].style.cssText = 'position:fixed!important;inset:0!important;top:0!important;left:0!important;width:100vw!important;height:100vh!important;border:none!important;z-index:9999!important;margin:0!important;';
                ['stHeader','stToolbar','stStatusWidget','stDecoration'].forEach(function(t) {{
                    var el = window.parent.document.querySelector('[data-testid="' + t + '"]');
                    if (el) el.style.display = 'none';
                }});
            }}
        }}
    }} catch(e) {{}}
}})();
setTimeout(function() {{
    try {{
        var frames = window.parent.document.querySelectorAll('iframe');
        for (var i = 0; i < frames.length; i++) {{
            if (frames[i].contentWindow === window) {{
                frames[i].style.cssText = 'position:fixed!important;inset:0!important;top:0!important;left:0!important;width:100vw!important;height:100vh!important;border:none!important;z-index:9999!important;margin:0!important;';
            }}
        }}
    }} catch(e) {{}}
}}, 400);
</script>
<style>
*, *::before, *::after {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{ width:100%; height:100%; overflow:hidden; background:#060C18;
    font-family:-apple-system,BlinkMacSystemFont,'SF Pro Display','Segoe UI',system-ui,sans-serif; }}

/* ── Gradient fallback (shows while videos load) ── */
.bg-fallback {{
    position:fixed; inset:0; z-index:0;
    background:linear-gradient(168deg,#0A0302 0%,#2D0D05 20%,#7A2808 45%,#B85020 70%,#E8A050 100%);
    animation:fallback 30s ease-in-out infinite;
}}
@keyframes fallback {{
    0%,100% {{ background:linear-gradient(168deg,#0A0302 0%,#7A2808 45%,#E8A050 100%); }}
    33%      {{ background:linear-gradient(180deg,#0A1020 0%,#4A3060 45%,#A4405C 100%); }}
    66%      {{ background:linear-gradient(175deg,#050C18 0%,#102035 45%,#1E4530 100%); }}
}}

/* ── YouTube video slots ── */
.yt-wrapper {{ position:fixed; inset:0; z-index:1; overflow:hidden; }}

.yt-slot {{
    position:absolute; inset:0;
    opacity:0; transition:opacity 2s ease;
}}
.yt-slot.active {{ opacity:1; }}

/* Fill viewport regardless of aspect ratio — classic YouTube bg technique */
.yt-slot iframe {{
    position:absolute;
    width:100vw; height:56.25vw;   /* 16:9 at full width */
    min-height:100vh;
    min-width:177.78vh;            /* 16:9 at full height */
    top:50%; left:50%;
    transform:translate(-50%,-50%);
    border:none; pointer-events:none;
}}

/* ── Overlay for readability ── */
.overlay {{
    position:fixed; inset:0; z-index:2; pointer-events:none;
    background:
        radial-gradient(ellipse 90% 70% at 50% 35%, transparent 0%, rgba(0,0,0,.38) 100%),
        linear-gradient(to bottom, rgba(0,0,0,.18) 0%, rgba(0,0,0,.18) 45%, rgba(0,0,0,.72) 100%);
}}

/* ── Page layout ── */
.page {{
    position:fixed; inset:0; z-index:3;
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    padding:24px 20px 96px;
}}

/* ── Brand ── */
.eyebrow {{
    display:inline-flex; align-items:center; gap:7px;
    background:rgba(245,166,35,.12); border:1px solid rgba(245,166,35,.38);
    color:#F5A623; padding:5px 15px; border-radius:100px;
    font-size:10.5px; font-weight:700; letter-spacing:.18em; text-transform:uppercase;
    margin-bottom:24px;
}}
.dot-live {{
    width:5px; height:5px; border-radius:50%; background:#F5A623;
    animation:pulse 2.2s ease-in-out infinite;
}}
@keyframes pulse {{ 0%,100%{{opacity:1;transform:scale(1)}} 50%{{opacity:.3;transform:scale(.6)}} }}

h1 {{
    color:#fff; font-size:clamp(2.6rem,5.5vw,4.2rem); font-weight:800;
    line-height:1.05; letter-spacing:-.03em; text-align:center; margin-bottom:18px;
    text-shadow:0 2px 32px rgba(0,0,0,.7);
}}
.sub {{
    color:rgba(255,255,255,.65); font-size:clamp(.95rem,1.6vw,1.08rem);
    line-height:1.65; text-align:center; max-width:440px; margin-bottom:40px;
    text-shadow:0 1px 8px rgba(0,0,0,.5);
}}

/* ── Card ── */
.card {{
    width:100%; max-width:390px;
    background:rgba(4,8,18,.65); border:1px solid rgba(255,255,255,.11);
    border-radius:22px; padding:34px 36px 28px;
    box-shadow:0 24px 72px rgba(0,0,0,.55),inset 0 1px 0 rgba(255,255,255,.06);
    backdrop-filter:blur(32px); -webkit-backdrop-filter:blur(32px);
}}
.card-label {{
    font-size:10.5px; font-weight:600; letter-spacing:.14em; text-transform:uppercase;
    color:rgba(255,255,255,.32); text-align:center; margin-bottom:20px;
}}
.btn {{
    display:block; width:100%; padding:16px 22px 14px; border-radius:13px; border:none;
    cursor:pointer; font-family:inherit; text-align:left; margin-bottom:10px;
    transition:transform .14s ease, box-shadow .14s ease, background .14s ease;
}}
.btn:last-of-type {{ margin-bottom:0; }}
.btn:active {{ transform:scale(.98)!important; }}
.btn-title {{ font-size:15px; font-weight:700; letter-spacing:.01em; display:block; margin-bottom:3px; }}
.btn-sub {{ font-size:11.5px; font-weight:400; opacity:.75; display:block; line-height:1.4; }}
.btn-e {{ background:#F5A623; color:#1B3A5C; box-shadow:0 4px 20px rgba(245,166,35,.3); }}
.btn-e:hover {{ transform:translateY(-2px); box-shadow:0 8px 30px rgba(245,166,35,.5); background:#F7B540; }}
.btn-e .btn-sub {{ opacity:.65; }}
.btn-i {{ background:rgba(255,255,255,.08); color:rgba(255,255,255,.88); border:1px solid rgba(255,255,255,.15); }}
.btn-i:hover {{ transform:translateY(-2px); background:rgba(255,255,255,.15); }}
.demo-note {{ margin-top:18px; text-align:center; font-size:11px; color:rgba(255,255,255,.22); letter-spacing:.05em; }}

/* ── Stats ── */
.stats {{ display:flex; align-items:center; margin-top:30px; }}
.stat {{ padding:0 24px; text-align:center; }}
.stat:first-child {{ padding-left:0; }} .stat:last-child {{ padding-right:0; }}
.stat-n {{ font-size:1.1rem; font-weight:700; color:rgba(255,255,255,.9); text-shadow:0 1px 8px rgba(0,0,0,.4); }}
.stat-l {{ font-size:10px; letter-spacing:.1em; text-transform:uppercase; color:rgba(255,255,255,.35); margin-top:3px; }}
.divider {{ width:1px; height:26px; background:rgba(255,255,255,.12); }}

/* ── Scene indicator ── */
.indicator {{
    position:fixed; bottom:28px; left:50%; transform:translateX(-50%);
    display:flex; align-items:center; gap:10px; z-index:4;
}}
.dots {{ display:flex; gap:7px; align-items:center; }}
.dot {{ width:4px; height:4px; border-radius:50%; background:rgba(255,255,255,.2); transition:background .4s ease,transform .4s ease; }}
.dot.on {{ background:rgba(255,255,255,.75); transform:scale(1.5); }}
.scene-lbl {{ color:rgba(255,255,255,.3); font-size:10px; letter-spacing:.2em; text-transform:uppercase; transition:opacity .4s ease; white-space:nowrap; user-select:none; }}
</style>
</head>
<body>

<div class="bg-fallback"></div>

<div class="yt-wrapper">
{_SLOTS}
</div>

<div class="overlay"></div>

<div class="page">
    <div class="eyebrow"><div class="dot-live"></div>Utah &nbsp;·&nbsp; The Startup State</div>
    <h1>Build the<br>Startup State.</h1>
    <p class="sub">Utah's platform connecting founders with funding<br>and investors with the next great company.</p>

    <div class="card">
        <div class="card-label">I am a...</div>
        <button class="btn btn-e" onclick="enter('entrepreneur')">
            <span class="btn-title">💼 &nbsp; Entrepreneur</span>
            <span class="btn-sub">Utah is the best state to build — let's find your funding.</span>
        </button>
        <button class="btn btn-i" onclick="enter('investor')">
            <span class="btn-title">📊 &nbsp; Investor</span>
            <span class="btn-sub">Utah's next breakout startup is already here. Come find it.</span>
        </button>
        <div class="demo-note">Demo mode &nbsp;·&nbsp; No account needed</div>
    </div>

    <div class="stats">
        <div class="stat"><div class="stat-n">500+</div><div class="stat-l">Grants</div></div>
        <div class="divider"></div>
        <div class="stat"><div class="stat-n">Live</div><div class="stat-l">Startup Map</div></div>
        <div class="divider"></div>
        <div class="stat"><div class="stat-n">Free</div><div class="stat-l">Always</div></div>
    </div>
</div>

<div class="indicator">
    <div class="dots">
        <div class="dot on" id="d0"></div><div class="dot" id="d1"></div>
        <div class="dot" id="d2"></div><div class="dot" id="d3"></div>
    </div>
    <div class="scene-lbl" id="sn">{_VIDEOS[0][1]}</div>
</div>

<script>
var scenes = {_SCENE_DATA};
var cur = 0;
var n = scenes.length;

function enter(role) {{
    try {{ window.parent.location.href = window.parent.location.pathname + '?role=' + role; }}
    catch(e) {{ window.location.href = '?role=' + role; }}
}}

function nextScene() {{
    document.getElementById('d'+cur).classList.remove('on');
    document.getElementById('v'+cur).classList.remove('active');
    cur = (cur + 1) % n;
    document.getElementById('d'+cur).classList.add('on');
    document.getElementById('v'+cur).classList.add('active');
    var lbl = document.getElementById('sn');
    lbl.style.opacity = '0';
    setTimeout(function() {{ lbl.textContent = scenes[cur][1]; lbl.style.opacity = '1'; }}, 400);
}}

document.getElementById('sn').style.transition = 'opacity .4s ease';
setInterval(nextScene, 18000);
</script>
</body>
</html>"""


def show_landing():
    st.markdown(
        """
        <style>
        [data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stSidebar"],
        [data-testid="stStatusWidget"],[data-testid="stDecoration"],
        #MainMenu, footer { display:none !important; }
        .block-container { padding:0 !important; margin:0 !important; max-width:100% !important; }
        [data-testid="stAppViewContainer"] { padding:0 !important; background:#060C18 !important; }
        [data-testid="stMain"], .main { padding:0 !important; background:#060C18 !important; }
        a#page-top { display:none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    components.html(_HTML, height=10000, scrolling=False)
