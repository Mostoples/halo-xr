"""HALO-XR · QR kuesioner — python video/qr_card.py
Hasil: output/QR_Kuesioner_HALO-XR.png (QR polos) dan output/QR_Kuesioner_HALO-XR_kartu.png (kartu siap cetak/bagikan)."""
import pathlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "output"; OUT.mkdir(exist_ok=True)
F = lambda w, s: ImageFont.truetype(str(ROOT / f"video/fonts/PJS-{w}.ttf"), s)
INK, INK2, BLUE, DEEP, ICE = (22, 35, 63), (74, 90, 122), (47, 123, 255), (22, 70, 214), (221, 235, 255)
URL = "haloxr-id.web.app/kuesioner.html"
M = [[c == "1" for c in row] for row in (ROOT / "video/build/qr_matrix.txt").read_text().split()]
N = len(M)


def rr(size, box, r, fill=255):
    m = Image.new("L", size, 0); ImageDraw.Draw(m).rounded_rectangle(box, r, fill=fill); return m


def qr_image(px, logo=True):
    """QR dengan modul bulat-persegi, penanda sudut biru, dan logo di tengah (koreksi galat level H)."""
    quiet = 4; cell = px // (N + 2 * quiet); size = cell * (N + 2 * quiet)
    im = Image.new("RGBA", (size, size), (255, 255, 255, 255)); d = ImageDraw.Draw(im)
    finder = lambda r, c: (r < 7 and c < 7) or (r < 7 and c >= N - 7) or (r >= N - 7 and c < 7)
    for r in range(N):
        for c in range(N):
            if M[r][c] and not finder(r, c):
                x, y = (c + quiet) * cell, (r + quiet) * cell
                d.rounded_rectangle((x, y, x + cell, y + cell), cell * 0.2, fill=INK)
    # Penanda sudut biru tua penuh (biru muda di tengah membuat QR gagal dibaca — sudah diuji dengan OpenCV)
    for r0, c0 in ((0, 0), (0, N - 7), (N - 7, 0)):
        x, y = (c0 + quiet) * cell, (r0 + quiet) * cell
        d.rounded_rectangle((x, y, x + 7 * cell, y + 7 * cell), cell * 1.2, fill=DEEP)
        d.rounded_rectangle((x + cell, y + cell, x + 6 * cell, y + 6 * cell), cell * 0.8, fill="white")
        d.rounded_rectangle((x + 2 * cell, y + 2 * cell, x + 5 * cell, y + 5 * cell), cell * 0.6, fill=DEEP)
    if logo:
        L = int(N * cell * 0.15); lx = (size - L) // 2
        d.rounded_rectangle((lx - cell // 2, lx - cell // 2, lx + L + cell // 2, lx + L + cell // 2), cell, fill="white")
        ic = Image.open(ROOT / "assets/icon-512.png").convert("RGBA").resize((L, L), Image.LANCZOS)
        im.alpha_composite(ic, (lx, lx))
    return im


# 1) QR polos
qr_image(1200).convert("RGB").save(OUT / "QR_Kuesioner_HALO-XR.png")

# 2) Kartu 1080×1350 (rasio feed Instagram / cetak A5 potret)
W, H = 1080, 1350
y, x = np.mgrid[0:H, 0:W].astype(np.float32)
k = np.clip(np.sqrt(((x - W * .5) / W) ** 2 + ((y - H * .3) / H) ** 2) / .8, 0, 1)[..., None]
bg = np.array([246, 249, 253]) * (1 - k) + np.array([218, 227, 240]) * k
for cx, cy, r, s, col in ((.1, .08, .3, 45, (140, 198, 255)), (.92, .95, .35, 40, (110, 160, 255))):
    g = np.exp(-(((x / W - cx) ** 2 + (y / H - cy) ** 2) / (r * r)))[..., None] * s / 255
    bg = bg * (1 - g) + np.array(col) * g
im = Image.fromarray(bg.clip(0, 255).astype(np.uint8)).convert("RGBA"); d = ImageDraw.Draw(im)

ic = Image.open(ROOT / "assets/icon-512.png").convert("RGBA").resize((64, 64), Image.LANCZOS)
im.alpha_composite(ic, (80, 72)); d.text((160, 82), "HALO-XR", font=F("ExtraBold", 36), fill=INK)
chip = "± 1 MENIT · ANONIM"; cf = F("ExtraBold", 24); cw = d.textlength(chip, font=cf) + 48
d.rounded_rectangle((80, 186, 80 + cw, 236), 25, fill="white"); d.text((104, 197), chip, font=cf, fill=BLUE)
d.text((80, 262), "Isi kuesioner", font=F("ExtraBold", 76), fill=INK)
# baris kedua gradien biru
t2 = "anatomi 3D, yuk!"; f2 = F("ExtraBold", 76)
mask = Image.new("L", im.size, 0); ImageDraw.Draw(mask).text((80, 350), t2, font=f2, fill=255)
gx = np.clip((np.arange(W) - 80) / 620, 0, 1)[None, :, None]
grad = np.zeros((H, W, 4), np.uint8); grad[..., :3] = (np.array(BLUE) * (1 - gx) + np.array(DEEP) * gx).astype(np.uint8); grad[..., 3] = 255
im.paste(Image.fromarray(grad), (0, 0), mask)
d.text((82, 462), "5 pertanyaan ringan tentang cara kamu belajar anatomi.", font=F("Medium", 30), fill=INK2)

# kartu QR dengan aura biru
q = qr_image(1200).resize((560, 560), Image.LANCZOS); qs = q.width; bx, by = (W - qs - 60) // 2, 560
box = (bx, by, bx + qs + 60, by + qs + 60)
halo = rr(im.size, (box[0], box[1] + 18, box[2], box[3] + 18), 44).filter(ImageFilter.GaussianBlur(34))
lay = Image.new("RGBA", im.size, (60, 130, 255, 0)); lay.putalpha(halo.point(lambda v: int(v * .45))); im.alpha_composite(lay)
im.paste(Image.new("RGBA", im.size, (255, 255, 255, 255)), (0, 0), rr(im.size, box, 44))
im.alpha_composite(q, (bx + 30, by + 30))

d.text((W // 2, box[3] + 62), "Pindai dengan kamera HP", font=F("Bold", 30), fill=INK, anchor="mm")
d.text((W // 2, box[3] + 108), URL, font=F("Bold", 28), fill=DEEP, anchor="mm")
im.convert("RGB").save(OUT / "QR_Kuesioner_HALO-XR_kartu.png")
print("ok")
