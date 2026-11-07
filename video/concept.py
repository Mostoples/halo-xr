"""HALO-XR · still konsep video tutorial (layout A & B) — python video/concept.py"""
import pathlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
B = ROOT / "video/build"; B.mkdir(parents=True, exist_ok=True)
F = lambda w, s: ImageFont.truetype(str(ROOT / f"video/fonts/PJS-{w}.ttf"), s)
W, H = 1920, 1080
INK, INK2, BLUE, DEEP, ICE, BG = (22, 35, 63), (74, 90, 122), (47, 123, 255), (22, 70, 214), (221, 235, 255), (233, 239, 247)


def background():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((x - W * 0.55) / W) ** 2 + ((y - H * 0.35) / H) ** 2)
    k = np.clip(d / 0.8, 0, 1)[..., None]
    img = np.array([246, 249, 253]) * (1 - k) + np.array([218, 227, 240]) * k
    for cx, cy, r, s, col in ((0.08, 0.12, 0.3, 40, (140, 198, 255)), (0.92, 0.95, 0.35, 34, (110, 160, 255))):
        g = np.exp(-(((x / W - cx) ** 2 + (y / H - cy) ** 2) / (r * r)))[..., None] * s / 255
        img = img * (1 - g) + np.array(col) * g
    return Image.fromarray(img.clip(0, 255).astype(np.uint8)).convert("RGBA")


def rr(size, box, r, fill=255):
    m = Image.new("L", size, 0); ImageDraw.Draw(m).rounded_rectangle(box, r, fill=fill); return m


def card(im, box, r=32, alpha=0.94, shadow=(40, 90, 200), blur=22):
    sh = rr(im.size, (box[0], box[1] + 14, box[2], box[3] + 14), r).filter(ImageFilter.GaussianBlur(blur))
    lay = Image.new("RGBA", im.size, shadow + (0,)); lay.putalpha(sh.point(lambda v: int(v * 0.28))); im.alpha_composite(lay)
    im.paste(Image.new("RGBA", im.size, (255, 255, 255, int(255 * alpha))), (0, 0), rr(im.size, box, r))


def grad_text(im, xy, text, font):
    d = ImageDraw.Draw(im); bb = d.textbbox(xy, text, font=font)
    m = Image.new("L", im.size, 0); ImageDraw.Draw(m).text(xy, text, font=font, fill=255)
    g = np.zeros((H, W, 4), np.uint8); t = np.clip((np.arange(W) - bb[0]) / max(1, bb[2] - bb[0]), 0, 1)[None, :, None]
    g[..., :3] = (np.array(BLUE) * (1 - t) + np.array(DEEP) * t).astype(np.uint8); g[..., 3] = 255
    im.paste(Image.fromarray(g), (0, 0), m)


def chip(im, xy, text, size=22, fill=(255, 255, 255), color=BLUE):
    d = ImageDraw.Draw(im); f = F("ExtraBold", size)
    w = d.textlength(text, font=f) + 44; h = size + 26
    card(im, (xy[0], xy[1], xy[0] + int(w), xy[1] + h), h // 2, 1.0, blur=12)
    d.text((xy[0] + 22, xy[1] + 11), text, font=f, fill=color)
    return int(w)


def pill(im, xy, text, icon=""):
    d = ImageDraw.Draw(im); f = F("Bold", 24)
    w = d.textlength(icon + text, font=f) + 48
    im.paste(Image.new("RGBA", im.size, ICE + (255,)), (0, 0), rr(im.size, (xy[0], xy[1], xy[0] + int(w), xy[1] + 52), 26))
    d.text((xy[0] + 24, xy[1] + 12), icon + text, font=f, fill=DEEP)
    return int(w)


def logo(im, x, y):
    ic = Image.open(ROOT / "assets/icon-512.png").convert("RGBA").resize((56, 56), Image.LANCZOS)
    im.alpha_composite(ic, (x, y)); ImageDraw.Draw(im).text((x + 70, y + 10), "HALO-XR", font=F("ExtraBold", 30), fill=INK)


def phone(im, scr_path, x, y, w, crop=2.05):
    s = Image.open(scr_path).convert("RGBA"); s = s.crop((0, 0, s.width, int(s.width * crop)))
    sw = w; sh = int(s.height * sw / s.width); s = s.resize((sw, sh), Image.LANCZOS)
    bz, rad = 18, 64
    body = (x, y, x + sw + 2 * bz, y + sh + 2 * bz)
    sha = rr(im.size, (body[0] + 20, body[1] + 40, body[2] + 20, body[3] + 40), rad + bz).filter(ImageFilter.GaussianBlur(50))
    lay = Image.new("RGBA", im.size, (70, 120, 235, 0)); lay.putalpha(sha.point(lambda v: int(v * 0.45))); im.alpha_composite(lay)
    im.paste(Image.new("RGBA", im.size, (236, 241, 248, 255)), (0, 0), rr(im.size, body, rad + bz))
    im.paste(Image.new("RGBA", im.size, (10, 14, 24, 255)), (0, 0), rr(im.size, (body[0] + 6, body[1] + 6, body[2] - 6, body[3] - 6), rad + bz - 6))
    s.putalpha(rr(s.size, (0, 0, sw - 1, sh - 1), rad)); im.alpha_composite(s, (x + bz, y + bz))
    ImageDraw.Draw(im).rounded_rectangle((x + bz + sw // 2 - 90, y + bz + 18, x + bz + sw // 2 + 90, y + bz + 62), 22, fill=(5, 7, 12, 255))


def progress(im, x, y, w, step, total):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x, y, x + w, y + 10), 5, fill=(205, 216, 233))
    d.rounded_rectangle((x, y, x + int(w * step / total), y + 10), 5, fill=BLUE)


# ---------------- Layout A: ponsel + panel teks (gaya showreel AQUENT) ----------------
im = background()
orb = Image.new("RGBA", im.size, (0, 0, 0, 0)); ImageDraw.Draw(orb).ellipse((180, 120, 980, 920), fill=(70, 150, 255, 120))
im.alpha_composite(orb.filter(ImageFilter.GaussianBlur(120)))
phone(im, ROOT / "deck/build/screens/viewer_cut_id.png", 330, 70, 430, crop=2.0)
logo(im, 1700 - 40, 60)
x0 = 1000
chip(im, (x0, 250), "LANGKAH 4 / 9 · KUPAS IRISAN")
d = ImageDraw.Draw(im)
d.text((x0, 330), "Kupas organnya,", font=F("ExtraBold", 76), fill=INK)
grad_text(im, (x0, 420), "lihat bagian dalam.", F("ExtraBold", 76))
d.multiline_text((x0, 540), "Setiap gestur memotong model lebih dalam.\nBagian dalam tampil gelap, tepi potongan bercahaya.", font=F("Medium", 32), fill=INK2, spacing=14)
px = x0
for ic, t in [("☝ ", "Telunjuk memutar"), ("🎙 ", "“kupas”"), ("", "Tombol Irisan")]:
    px += pill(im, (px, 680), t, "") + 16
progress(im, x0, 960, 700, 4, 9)
d.text((x0, 905), "Tutorial HALO-XR", font=F("Bold", 24), fill=(131, 146, 174))
im.convert("RGB").save(B / "concept_A.png")

# ---------------- Layout B: rekaman layar penuh + lower-third ----------------
im = background()
app = Image.open(B / "land_viewer.png").convert("RGBA").resize((1600, 900), Image.LANCZOS)
fx, fy = 160, 70
card(im, (fx - 14, fy - 14, fx + 1600 + 14, fy + 900 + 14), 40, 1.0, blur=30)
app.putalpha(rr(app.size, (0, 0, 1599, 899), 30)); im.alpha_composite(app, (fx, fy))
# lower-third
card(im, (110, 800, 1010, 1010), 34, 0.96)
d = ImageDraw.Draw(im)
d.ellipse((145, 840, 245, 940), fill=BLUE); d.text((195, 890), "4", font=F("ExtraBold", 50), fill="white", anchor="mm")
d.text((275, 832), "Kupas irisan", font=F("ExtraBold", 46), fill=INK)
d.text((277, 898), "Telunjuk memutar  ·  ucapkan “kupas”  ·  tombol Irisan", font=F("Medium", 26), fill=INK2)
progress(im, 277, 958, 680, 4, 9)
# hint gestur
card(im, (1430, 110, 1730, 200), 45, 0.96)
d.text((1580, 155), "☝  memutar", font=F("Bold", 30), fill=DEEP, anchor="mm")
im.convert("RGB").save(B / "concept_B.png")

sheet = Image.new("RGB", (1920, 540 * 2 + 20), (255, 255, 255))
for i, n in enumerate("AB"):
    sheet.paste(Image.open(B / f"concept_{n}.png").resize((960 * 2, 1080)).resize((960 * 2, 1080)).resize((1920, 1080)).resize((960, 540)), (0 if True else 0, i * 560))
side = Image.new("RGB", (1940, 540), "white")
side.paste(Image.open(B / "concept_A.png").resize((960, 540)), (0, 0)); side.paste(Image.open(B / "concept_B.png").resize((960, 540)), (980, 0))
side.save(B / "concepts.jpg", quality=88)
print("ok")
