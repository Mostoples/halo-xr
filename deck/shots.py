"""HALO-XR · ambil aset deck dari app yang berjalan (python deck/shots.py, server: python serve.py 8766).
Hasil: deck/build/screens/*.png (layar ponsel), deck/build/media/*.png (organ cut-out, piramida, logo)."""
import asyncio, pathlib, sys
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCR = ROOT / "deck/build/screens"; MED = ROOT / "deck/build/media"
SCR.mkdir(parents=True, exist_ok=True); MED.mkdir(parents=True, exist_ok=True)
URL = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8766") + "/?nosw"
LANG = sys.argv[2] if len(sys.argv) > 2 else "en"
ARGS = ["--use-gl=angle", "--ignore-gpu-blocklist"]

CUTOUT_CSS = """
html,body{background:transparent!important}
body::before,body::after,.app>:not(main),#s-viewer>:not(.viewer-layout),.controls,.viewer-layout>.stack:last-child{display:none!important}
.stage-card{background:none!important;box-shadow:none!important}
.stage{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important;aspect-ratio:auto!important;border-radius:0!important;z-index:999;background:transparent!important}
.stage::before,.labels,.style-toggle,.stage-hint,.loading{display:none!important}
"""


async def phone(b):
    pg = await b.new_page(viewport={"width": 412, "height": 892}, device_scale_factor=3)
    await pg.goto(URL + f"&lang={LANG}", wait_until="networkidle"); await pg.wait_for_timeout(2500)
    await pg.evaluate("APP.set({auto:true})")
    shots = [
        ("home", "APP.go('home')"),
        ("library", "APP.go('library')"),
        ("viewer_holo", "APP.set({organ:'heart',style:'holo',peel:0}).then(()=>APP.go('viewer'))"),
        ("viewer_cut", "APP.set({organ:'heart',style:'real',peel:2}).then(()=>{APP.go('viewer');APP.set({focus:3})})"),
        ("viewer_cell", "APP.set({organ:'cell',peel:1}).then(()=>APP.go('viewer'))"),
        ("learn", "APP.set({quiz:{pre:40,post:80}}).then(()=>APP.go('learn'))"),
        ("device", "(()=>{APP.go('device');for(const g of ['right','cw','ccw','left','forward','backward'])APP.gesture(g)})()"),
    ]
    for name, js in shots:
        await pg.evaluate(js); await pg.wait_for_timeout(2600)
        await pg.screenshot(path=str(SCR / f"{name}_{LANG}.png"))
    await pg.close()


async def cutouts(b):
    pg = await b.new_page(viewport={"width": 900, "height": 900}, device_scale_factor=2)
    await pg.goto(URL + f"&lang={LANG}&screen=viewer", wait_until="networkidle"); await pg.wait_for_timeout(2000)
    await pg.add_style_tag(content=CUTOUT_CSS)
    for organ, style, peel, yaw in [("heart", "real", 0, 0.3), ("brain", "real", 0, 0.5), ("lungs", "real", 0, 0), ("eyeball", "real", 0, 0.6),
                                    ("heart", "real", 2, 0.25), ("heart", "holo", 0, 0.3), ("brain", "holo", 0, 0.5)]:
        await pg.evaluate(f"""APP.set({{organ:'{organ}',style:'{style}',auto:false}}).then(()=>{{
            const v=APP.viewer; v.markers.forEach(m=>v.pivot.remove(m)); v.markers=[];
            v.setPeel({peel}); v.state.yaw=v.state.tYaw={yaw}; v.state.pitch=v.state.tPitch=0.08; v._resize(); }})""")
        await pg.evaluate("s=>{const e=document.querySelector('.stage'); if(s==='holo') e.style.setProperty('background','radial-gradient(120% 90% at 50% 0%,#12285A 0%,#08132F 55%,#040917 100%)','important'); else e.style.removeProperty('background');}", style)
        await pg.wait_for_timeout(2200)
        bg = style == "real"
        await pg.screenshot(path=str(MED / f"{organ}_{style}{'_cut' if peel else ''}.png"), omit_background=bg)
    await pg.close()


async def pyramid(b):
    pg = await b.new_page(viewport={"width": 1500, "height": 1000}, device_scale_factor=1.5)
    await pg.goto(URL + f"&lang={LANG}", wait_until="networkidle"); await pg.wait_for_timeout(2000)
    for organ, style in [("heart", "real"), ("brain", "holo")]:
        await pg.evaluate(f"APP.set({{organ:'{organ}',style:'{style}',auto:false,focus:0}}).then(()=>APP.enterPyramid())")
        await pg.wait_for_timeout(2600)
        await pg.evaluate("document.getElementById('pyrHud').classList.add('hide')"); await pg.wait_for_timeout(600)
        await pg.screenshot(path=str(MED / f"pyramid_{organ}_{style}.png"))
        await pg.evaluate("APP.exitPyramid()")
    await pg.close()


def logos():
    import fitz
    from PIL import Image
    pdf = next(ROOT.glob("*.pdf"))
    pg = fitz.open(pdf)[0]
    pix = pg.get_pixmap(matrix=fitz.Matrix(3, 3), clip=fitz.Rect(520, 652, 920, 800))
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    im.save(MED / "logos_raw.png")
    # buang latar hitam: alpha dari jarak ke hitam (logo punya warna cerah / garis putih)
    import numpy as np
    a = np.asarray(im).astype(np.float32); lum = a.max(axis=2)
    alpha = np.clip((lum - 28) / 40, 0, 1) * 255
    rgba = np.dstack([a, alpha]).astype(np.uint8)
    out = Image.fromarray(rgba, "RGBA"); out = out.crop(out.getbbox()); out.save(MED / "logos.png")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=ARGS)
        if "--cut" not in sys.argv: await phone(b)
        await cutouts(b)
        if LANG == "en": await pyramid(b)
        await b.close()
    if LANG == "en": logos()
    print("ok", LANG)

asyncio.run(main())
