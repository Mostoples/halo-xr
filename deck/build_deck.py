"""
HALO-XR pitch deck — desain ulang neumorphism putih-biru (gaya AQUENT) dari "HALO-XR Interactive Anatomy Hologram.pdf".
Lapisan visual (kartu, ponsel, orb, diagram) dirender PIL; semua teks native & bisa diedit di PowerPoint.
Aset diambil dari app lewat deck/shots.py.   Pakai: python deck/build_deck.py [en|id]
"""
import pathlib, hashlib, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from lxml import etree

LANG = sys.argv[1] if len(sys.argv) > 1 else "en"
ROOT = pathlib.Path(__file__).resolve().parent.parent
SCR = ROOT / "deck/build/screens"
MED = ROOT / "deck/build/media"
GEN = ROOT / "deck/build/gen"; GEN.mkdir(parents=True, exist_ok=True)
OUTD = ROOT / "output"; OUTD.mkdir(exist_ok=True)
OUT = OUTD / f"HALO-XR_Deck_Neumorph_{LANG.upper()}.pptx"

SW_IN, SH_IN = 13.333, 7.5
PX = 150
INK, INK2, MUTED = "16233F", "4A5A7A", "7A8AA8"
BLUE, DEEP, SKY, ICE = "2F7BFF", "1646D6", "8CC6FF", "DDEBFF"
OK, WARN = "13A06B", "E0703F"
CARD = (237, 242, 249)
FONT = "Segoe UI"
TOTAL = 12
FX_START = {}

# =============================================================== TEKS (ID/EN) ===
TEAM = "Afkar Gilang Prasetya · Aufa Bayu Nur Rahman · Kamajaya Willia Zabir · M. Azhar Rifky Zulkarnain · Tirta Manggala Nusantara · Toti Surya Samantha"
TEXT = {
 "en": {
  "cover": {"kick": "SOCIETY 5.0 · BIOLOGY EDUCATION", "t1": "HALO-XR", "t2": "Interactive Anatomy Hologram",
            "sub": "A low-cost, touchless pseudo-hologram system designed for collaborative secondary-school anatomy education.",
            "team": "THE TEAM", "year": "Academic Year 2026/2027", "pills": ["Pepper's Ghost", "9 touchless gestures", "10 3D models"]},
  "s2": {"chip": "01 · PROBLEM", "t": [("Anatomy is 3D. ", INK), ("Classrooms are still flat.", BLUE)],
         "sub": "Today's immersive alternatives price out ordinary classrooms and isolate learners.",
         "cards": [("Cognitive gap", "Spatial ability is crucial for anatomy, yet schools rely on flat, static textbooks."),
                   ("The VR barrier", "Virtual reality improves spatial knowledge but isolates single users and can cause dizziness."),
                   ("Cost prohibitive", "Entry-level VR hardware is a barrier to the fair distribution of digital innovation.")],
         "big": "USD 349.99", "bigk": "COST DISPARITY", "bigd": "One entry-level Meta Quest 3S. Unrealistic for 1:1 student deployment in Indonesia."},
  "s3": {"chip": "02 · THE GAP", "t": [("Bridging accessibility ", INK), ("and immersion.", BLUE)],
         "sub": "HALO-XR combines the group-friendly affordability of conventional media with the interactive 3D benefits of VR.",
         "cols": ["Criterion", "Textbooks", "VR headsets", "HALO-XR"],
         "rows": [("3D view from many directions", "No", "Yes", "Yes · four sides"), ("Viewing by a group", "Yes", "One user only", "Yes · small group"),
                  ("Interactive exploration", "No", "Yes", "Yes · touchless"), ("Cost barrier", "Low", "High ($350+)", "Ultra-low")]},
  "s4": {"chip": "03 · SOLUTION", "t": [("A touchless ", INK), ("cyber-physical ecosystem.", BLUE)],
         "sub": "A Pepper's Ghost pyramid plus low-cost infrared sensing gives headset-free extended reality.",
         "units": [("Gesture control unit", "PAJ7620U2 sensor + ESP32 tracks 9 touchless hand movements and streams them over Bluetooth LE."),
                   ("Display unit", "A web app on any tablet maps gestures to actions (rotate, zoom, peel) across 4 synchronised views."),
                   ("Optical unit", "A 45° acrylic pyramid reflects the screen so the 3D anatomy appears to float in mid-air.")]},
  "s5": {"chip": "04 · HOW IT FORMS", "t": [("Four views, ", INK), ("one floating organ.", BLUE)],
         "sub": "The tablet renders front, right, back and left cameras. Each face of the pyramid reflects one of them to the viewer on that side.",
         "labels": ["BACK", "RIGHT", "FRONT", "LEFT"],
         "pts": [("Top of the organ points outward", "so every reflection appears upright"), ("Mirrored per view", "so labels read correctly after reflection"),
                 ("Calibrated in the app", "view size, gap from centre, guide lines")]},
  "s6": {"chip": "05 · METHOD", "t": [("Systematic R&D ", INK), ("driven by ADDIE.", BLUE)],
         "sub": "Strict alignment with educational needs, precise optical physics and robust technical deployment.",
         "steps": [("Analysis", "Mapped biology curriculum needs and set a strict < 150 ms interaction-latency requirement.", "done"),
                   ("Design", "Calculated the exact pyramid geometry for horizontal light reflection (Snell's law, Fresnel equations).", "done"),
                   ("Development", "Fabricated parts, event-driven ESP32 firmware and optimised 3D models for mobile rendering.", "done"),
                   ("Implementation", "Classroom trials in partner schools with small learning groups.", "next"),
                   ("Evaluation", "Technical benchmark, expert validation, SUS and pre/post-test N-gain.", "next")],
         "done": "DONE", "next": "NEXT", "diag": ["Observer", "Tablet screen", "Source light", "Virtual image"],
         "optic": "Each acrylic face sits at exactly 45° (7.78 cm slant), so light from the screen turns horizontally to eye level and the virtual image appears inside the pyramid."},
  "s7": {"chip": "06 · PERFORMANCE", "t": [("High-fidelity interaction ", INK), ("at a fraction of the cost.", BLUE)],
         "sub": "Near-instant touchless interaction while staying radically affordable.",
         "k1": "Rp 265,000", "k1l": "Total hardware cost", "k1d": "Excluding the existing tablet. Less than 1/10 of the price of VR.",
         "k2": "108.3 ms", "k2l": "Estimated latency", "k2d": "Target ≤ 150 ms, so the response is perceived as immediate.",
         "note": "Optical note", "noted": "Unpolarised light reflects only ~5% off acrylic. A black background, a dim room and maximum screen brightness maximise contrast."},
  "s8": {"chip": "07 · THE APP", "t": [("One web app, ", INK), ("ten 3D models.", BLUE)],
         "sub": "Native HTML, CSS & JS that runs on any tablet and works offline as a PWA.",
         "caps": ["Library", "Hologram style", "Peel section", "Layered cell"],
         "pills": ["9 textured 3D organs", "Realistic / hologram shader", "Section peel by gesture", "Labelled structures", "ID / EN", "Web Bluetooth"],
         "credit": "3D organ models & content adapted from github.com/thebuggeddev/anatomy"},
  "s9": {"chip": "08 · IMPACT", "t": [("Advancing Society 5.0 ", INK), ("and the SDGs.", BLUE)],
         "sub": "Technology must be accessible, inclusive and designed around real human well-being.",
         "cards": [("Fair technological distribution", "A highly reproducible open design brings 3D education to resource-limited schools."),
                   ("Human-centred hygiene", "Touchless infrared control lets many students share one device without contact or wear."),
                   ("Sustainable infrastructure", "Reuses existing school tablets and runs at very low power.")],
         "sdg": ["SDG 4 · Quality education", "SDG 9 · Innovation", "SDG 10 · Reduced inequalities"]},
  "s10": {"chip": "09 · VALIDATION", "t": [("Rigorous verification ", INK), ("and classroom integration.", BLUE)],
          "sub": "Technical benchmarking first, then a quasi-experimental classroom evaluation.",
          "steps": [("Technical verification", "Gesture accuracy ≥ 90%, rendering ≥ 30 fps, visibility under varied classroom light."),
                    ("Expert & usability validation", "Biology-teacher review for anatomical accuracy; System Usability Scale target ≥ 70."),
                    ("Learning outcomes", "Pre/post-test normalised gain (N-gain) compared against conventional media.")],
          "phone": "N-gain is calculated in the app's Class tab", "sample": "Sample values shown"},
  "s11": {"chip": "10 · CONCLUSION", "t1": "Transforming classrooms", "t2": "into cyber-physical spaces.",
          "sub": "HALO-XR shows that interactive, touchless 3D anatomy can be delivered through radically affordable, accessible technology.",
          "cards": [("Resolves passivity", "Replaces looping videos with active 9-gesture manipulation."),
                    ("Removes VR barriers", "Avoids the $350 cost and the dizziness of headsets."),
                    ("Empowers schools", "A reproducible blueprint for building Society 5.0 learning tools.")]},
  "s12": {"chip": "11 · ACKNOWLEDGEMENTS", "t": [("Open collaboration ", INK), ("drives innovation.", BLUE)],
          "inst": "Research institutions", "insts": ["SMA Muhammadiyah PK Kottabarat Surakarta", "Madrasah Aliyah Negeri 1 Surakarta", "SMA Negeri 4 Surakarta"],
          "status": "Project status", "statusd": "Open for technical validation and classroom integration partnerships.",
          "contact": "Contact the research team", "thanks": "Thank you."},
 },
 "id": {
  "cover": {"kick": "SOCIETY 5.0 · PENDIDIKAN BIOLOGI", "t1": "HALO-XR", "t2": "Hologram Anatomi Interaktif",
            "sub": "Sistem pseudo-hologram tanpa sentuh berbiaya rendah untuk pembelajaran anatomi kolaboratif di sekolah menengah.",
            "team": "TIM", "year": "Tahun Ajaran 2026/2027", "pills": ["Pepper's Ghost", "9 gestur tanpa sentuh", "10 model 3D"]},
  "s2": {"chip": "01 · MASALAH", "t": [("Anatomi itu 3D. ", INK), ("Kelas masih datar.", BLUE)],
         "sub": "Alternatif imersif saat ini terlalu mahal untuk kelas biasa dan membuat siswa belajar sendiri-sendiri.",
         "cards": [("Kesenjangan kognitif", "Kemampuan spasial penting untuk anatomi, tetapi sekolah masih bergantung pada buku teks yang datar dan statis."),
                   ("Hambatan VR", "Realitas virtual meningkatkan pemahaman spasial, tetapi hanya untuk satu pengguna dan bisa memicu pusing."),
                   ("Biaya tinggi", "Perangkat VR kelas pemula menjadi penghalang pemerataan inovasi digital.")],
         "big": "USD 349,99", "bigk": "KESENJANGAN BIAYA", "bigd": "Harga satu Meta Quest 3S kelas pemula. Tidak realistis untuk satu siswa satu perangkat di Indonesia."},
  "s3": {"chip": "02 · CELAH", "t": [("Menjembatani keterjangkauan ", INK), ("dan imersi.", BLUE)],
         "sub": "HALO-XR menggabungkan keterjangkauan media konvensional yang ramah kelompok dengan manfaat 3D interaktif dari VR.",
         "cols": ["Kriteria", "Buku teks", "Headset VR", "HALO-XR"],
         "rows": [("Tampilan 3D dari banyak arah", "Tidak", "Ya", "Ya · empat sisi"), ("Ditonton kelompok", "Ya", "Satu orang", "Ya · kelompok kecil"),
                  ("Eksplorasi interaktif", "Tidak", "Ya", "Ya · tanpa sentuh"), ("Hambatan biaya", "Rendah", "Tinggi ($350+)", "Sangat rendah")]},
  "s4": {"chip": "03 · SOLUSI", "t": [("Ekosistem siber-fisik ", INK), ("tanpa sentuh.", BLUE)],
         "sub": "Piramida Pepper's Ghost dan sensor inframerah murah menghadirkan extended reality tanpa headset.",
         "units": [("Unit kontrol gestur", "Sensor PAJ7620U2 + ESP32 membaca 9 gerakan tangan tanpa sentuh dan mengirimnya lewat Bluetooth LE."),
                   ("Unit tampilan", "Aplikasi web di tablet apa pun memetakan gestur ke aksi (putar, zoom, kupas) pada 4 tampilan sinkron."),
                   ("Unit optik", "Piramida akrilik 45° memantulkan layar sehingga anatomi 3D tampak melayang di udara.")]},
  "s5": {"chip": "04 · CARA TERBENTUK", "t": [("Empat tampilan, ", INK), ("satu organ melayang.", BLUE)],
         "sub": "Tablet merender kamera depan, kanan, belakang, dan kiri. Tiap sisi piramida memantulkan satu tampilan ke penonton di sisi itu.",
         "labels": ["BELAKANG", "KANAN", "DEPAN", "KIRI"],
         "pts": [("Bagian atas organ menghadap keluar", "agar setiap pantulan tampak tegak"), ("Dicerminkan per tampilan", "agar label terbaca benar setelah dipantulkan"),
                 ("Dikalibrasi di aplikasi", "ukuran tampilan, jarak dari pusat, garis bantu")]},
  "s6": {"chip": "04 · METODE", "t": [("R&D sistematis ", INK), ("dengan model ADDIE.", BLUE)],
         "sub": "Selaras dengan kebutuhan pendidikan, fisika optik yang presisi, dan implementasi teknis yang andal.",
         "steps": [("Analisis", "Memetakan kebutuhan kurikulum biologi dan menetapkan syarat latensi interaksi < 150 ms.", "done"),
                   ("Desain", "Menghitung geometri piramida untuk pantulan cahaya horizontal (hukum Snellius, persamaan Fresnel).", "done"),
                   ("Pengembangan", "Fabrikasi komponen, firmware ESP32 berbasis event, dan model 3D teroptimasi untuk perangkat mobile.", "done"),
                   ("Implementasi", "Uji coba di kelas sekolah mitra dengan kelompok belajar kecil.", "next"),
                   ("Evaluasi", "Benchmark teknis, validasi ahli, SUS, dan N-gain pre/post-test.", "next")],
         "done": "SELESAI", "next": "BERIKUTNYA", "diag": ["Pengamat", "Layar tablet", "Sumber cahaya", "Bayangan maya"],
         "optic": "Setiap sisi akrilik tepat 45° (sisi miring 7,78 cm), sehingga cahaya dari layar berbelok horizontal setinggi mata dan bayangan maya tampak di dalam piramida."},
  "s7": {"chip": "06 · KINERJA", "t": [("Interaksi presisi tinggi ", INK), ("dengan biaya sangat kecil.", BLUE)],
         "sub": "Interaksi tanpa sentuh yang nyaris instan sekaligus sangat terjangkau.",
         "k1": "Rp 265.000", "k1l": "Total biaya perangkat", "k1d": "Belum termasuk tablet yang sudah ada. Kurang dari 1/10 harga VR.",
         "k2": "108,3 ms", "k2l": "Estimasi latensi", "k2d": "Target ≤ 150 ms agar respons terasa seketika.",
         "note": "Catatan optik", "noted": "Akrilik hanya memantulkan ±5% cahaya tak terpolarisasi. Latar hitam, ruangan redup, dan kecerahan layar maksimum memaksimalkan kontras."},
  "s8": {"chip": "07 · APLIKASI", "t": [("Satu aplikasi web, ", INK), ("sepuluh model 3D.", BLUE)],
         "sub": "HTML, CSS, dan JS native. Berjalan di tablet apa pun dan bisa offline sebagai PWA.",
         "caps": ["Pustaka", "Gaya hologram", "Kupas irisan", "Sel berlapis"],
         "pills": ["9 organ 3D bertekstur", "Shader realistis / hologram", "Kupas irisan dengan gestur", "Struktur berlabel", "ID / EN", "Web Bluetooth"],
         "credit": "Model 3D & materi organ diadaptasi dari github.com/thebuggeddev/anatomy"},
  "s9": {"chip": "08 · DAMPAK", "t": [("Mendukung Society 5.0 ", INK), ("dan SDGs.", BLUE)],
         "sub": "Teknologi harus mudah diakses, inklusif, dan dirancang untuk kesejahteraan manusia.",
         "cards": [("Pemerataan teknologi", "Desain terbuka yang mudah direplikasi membawa pembelajaran 3D ke sekolah dengan sumber daya terbatas."),
                   ("Higienis & berpusat pada manusia", "Kontrol inframerah tanpa sentuh memungkinkan banyak siswa berbagi satu perangkat tanpa kontak."),
                   ("Infrastruktur berkelanjutan", "Memanfaatkan tablet sekolah yang sudah ada dan hemat daya.")],
         "sdg": ["SDG 4 · Pendidikan berkualitas", "SDG 9 · Inovasi", "SDG 10 · Berkurangnya kesenjangan"]},
  "s10": {"chip": "09 · VALIDASI", "t": [("Verifikasi ketat ", INK), ("dan integrasi kelas.", BLUE)],
          "sub": "Benchmark teknis lebih dulu, lalu evaluasi kelas kuasi-eksperimen.",
          "steps": [("Verifikasi teknis", "Akurasi gestur ≥ 90%, rendering ≥ 30 fps, visibilitas pada berbagai pencahayaan kelas."),
                    ("Validasi ahli & usabilitas", "Telaah guru biologi untuk akurasi anatomi; target System Usability Scale ≥ 70."),
                    ("Hasil belajar", "Normalized gain (N-gain) pre/post-test dibandingkan dengan media konvensional.")],
          "phone": "N-gain dihitung di tab Kelas aplikasi", "sample": "Contoh nilai tampilan"},
  "s11": {"chip": "10 · KESIMPULAN", "t1": "Mengubah ruang kelas", "t2": "menjadi ruang siber-fisik.",
          "sub": "HALO-XR membuktikan anatomi 3D interaktif tanpa sentuh bisa dihadirkan dengan teknologi yang sangat terjangkau dan mudah diakses.",
          "cards": [("Mengatasi kepasifan", "Mengganti video berulang dengan manipulasi aktif lewat 9 gestur."),
                    ("Menghapus hambatan VR", "Tanpa biaya $350 dan tanpa pusing akibat headset."),
                    ("Memberdayakan sekolah", "Cetak biru yang bisa direplikasi untuk alat belajar Society 5.0.")]},
  "s12": {"chip": "11 · UCAPAN TERIMA KASIH", "t": [("Kolaborasi terbuka ", INK), ("mendorong inovasi.", BLUE)],
          "inst": "Institusi riset", "insts": ["SMA Muhammadiyah PK Kottabarat Surakarta", "Madrasah Aliyah Negeri 1 Surakarta", "SMA Negeri 4 Surakarta"],
          "status": "Status proyek", "statusd": "Terbuka untuk kemitraan validasi teknis dan integrasi di kelas.",
          "contact": "Hubungi tim peneliti", "thanks": "Terima kasih."},
 },
}
L = TEXT[LANG]
# urutan slide: s5 (cara terbentuk) memakai nomor bab 04, metode jadi 05
L["s6"]["chip"] = L["s6"]["chip"].replace("04", "05")


def rgb(h): return RGBColor.from_string(h)
def cache(name, key): return GEN / f"{name}_{hashlib.md5(repr(key).encode()).hexdigest()[:10]}.png"


# ================================================================ art gen ===
def bg_light():
    p = GEN / "bg_light.png"
    if p.exists(): return p
    W, H = int(SW_IN * 120), int(SH_IN * 120)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((x - W * 0.55) / W) ** 2 + ((y - H * 0.35) / H) ** 2)
    k = np.clip(d / 0.8, 0, 1)[..., None]
    img = np.array([246, 249, 253]) * (1 - k) + np.array([218, 227, 240]) * k
    for cx, cy, r, s, col in ((0.05, 0.1, 0.3, 26, (140, 198, 255)), (0.95, 0.95, 0.35, 24, (130, 170, 255))):
        g = np.exp(-(((x / W - cx) ** 2 + (y / H - cy) ** 2) / (r * r)))[..., None] * s / 255
        img = img * (1 - g) + np.array(col) * g
    Image.fromarray(img.clip(0, 255).astype(np.uint8)).save(p)
    return p


def bg_brand():
    p = GEN / "bg_brand.png"
    if p.exists(): return p
    W, H = int(SW_IN * 120), int(SH_IN * 120)
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    t = np.clip((x / W) * 0.7 + (y / H) * 0.3, 0, 1)[..., None]
    img = np.array([47, 123, 255]) * (1 - t) + np.array([22, 70, 214]) * t
    for cx, cy, r, s in ((0.2, 0.15, 0.35, 60), (0.85, 0.9, 0.4, 40)):
        g = np.exp(-(((x / W - cx) ** 2 + (y / H - cy) ** 2) / (r * r)))[..., None] * s / 255
        img = img * (1 - g) + 255 * g
    Image.fromarray(img.clip(0, 255).astype(np.uint8)).save(p)
    return p


def _rr(size, box, r, fill=255):
    m = Image.new("L", size, 0)
    ImageDraw.Draw(m).rounded_rectangle(box, r, fill=fill)
    return m


M_IN = 0.34


def card_img(w, h, r=0.26, kind="raise", fill=CARD, dist=0.09, blur=0.13):
    p = cache("card", (w, h, r, kind, fill, dist, blur))
    if p.exists(): return p
    m = int(M_IN * PX)
    W, H = int(w * PX) + 2 * m, int(h * PX) + 2 * m
    box = (m, m, m + int(w * PX), m + int(h * PX))
    R, D, B = int(r * PX), int(dist * PX), int(blur * PX)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    def layer(mask, color, alpha):
        lay = Image.new("RGBA", (W, H), color + (0,))
        lay.putalpha(Image.fromarray((np.array(mask).astype(np.float32) * alpha).astype(np.uint8)))
        im.alpha_composite(lay)
    if kind == "raise":
        dk = _rr((W, H), (box[0] + D // 2, box[1] + D, box[2] + D // 2, box[3] + D), R).filter(ImageFilter.GaussianBlur(B * 1.3))
        layer(dk, (92, 140, 255), 0.30)
        lt = _rr((W, H), (box[0] - D, box[1] - D, box[2] - D, box[3] - D), R).filter(ImageFilter.GaussianBlur(B))
        layer(lt, (255, 255, 255), 1.0)
        ga = np.zeros((H, W, 4), np.uint8)
        t = np.linspace(0, 1, H)[:, None, None]
        ga[..., :3] = (np.array([246, 249, 254]) * (1 - t) + np.array(fill) * t).astype(np.uint8)
        ga[..., 3] = 255
        im.paste(Image.fromarray(ga), (0, 0), _rr((W, H), box, R))
    else:
        halo = _rr((W, H), box, R).filter(ImageFilter.GaussianBlur(B * 1.1))
        layer(halo, (70, 150, 255), 0.55)
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        cx, cy = box[0] + (box[2] - box[0]) * 0.35, box[1] + (box[3] - box[1]) * 0.28
        dd = np.sqrt(((xx - cx) / (box[2] - box[0])) ** 2 + ((yy - cy) / (box[3] - box[1])) ** 2)
        k = np.clip(dd / 0.95, 0, 1)[..., None]
        ga = np.zeros((H, W, 4), np.uint8)
        ga[..., :3] = (np.array([255, 255, 255]) * (1 - k) + np.array([214, 230, 255]) * k).astype(np.uint8)
        ga[..., 3] = 255
        im.paste(Image.fromarray(ga), (0, 0), _rr((W, H), box, R))
        rim = Image.new("L", (W, H), 0)
        ImageDraw.Draw(rim).rounded_rectangle(box, R, outline=255, width=max(2, int(PX * 0.012)))
        layer(rim, (255, 255, 255), 0.9)
    im.save(p)
    return p


def phone_img(screen_name, crop_h=None):
    """Mockup ponsel (rangka terang, bezel hitam, dynamic island) di sekitar screenshot app."""
    p = cache("phone", (screen_name, crop_h, 4))
    if p.exists(): return p
    scr = Image.open(SCR / f"{screen_name}.png").convert("RGBA")
    if crop_h: scr = scr.crop((0, 0, scr.width, int(scr.width * crop_h)))
    k = 585 / scr.width
    sw, sh = int(scr.width * k), int(scr.height * k)
    scr = scr.resize((sw, sh), Image.LANCZOS)
    bz, rad = int(sw * 12 / 404), int(sw * 54 / 404)
    pw, ph = sw + 2 * bz, sh + 2 * bz
    m = int(pw * 0.16)
    W, H = pw + 2 * m, ph + 2 * m
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    body = (m, m, m + pw, m + ph)
    R = rad + bz
    dk = _rr((W, H), (m + 14, m + 34, m + pw + 14, m + ph + 34), R, 120).filter(ImageFilter.GaussianBlur(46))
    im.paste(Image.new("RGBA", (W, H), (70, 120, 235, 255)), (0, 0), dk)
    ga = np.zeros((H, W, 4), np.uint8)
    t = np.linspace(0, 1, H)[:, None, None]
    ga[..., :3] = (np.array([252, 253, 255]) * (1 - t) + np.array([204, 214, 230]) * t).astype(np.uint8)
    ga[..., 3] = 255
    im.paste(Image.fromarray(ga), (0, 0), _rr((W, H), body, R))
    im.paste(Image.new("RGBA", (W, H), (10, 14, 24, 255)), (0, 0), _rr((W, H), (m + 5, m + 5, m + pw - 5, m + ph - 5), R - 5))
    scr.putalpha(_rr((sw, sh), (0, 0, sw - 1, sh - 1), rad))
    im.alpha_composite(scr, (m + bz, m + bz))
    ImageDraw.Draw(im).rounded_rectangle((W // 2 - int(sw * 0.15), m + bz + int(sw * 0.028), W // 2 + int(sw * 0.15),
                                          m + bz + int(sw * 0.11)), int(sw * 0.042), fill=(5, 7, 12, 255))
    im.save(p)
    return p


def phone_size(screen_name, w, crop_h=None):
    """Lebar gambar mockup (inci) → (w_total, h_total, offset) supaya layar selebar w."""
    im = Image.open(phone_img(screen_name, crop_h))
    tw = w * im.width / 585  # lebar total relatif lebar layar 585 px
    return tw, tw * im.height / im.width, (tw - w) / 2


def photo_aura(path, w, h, r=0.24, fit="cover"):
    p = cache("paura", (str(path), w, h, r, fit, 3))
    if p.exists(): return p
    src = Image.open(path).convert("RGBA")
    W, H, m = int(w * PX), int(h * PX), int(M_IN * PX)
    s_ = max(W / src.width, H / src.height)
    src = src.resize((int(src.width * s_) + 1, int(src.height * s_) + 1), Image.LANCZOS)
    l, t = (src.width - W) // 2, (src.height - H) // 2
    src = src.crop((l, t, l + W, t + H))
    R = int(r * PX)
    out = Image.new("RGBA", (W + 2 * m, H + 2 * m), (0, 0, 0, 0))
    box = (m, m, m + W, m + H)
    halo = _rr(out.size, (box[0] - 4, box[1] + 6, box[2] + 4, box[3] + 10), R).filter(ImageFilter.GaussianBlur(int(0.16 * PX)))
    lay = Image.new("RGBA", out.size, (60, 140, 255, 0))
    lay.putalpha(Image.fromarray((np.array(halo) * 0.62).astype(np.uint8)))
    out.alpha_composite(lay)
    out.paste(Image.new("RGBA", out.size, (255, 255, 255, 235)), (0, 0), _rr(out.size, (box[0] - 5, box[1] - 5, box[2] + 5, box[3] + 5), R + 5))
    src.putalpha(_rr((W, H), (0, 0, W - 1, H - 1), R))
    out.alpha_composite(src, (m, m))
    out.save(p)
    return p


def orb_img(color=(70, 150, 255)):
    p = cache("orb", color)
    if p.exists(): return p
    N = 600
    y, x = np.mgrid[0:N, 0:N].astype(np.float32)
    d = np.sqrt((x - N / 2) ** 2 + (y - N / 2) ** 2) / (N / 2)
    im = np.zeros((N, N, 4), np.uint8)
    im[..., :3] = color
    im[..., 3] = (np.clip(1 - d, 0, 1) ** 2.2 * 190).astype(np.uint8)
    Image.fromarray(im).save(p)
    return p


def trim(path):
    """Potong area transparan cut-out organ."""
    p = cache("trim", str(path))
    if p.exists(): return p
    im = Image.open(path).convert("RGBA")
    bb = im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
    im.crop(bb).save(p)
    return p


def center_crop(path, fw, fh):
    """Potong bagian tengah gambar (fw, fh = pecahan lebar/tinggi)."""
    p = cache("cc", (str(path), fw, fh))
    if p.exists(): return p
    im = Image.open(path); W, H = im.size; w, h = int(W * fw), int(H * fh)
    im.crop(((W - w) // 2, (H - h) // 2, (W + w) // 2, (H + h) // 2)).save(p)
    return p


def optic_diagram():
    """Penampang optik: layar tablet, piramida 45°, sinar ke pengamat, bayangan maya."""
    p = GEN / "optic.png"
    if p.exists(): return p
    W, H = int(5.6 * PX), int(3.0 * PX)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    base_y, cx, half = int(H * 0.84), W // 2, int(W * 0.25)
    d.rounded_rectangle((int(W * 0.12), base_y, int(W * 0.88), base_y + 18), 9, fill=(22, 35, 63, 255))
    d.rounded_rectangle((int(W * 0.18), base_y + 4, int(W * 0.82), base_y + 10), 3, fill=(47, 123, 255, 255))
    top = base_y - half
    poly = [(cx, base_y - 2), (cx + half, top), (cx - half, top)]
    glass = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(glass).polygon(poly, fill=(140, 198, 255, 70))
    im.alpha_composite(glass)
    d.line(poly + [poly[0]], fill=(47, 123, 255, 255), width=5, joint="curve")
    sx = cx + int(half * 0.45)
    hit = (sx, base_y - (sx - cx))
    for a, b in [((sx, base_y), hit), (hit, (W - 30, hit[1]))]:
        n = 14
        for i in range(n):
            if i % 2: continue
            t0, t1 = i / n, (i + 1) / n
            d.line([(a[0] + (b[0] - a[0]) * t0, a[1] + (b[1] - a[1]) * t0), (a[0] + (b[0] - a[0]) * t1, a[1] + (b[1] - a[1]) * t1)], fill=(245, 165, 36, 255), width=5)
    d.polygon([(W - 30, hit[1]), (W - 52, hit[1] - 10), (W - 52, hit[1] + 10)], fill=(245, 165, 36, 255))
    vy = hit[1]
    ghost = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(ghost).ellipse((cx - 30, vy - 30, cx + 30, vy + 30), fill=(47, 123, 255, 150))
    im.alpha_composite(ghost.filter(ImageFilter.GaussianBlur(6)))
    d.ellipse((cx - 16, vy - 16, cx + 16, vy + 16), fill=(47, 123, 255, 255))
    d.arc((cx + half - 60, top - 60, cx + half + 60, top + 60), 135, 180, fill=(74, 90, 122, 255), width=3)
    im.save(p)
    return p


# ============================================================ pptx utils ===
prs = Presentation()
prs.slide_width, prs.slide_height = Inches(SW_IN), Inches(SH_IN)
BLANK = prs.slide_layouts[6]


def pic(slide, path, x, y, w=None, h=None):
    kw = {}
    if w is not None: kw["width"] = Inches(w)
    if h is not None: kw["height"] = Inches(h)
    return slide.shapes.add_picture(str(path), Inches(x), Inches(y), **kw)


def card(slide, x, y, w, h, r=0.26, kind="raise", **kw):
    return pic(slide, card_img(w, h, r, kind, **kw), x - M_IN, y - M_IN, w + 2 * M_IN, h + 2 * M_IN)


def text(slide, x, y, w, h, content, size=14, color=INK2, bold=False, font=FONT, align="l", anchor="t",
         spacing=None, space_after=0, charsp=None):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame; tf.word_wrap = True
    for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"): setattr(tf, side, 0)
    tf.vertical_anchor = {"t": MSO_ANCHOR.TOP, "m": MSO_ANCHOR.MIDDLE, "b": MSO_ANCHOR.BOTTOM}[anchor]
    paras = content if isinstance(content, list) else [content]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = {"l": PP_ALIGN.LEFT, "c": PP_ALIGN.CENTER, "r": PP_ALIGN.RIGHT}[align]
        if spacing: p.line_spacing = spacing
        if space_after: p.space_after = Pt(space_after)
        runs = para if isinstance(para, list) else [(para, {})] if isinstance(para, str) else [para]
        for run in runs:
            t, o = (run, {}) if isinstance(run, str) else run
            r = p.add_run(); r.text = t; f = r.font
            f.name = o.get("font", font); f.size = Pt(o.get("size", size)); f.bold = o.get("bold", bold)
            f.color.rgb = rgb(o.get("color", color))
            cs = o.get("charsp", charsp)
            if cs: r._r.get_or_add_rPr().set("spc", str(cs))
    return tb


def glow(shape, color=BLUE, rad_pt=7, alpha=38):
    spPr = shape._element.spPr
    eff = spPr.find(qn("a:effectLst"))
    if eff is None:
        eff = spPr.makeelement(qn("a:effectLst"), {}); spPr.append(eff)
    g = eff.makeelement(qn("a:glow"), {"rad": str(int(rad_pt * 12700))})
    c = g.makeelement(qn("a:srgbClr"), {"val": color})
    c.append(c.makeelement(qn("a:alpha"), {"val": str(alpha * 1000)}))
    g.append(c); eff.insert(0, g)


def aura_orb(slide, cx, cy, d, color=(70, 150, 255)):
    sh = pic(slide, orb_img(color), cx - d / 2, cy - d / 2, d, d); sh.name = "FX_PULSE orb"; return sh


def photo(slide, path, x, y, w, h, r=0.24):
    return pic(slide, photo_aura(path, w, h, r), x - M_IN, y - M_IN, w + 2 * M_IN, h + 2 * M_IN)


def phone(slide, name, x, y, w, crop_h=None, float_=False):
    tw, th, off = phone_size(name, w, crop_h)
    sh = pic(slide, phone_img(name, crop_h), x - off, y - off * 0.9, tw)
    if float_: sh.name = "FX_FLOAT phone"
    return sh


def organ(slide, name, x, y, h, orb=True):
    p = trim(MED / f"{name}.png")
    im = Image.open(p); w = h * im.width / im.height
    if orb: aura_orb(slide, x + w / 2, y + h / 2, h * 1.35)
    sh = pic(slide, p, x, y, w, h); sh.name = "FX_FLOAT organ"
    return w


def chip(slide, x, y, label, fill=ICE, color=DEEP, size=9.5, glow_=True):
    w = 0.4 + len(label) * 0.098 * size / 9.5
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(0.3))
    s.adjustments[0] = 0.5; s.fill.solid(); s.fill.fore_color.rgb = rgb(fill); s.line.fill.background(); s.shadow.inherit = False
    tf = s.text_frame
    for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"): setattr(tf, side, 0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = label
    r.font.size, r.font.bold, r.font.name = Pt(size), True, FONT
    r.font.color.rgb = rgb(color); r._r.get_or_add_rPr().set("spc", "120")
    if glow_: glow(s, BLUE, 5, 22)
    return w


def badge(slide, x, y, d, label, fill=BLUE, size=12):
    s = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
    s.fill.solid(); s.fill.fore_color.rgb = rgb(fill); s.line.fill.background(); s.shadow.inherit = False
    tf = s.text_frame
    for side in ("margin_left", "margin_right", "margin_top", "margin_bottom"): setattr(tf, side, 0)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER
    r = p.add_run(); r.text = label
    r.font.size, r.font.bold, r.font.name = Pt(size), True, FONT
    r.font.color.rgb = rgb("FFFFFF")
    glow(s, fill, 8, 45)


def arrow(slide, x, y, w=0.34, h=0.3, color=BLUE):
    s = slide.shapes.add_shape(MSO_SHAPE.CHEVRON, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid(); s.fill.fore_color.rgb = rgb(color); s.line.fill.background(); s.shadow.inherit = False
    glow(s, color, 6, 40)


def logo(slide, x, y, dark=False):
    pic(slide, ROOT / "assets/icon-512.png", x, y, 0.42)
    text(slide, x + 0.52, y + 0.02, 1.4, 0.4, [[("HALO-XR", {"bold": True, "size": 14, "color": "FFFFFF" if dark else INK})]], anchor="m")


def new_slide(section, title=None, sub=None, bg="light"):
    s = prs.slides.add_slide(BLANK)
    pic(s, bg_light() if bg == "light" else bg_brand(), 0, 0, SW_IN, SH_IN)
    if section: chip(s, 0.6, 0.45, section)
    if title: text(s, 0.6, 0.86, 10.4, 0.7, [[(t, {"color": c}) for t, c in title]], size=31, bold=True)
    if sub: text(s, 0.6, 1.5, 10.0, 0.45, sub, size=13.5, color=INK2)
    logo(s, SW_IN - 0.6 - 1.55, 0.42, dark=bg != "light")
    text(s, SW_IN - 1.4, SH_IN - 0.42, 0.8, 0.25, f"{len(prs.slides):02d} / {TOTAL}", size=9, color=MUTED if bg == "light" else "DDEBFF", align="r")
    FX_START[s.slide_id] = len(s.shapes)
    return s


def notes(slide, t): slide.notes_slide.notes_text_frame.text = t


# ================================================================= SLIDES ===
# 1 · Cover
C = L["cover"]
s = prs.slides.add_slide(BLANK)
pic(s, bg_light(), 0, 0, SW_IN, SH_IN)
FX_START[s.slide_id] = 1
logo(s, 0.6, 0.5)
chip(s, 0.6, 1.35, C["kick"])
text(s, 0.6, 1.8, 7.2, 1.0, C["t1"], size=60, bold=True, color=INK)
text(s, 0.6, 2.75, 7.4, 0.7, C["t2"], size=30, bold=True, color=BLUE)
text(s, 0.6, 3.5, 6.6, 0.8, C["sub"], size=14.5, color=INK2, spacing=1.1)
x = 0.6
for pl in C["pills"]:
    x += chip(s, x, 4.45, pl, fill="FFFFFF", color=DEEP, size=10) + 0.15
card(s, 0.6, 5.1, 6.9, 1.75, 0.24)
text(s, 0.85, 5.28, 3.0, 0.3, C["team"], size=10, bold=True, color=BLUE, charsp=150)
text(s, 0.85, 5.58, 4.5, 1.0, TEAM, size=11, color=INK2, spacing=1.1)
text(s, 0.85, 6.45, 4.0, 0.3, C["year"], size=10.5, bold=True, color=INK)
pic(s, MED / "logos.png", 5.45, 5.55, 1.85)
aura_orb(s, 10.3, 3.4, 6.4)
organ(s, "heart_real", 9.0, 0.9, 4.9, orb=False)
photo(s, center_crop(MED / "pyramid_heart_real.png", 0.56, 0.84), 7.75, 4.7, 2.75, 2.15, 0.24).name = "FX_FLOAT pyr"
notes(s, "HALO-XR: hologram anatomi interaktif berbiaya rendah dan tanpa sentuh untuk pembelajaran kolaboratif.")

# 2 · Problem
D = L["s2"]
s = new_slide(D["chip"], D["t"], D["sub"])
for i, (h, b) in enumerate(D["cards"]):
    y = 2.35 + i * 1.5
    card(s, 0.6, y, 6.3, 1.22, 0.24)
    badge(s, 0.85, y + 0.33, 0.56, f"{i + 1:02d}", size=12)
    text(s, 1.65, y + 0.2, 5.0, 0.35, h, size=15.5, bold=True, color=INK)
    text(s, 1.65, y + 0.55, 5.0, 0.6, b, size=12, color=INK2, spacing=1.05)
card(s, 7.45, 2.35, 5.25, 4.22, 0.32, kind="aura")
text(s, 7.85, 2.7, 4.5, 0.3, D["bigk"], size=10.5, bold=True, color=BLUE, charsp=150)
text(s, 7.85, 3.05, 4.6, 0.9, D["big"], size=46, bold=True, color=DEEP)
text(s, 7.85, 4.05, 4.4, 0.9, D["bigd"], size=13.5, color=INK2, spacing=1.1)
vs = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(7.85), Inches(5.25), Inches(4.45), Inches(0.95))
vs.adjustments[0] = 0.3; vs.fill.solid(); vs.fill.fore_color.rgb = rgb("FFFFFF"); vs.line.fill.background(); vs.shadow.inherit = False
text(s, 8.1, 5.36, 4.1, 0.75, [[("HALO-XR  ", {"bold": True, "color": BLUE, "size": 15}), ("≈ Rp 265.000" if LANG == "id" else "≈ Rp 265,000", {"bold": True, "color": INK, "size": 15})],
                                ["< 1/10 VR · 1 set / 1 kelompok" if LANG == "id" else "< 1/10 of VR · 1 set per group"]], size=11.5, color=INK2)

# 3 · Gap table
D = L["s3"]
s = new_slide(D["chip"], D["t"], D["sub"])
X = [0.6, 4.7, 6.85, 9.0]; Wc = [4.0, 2.05, 2.05, 3.7]
card(s, 9.0, 2.2, 3.7, 4.75, 0.3, kind="aura")
for j, c in enumerate(D["cols"]):
    text(s, X[j] + (0.25 if j == 0 else 0), 2.45, Wc[j] - 0.2, 0.3, c.upper(), size=10.5, bold=True, color=BLUE if j == 3 else MUTED, align="l" if j == 0 else "c", charsp=120)
for i, row in enumerate(D["rows"]):
    y = 2.95 + i * 0.98
    card(s, 0.6, y, 8.15, 0.8, 0.2)
    for j, v in enumerate(row):
        if j == 0:
            text(s, 0.85, y, 3.8, 0.8, v, size=13.5, bold=True, color=INK, anchor="m")
        elif j < 3:
            text(s, X[j], y, Wc[j], 0.8, v, size=12.5, color=INK2, align="c", anchor="m")
        else:
            badge(s, 9.3, y + 0.22, 0.36, "✓", fill=OK if i < 3 else BLUE, size=11)
            text(s, 9.8, y, 2.8, 0.8, v, size=13.5, bold=True, color=DEEP, anchor="m")

# 4 · Solution ecosystem
D = L["s4"]
s = new_slide(D["chip"], D["t"], D["sub"])
cw_ = 3.75
for i, (h, b) in enumerate(D["units"]):
    x = 0.6 + i * (cw_ + 0.5)
    card(s, x, 2.25, cw_, 4.7, 0.3, kind="aura" if i == 1 else "raise")
    if i == 0:
        phone(s, "device_" + LANG, x + 0.875, 2.5, 2.0, crop_h=1.0)
    elif i == 1:
        phone(s, "viewer_holo_" + LANG, x + 0.875, 2.5, 2.0, crop_h=1.0)
    else:
        photo(s, center_crop(MED / "pyramid_heart_real.png", 0.56, 0.84), x + 0.25, 2.55, cw_ - 0.5, 2.0, 0.22)
        text(s, x + 0.25, 4.65, cw_ - 0.5, 0.3, "45° · 7.78 cm", size=10.5, bold=True, color=BLUE, align="c", charsp=100)
    badge(s, x + 0.3, 5.2, 0.46, str(i + 1), size=12)
    text(s, x + 0.9, 5.2, cw_ - 1.1, 0.46, h, size=14.5, bold=True, color=INK, anchor="m")
    text(s, x + 0.3, 5.75, cw_ - 0.55, 1.1, b, size=11.5, color=INK2, spacing=1.05)
    if i < 2: arrow(s, x + cw_ + 0.1, 4.4, 0.3, 0.32)

# 5 · How the hologram forms (4 views)
D = L["s5"]
s = new_slide(D["chip"], D["t"], D["sub"])
pw = 4.7
photo(s, center_crop(MED / "pyramid_brain_holo.png", 0.56, 0.84), 1.7, 2.2, pw, pw, 0.3)
cx, cy = 1.7 + pw / 2, 2.2 + pw / 2
for lab, (dx, dy) in zip(D["labels"], [(0, -1), (1, 0), (0, 1), (-1, 0)]):
    cwid = 0.4 + len(lab) * 0.098 * 8.5 / 9.5
    lx = cx + dx * (pw / 2 + 0.15) - (cwid / 2 if dx == 0 else (0 if dx > 0 else cwid)); ly = cy + dy * (pw / 2 - 0.25) - 0.15
    if dx: lx = cx + dx * pw * 0.28 - cwid / 2; ly = cy + 0.95
    chip(s, lx, ly, lab, fill="0B1A3A", color="BFE3FF", size=8.5, glow_=True)
for i, (h, b) in enumerate(D["pts"]):
    y = 2.35 + i * 1.5
    card(s, 7.95, y, 4.75, 1.2, 0.24, kind="aura" if i == 0 else "raise")
    badge(s, 8.2, y + 0.32, 0.56, f"{i + 1:02d}")
    text(s, 9.0, y + 0.22, 3.6, 0.35, h, size=14.5, bold=True, color=INK)
    text(s, 9.0, y + 0.6, 3.6, 0.5, b, size=12, color=INK2)

# 6 · ADDIE
D = L["s6"]
s = new_slide(D["chip"], D["t"], D["sub"])
card(s, 0.6, 2.2, 5.6, 2.55, 0.28)
pic(s, optic_diagram(), 0.6, 2.05, 5.6)
dl = D["diag"]
text(s, 4.85, 3.55, 1.2, 0.3, dl[0], size=10, bold=True, color=INK2, align="r")
text(s, 0.85, 4.3, 1.6, 0.3, dl[1], size=10, bold=True, color=INK2)
text(s, 4.12, 4.22, 1.6, 0.3, dl[2], size=10, bold=True, color="C47F00")
text(s, 0.75, 3.8, 1.6, 0.3, dl[3], size=10, bold=True, color=BLUE, align="r")
text(s, 6.6, 2.3, 6.1, 0.4, "45°  ·  Snell  ·  Fresnel", size=20, bold=True, color=DEEP)
text(s, 6.6, 2.85, 6.0, 1.6, D["optic"], size=13, color=INK2, spacing=1.1)
sw_ = 2.3
for i, (h, b, st) in enumerate(D["steps"]):
    x = 0.6 + i * (sw_ + 0.17)
    done = st == "done"
    card(s, x, 5.0, sw_, 1.95, 0.22, kind="aura" if i == 2 else "raise")
    badge(s, x + 0.2, 5.18, 0.42, h[0], fill=BLUE if done else "9FB3D6", size=12)
    chip(s, x + sw_ - 1.15, 5.24, D["done"] if done else D["next"], fill=ICE if done else "EEF2F8", color=DEEP if done else MUTED, size=7.5, glow_=False)
    text(s, x + 0.2, 5.7, sw_ - 0.35, 0.3, h, size=13, bold=True, color=INK if done else INK2)
    text(s, x + 0.2, 6.02, sw_ - 0.35, 0.9, b, size=9.5, color=INK2, spacing=1.0)

# 7 · Performance
D = L["s7"]
s = new_slide(D["chip"], D["t"], D["sub"])
for i, (k, l, d_) in enumerate([(D["k1"], D["k1l"], D["k1d"]), (D["k2"], D["k2l"], D["k2d"])]):
    x = 0.6 + i * 4.2
    card(s, x, 2.3, 3.85, 3.0, 0.3, kind="aura")
    badge(s, x + 0.35, 2.6, 0.5, "✓", fill=OK)
    text(s, x + 0.35, 3.25, 3.3, 0.8, k, size=38, bold=True, color=DEEP)
    text(s, x + 0.35, 4.05, 3.3, 0.35, l, size=15, bold=True, color=INK)
    text(s, x + 0.35, 4.45, 3.2, 0.8, d_, size=11.5, color=INK2, spacing=1.05)
card(s, 0.6, 5.65, 8.05, 1.3, 0.24)
text(s, 0.9, 5.82, 7.5, 0.3, D["note"].upper(), size=10, bold=True, color=BLUE, charsp=150)
text(s, 0.9, 6.12, 7.5, 0.8, D["noted"], size=12, color=INK2, spacing=1.05)
organ(s, "heart_real_cut", 9.55, 2.25, 4.4)

# 8 · App
D = L["s8"]
s = new_slide(D["chip"], D["t"], D["sub"])
names = ["library", "viewer_holo", "viewer_cut", "viewer_cell"]
for i, (n, cap) in enumerate(zip(names, D["caps"])):
    x = 0.75 + i * 2.3
    phone(s, f"{n}_{LANG}", x, 2.2, 2.0, crop_h=1.75, float_=(i == 1))
    text(s, x - 0.1, 6.45, 2.2, 0.3, cap, size=11.5, bold=True, color=INK, align="c")
card(s, 9.95, 2.25, 2.75, 4.25, 0.28, kind="aura")
for i, pl in enumerate(D["pills"]):
    y = 2.5 + i * 0.64
    badge(s, 10.15, y + 0.04, 0.32, "✓", fill=BLUE, size=9)
    text(s, 10.6, y, 2.0, 0.45, pl, size=11, bold=True, color=INK, anchor="m")
text(s, 0.6, 6.95, 9.0, 0.25, D["credit"], size=9, color=MUTED)

# 9 · Society 5.0 & SDGs
D = L["s9"]
s = new_slide(D["chip"], D["t"], D["sub"])
for i, (h, b) in enumerate(D["cards"]):
    y = 2.3 + i * 1.3
    card(s, 0.6, y, 6.6, 1.08, 0.24)
    badge(s, 0.85, y + 0.3, 0.54, "✓", fill=BLUE)
    text(s, 1.65, y + 0.16, 5.4, 0.35, h, size=15, bold=True, color=INK)
    text(s, 1.65, y + 0.52, 5.4, 0.6, b, size=12, color=INK2, spacing=1.05)
for i, sd in enumerate(D["sdg"]):
    chip(s, 0.6 if i != 1 else 0.6 + 0.4 + len(D["sdg"][0]) * 0.098 * 9 / 9.5 + 0.15, 6.3 if i < 2 else 6.7, sd, fill="FFFFFF", color=DEEP, size=9)
photo(s, MED / "brain_holo.png", 7.75, 2.3, 4.95, 4.65, 0.32)

# 10 · Validation
D = L["s10"]
s = new_slide(D["chip"], D["t"], D["sub"])
ln = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.13), Inches(2.75), Inches(0.05), Inches(3.4))
ln.fill.solid(); ln.fill.fore_color.rgb = rgb(ICE); ln.line.fill.background(); ln.shadow.inherit = False
for i, (h, b) in enumerate(D["steps"]):
    y = 2.3 + i * 1.5
    badge(s, 0.85, y + 0.25, 0.6, str(i + 1), size=14)
    card(s, 1.75, y, 6.0, 1.2, 0.24, kind="aura" if i == 2 else "raise")
    text(s, 2.0, y + 0.18, 5.5, 0.35, h, size=15, bold=True, color=INK)
    text(s, 2.0, y + 0.55, 5.5, 0.6, b, size=12, color=INK2, spacing=1.05)
phone(s, "learn_" + LANG, 9.15, 2.1, 2.1, crop_h=1.8, float_=True)
text(s, 8.35, 6.55, 3.7, 0.3, D["phone"], size=11, bold=True, color=INK, align="c")
text(s, 8.35, 6.85, 3.7, 0.25, D["sample"], size=9, color=MUTED, align="c")

# 11 · Conclusion (brand background)
D = L["s11"]
s = new_slide(D["chip"], None, None, bg="brand")
text(s, 0.6, 1.0, 8.0, 0.8, D["t1"], size=40, bold=True, color="FFFFFF")
text(s, 0.6, 1.75, 8.0, 0.8, D["t2"], size=40, bold=True, color="BFE3FF")
text(s, 0.6, 2.7, 7.2, 0.9, D["sub"], size=15, color="EAF4FF", spacing=1.1)
for i, (h, b) in enumerate(D["cards"]):
    x = 0.6 + i * 2.6
    card(s, x, 4.15, 2.35, 2.6, 0.26, fill=(236, 243, 252))
    badge(s, x + 0.25, 4.4, 0.5, "✓", fill=BLUE)
    text(s, x + 0.25, 5.05, 1.95, 0.6, h, size=14, bold=True, color=INK, spacing=1.0)
    text(s, x + 0.25, 5.7, 1.95, 1.0, b, size=10.5, color=INK2, spacing=1.05)
aura_orb(s, 10.6, 4.1, 5.5, (255, 255, 255))
organ(s, "brain_real", 8.6, 2.35, 3.6, orb=False)

# 12 · Acknowledgements
D = L["s12"]
s = new_slide(D["chip"], D["t"])
card(s, 0.6, 2.0, 6.3, 4.1, 0.3)
text(s, 0.9, 2.25, 5.5, 0.3, D["inst"].upper(), size=10.5, bold=True, color=BLUE, charsp=150)
pic(s, MED / "logos.png", 0.9, 2.7, 2.6)
for i, nm in enumerate(D["insts"]):
    text(s, 0.9, 3.75 + i * 0.5, 5.8, 0.4, [[("●  ", {"color": BLUE, "size": 10}), (nm, {})]], size=14, bold=True, color=INK)
text(s, 0.9, 5.35, 5.8, 0.6, TEAM, size=10, color=INK2, spacing=1.05)
card(s, 7.35, 2.0, 5.35, 1.85, 0.3, kind="aura")
text(s, 7.65, 2.25, 4.8, 0.3, D["status"].upper(), size=10.5, bold=True, color=BLUE, charsp=150)
text(s, 7.65, 2.6, 4.8, 1.1, D["statusd"], size=15, bold=True, color=INK, spacing=1.1)
card(s, 7.35, 4.25, 5.35, 1.85, 0.3)
text(s, 7.65, 4.5, 4.8, 0.3, D["contact"].upper(), size=10.5, bold=True, color=BLUE, charsp=150)
text(s, 7.65, 4.85, 4.8, 0.45, "partnership@halo-xr.edu.id", size=17, bold=True, color=DEEP)
text(s, 7.65, 5.35, 4.8, 0.45, "github.com/thebuggeddev/anatomy (3D assets)", size=10, color=MUTED)
text(s, 0.6, 6.45, 12.1, 0.6, D["thanks"], size=28, bold=True, color=BLUE, align="c")


# =========================================================== FUTURISTIC FX ===
NS_P = "http://schemas.openxmlformats.org/presentationml/2006/main"
TRANS = (
    '<mc:AlternateContent xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006">'
    '<mc:Choice xmlns:p159="http://schemas.microsoft.com/office/powerpoint/2015/09/main" '
    'xmlns:p14="http://schemas.microsoft.com/office/powerpoint/2010/main" Requires="p159">'
    '<p:transition xmlns:p="%s" spd="slow" p14:dur="1400"><p159:morph option="byObject"/></p:transition>'
    '</mc:Choice><mc:Fallback><p:transition xmlns:p="%s" spd="slow"><p:fade/></p:transition></mc:Fallback>'
    '</mc:AlternateContent>' % (NS_P, NS_P))


class Ids:
    def __init__(self): self.n = 2
    def __call__(self):
        self.n += 1; return self.n


def _target(spid): return f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'


def fx_entrance(nid, spid, delay, dur=650):
    return (f'<p:par><p:cTn id="{nid()}" presetID="42" presetClass="entr" presetSubtype="0" fill="hold" grpId="0" nodeType="withEffect">'
            f'<p:stCondLst><p:cond delay="{delay}"/></p:stCondLst><p:childTnLst>'
            f'<p:set><p:cBhvr><p:cTn id="{nid()}" dur="1" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst></p:cTn>{_target(spid)}'
            f'<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst></p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>'
            f'<p:animEffect transition="in" filter="fade"><p:cBhvr><p:cTn id="{nid()}" dur="{dur}"/>{_target(spid)}</p:cBhvr></p:animEffect>'
            f'<p:anim calcmode="lin" valueType="num"><p:cBhvr><p:cTn id="{nid()}" dur="{dur}" decel="100000" fill="hold"/>{_target(spid)}'
            f'<p:attrNameLst><p:attrName>ppt_y</p:attrName></p:attrNameLst></p:cBhvr><p:tavLst>'
            f'<p:tav tm="0"><p:val><p:strVal val="#ppt_y+0.04"/></p:val></p:tav><p:tav tm="100000"><p:val><p:strVal val="#ppt_y"/></p:val></p:tav>'
            f'</p:tavLst></p:anim></p:childTnLst></p:cTn></p:par>')


def fx_float(nid, spid, delay, amp=0.012, dur=2600):
    return (f'<p:par><p:cTn id="{nid()}" presetID="0" presetClass="path" presetSubtype="0" repeatCount="indefinite" accel="50000" decel="50000" autoRev="1" fill="hold" grpId="1" nodeType="withEffect">'
            f'<p:stCondLst><p:cond delay="{delay}"/></p:stCondLst><p:childTnLst>'
            f'<p:animMotion origin="layout" path="M 0 0 L 0 -{amp} E" pathEditMode="relative" ptsTypes="AA"><p:cBhvr>'
            f'<p:cTn id="{nid()}" dur="{dur}" fill="hold"/>{_target(spid)}<p:attrNameLst><p:attrName>ppt_x</p:attrName><p:attrName>ppt_y</p:attrName></p:attrNameLst>'
            f'</p:cBhvr><p:rCtr x="0" y="0"/></p:animMotion></p:childTnLst></p:cTn></p:par>')


def fx_pulse(nid, spid, delay, dur=3200):
    return (f'<p:par><p:cTn id="{nid()}" presetID="6" presetClass="emph" presetSubtype="0" repeatCount="indefinite" accel="50000" decel="50000" autoRev="1" fill="hold" grpId="1" nodeType="withEffect">'
            f'<p:stCondLst><p:cond delay="{delay}"/></p:stCondLst><p:childTnLst>'
            f'<p:animScale><p:cBhvr><p:cTn id="{nid()}" dur="{dur}" fill="hold"/>{_target(spid)}</p:cBhvr><p:by x="112000" y="112000"/></p:animScale>'
            f'</p:childTnLst></p:cTn></p:par>')


def apply_fx(slide, start):
    nid = Ids()
    pars, blds = [], []
    step, delay = 55, 150
    for sh in list(slide.shapes)[start:]:
        spid = sh.shape_id
        if sh.name.startswith("FX_PULSE"):
            pars.append(fx_pulse(nid, spid, 0)); continue
        pars.append(fx_entrance(nid, spid, min(delay, 2200)))
        if sh.name.startswith("FX_FLOAT"):
            pars.append(fx_float(nid, spid, min(delay, 2200) + 700))
        if sh.shape_type != 13:
            blds.append(f'<p:bldP spid="{spid}" grpId="0" animBg="1"/>')
        delay += step
    sld = slide._element
    anchor = sld.find(qn("p:clrMapOvr"))
    if anchor is None: anchor = sld.find(qn("p:cSld"))
    t = etree.fromstring(TRANS); anchor.addnext(t)
    if not pars: return
    xml = (f'<p:timing xmlns:p="{NS_P}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
           f'<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
           f'<p:par><p:cTn id="{nid()}" fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst><p:childTnLst>'
           f'<p:par><p:cTn id="{nid()}" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
           + "".join(pars) +
           '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>'
           '</p:childTnLst></p:cTn><p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
           '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
           '</p:childTnLst></p:cTn></p:par></p:tnLst>'
           + (f'<p:bldLst>{"".join(blds)}</p:bldLst>' if blds else '') + '</p:timing>')
    t.addnext(etree.fromstring(xml))


for sl in prs.slides:
    apply_fx(sl, FX_START.get(sl.slide_id, len(sl.shapes)))

assert len(prs.slides) == TOTAL, len(prs.slides)
prs.save(OUT)
print("saved", OUT, len(prs.slides), "slides")
