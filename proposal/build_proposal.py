"""
HALO-XR · Proposal kemitraan (A4, PDF, dekoratif) — satu PDF per sekolah tujuan, tanpa surat pengantar dan tanpa logo sekolah.
Pakai: python proposal/build_proposal.py        → output/Proposal_Kemitraan_HALO-XR_<sekolah>.pdf
Data yang belum diketahui ditandai <mark>[...]</mark> (kuning) agar mudah dilengkapi sebelum dikirim.
"""
import asyncio, pathlib, html
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
B = ROOT / "proposal/build"; B.mkdir(parents=True, exist_ok=True)
OUT = ROOT / "output"; OUT.mkdir(exist_ok=True)
U = lambda p: (ROOT / p).as_uri()
TEAM = ["Afkar Gilang Prasetya", "Aufa Bayu Nur Rahman", "Kamajaya Willia Zabir", "M. Azhar Rifky Zulkarnain", "Tirta Manggala Nusantara", "Toti Surya Samantha"]
PH = lambda t: f"<mark>[{t}]</mark>"
E = html.escape

SCHOOLS = [
    {"slug": "SMA_Al_Azhar_Syifa_Budi_Solo", "name": "SMA Al Azhar Syifa Budi Solo", "head": "Kepala SMA Al Azhar Syifa Budi Solo", "level": "SMA",
     "kur": "Biologi Fase E–F (kelas X–XII): sel, jaringan, serta struktur dan fungsi sistem organ manusia",
     "materi": ["Sel hewan & organel", "Sistem peredaran darah (jantung)", "Sistem saraf (otak) & indra (mata)", "Sistem pernapasan, pencernaan, ekskresi"],
     "note": "Kami berharap SMA Al Azhar Syifa Budi Solo dapat menjadi salah satu sekolah pertama yang menerapkan HALO-XR di kelas Biologi."},
    {"slug": "SMA_Negeri_4_Surakarta", "name": "SMA Negeri 4 Surakarta", "head": "Kepala SMA Negeri 4 Surakarta", "level": "SMA",
     "kur": "Biologi Fase E–F (kelas X–XII): sel, jaringan, serta struktur dan fungsi sistem organ manusia",
     "materi": ["Sel hewan & organel", "Sistem peredaran darah (jantung)", "Sistem saraf (otak) & indra (mata)", "Sistem pernapasan, pencernaan, ekskresi"],
     "note": "SMA Negeri 4 Surakarta telah mendukung HALO-XR sebagai institusi riset sejak tahap pengembangan. Kemitraan ini melanjutkan dukungan tersebut ke tahap penerapan di kelas."},
    {"slug": "SMP_Al_Azhar_Syifa_Budi_Solo", "name": "SMP Al Azhar Syifa Budi Solo", "head": "Kepala SMP Al Azhar Syifa Budi Solo", "level": "SMP",
     "kur": "IPA Fase D (kelas VII–IX): sel sebagai unit kehidupan dan sistem organ pada manusia",
     "materi": ["Sel hewan (kelas VII)", "Peredaran darah & pernapasan (kelas VIII)", "Pencernaan & ekskresi (kelas VIII)", "Sistem saraf & indra (kelas IX)"],
     "note": "Untuk jenjang SMP, HALO-XR membantu siswa membangun gambaran 3D organ sejak awal mempelajari sistem organ, sehingga lebih siap ketika materi diperdalam di SMA."},
]

# ikon garis sederhana (stroke = currentColor)
I = {
    "brain": '<path d="M9 4a3 3 0 0 0-3 3 3 3 0 0 0-2 5 3 3 0 0 0 2 5 3 3 0 0 0 3 3h1V4Z"/><path d="M15 4a3 3 0 0 1 3 3 3 3 0 0 1 2 5 3 3 0 0 1-2 5 3 3 0 0 1-3 3h-1V4Z"/>',
    "vr": '<rect x="2" y="7" width="20" height="10" rx="4"/><circle cx="8" cy="12" r="2"/><circle cx="16" cy="12" r="2"/>',
    "coin": '<circle cx="12" cy="12" r="9"/><path d="M14.5 9.5c-.5-1-1.5-1.5-2.5-1.5-1.7 0-2.8 1-2.8 2.2 0 2.8 5.6 1.4 5.6 4.2 0 1.2-1.2 2.1-2.8 2.1-1.1 0-2.2-.6-2.7-1.6M12 6v2m0 8v2"/>',
    "pyramid": '<path d="M12 3 21 20H3Z"/><path d="M12 3v17M7.5 11.5h9"/>',
    "tablet": '<rect x="4" y="2" width="16" height="20" rx="3"/><path d="M10 18h4"/>',
    "hand": '<path d="M7 11V6.5a1.5 1.5 0 0 1 3 0V11M10 10V4.5a1.5 1.5 0 0 1 3 0V10M13 10V5.5a1.5 1.5 0 0 1 3 0V12M16 9.5a1.5 1.5 0 0 1 3 0V14a7 7 0 0 1-7 7h-1a6 6 0 0 1-5-2.7L3.5 14a1.5 1.5 0 0 1 2.5-1.7L7 14"/>',
    "school": '<path d="m2 9 10-5 10 5-10 5Z"/><path d="M6 11v5c3 2.5 9 2.5 12 0v-5"/>',
    "teacher": '<circle cx="12" cy="7" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0"/><circle cx="17" cy="9" r="2.5"/><path d="M17 14a5 5 0 0 1 4.5 5"/>',
    "layers": '<path d="m12 3 9 5-9 5-9-5Z"/><path d="m3 13 9 5 9-5"/>',
    "mic": '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0M12 18v3"/>',
    "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
    "shield": '<path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6Z"/><path d="m9 12 2 2 4-4"/>',
    "star": '<path d="m12 3 2.8 5.8 6.2.9-4.5 4.4 1 6.2L12 17.4 6.5 20.3l1-6.2L3 9.7l6.2-.9Z"/>',
    "gauge": '<path d="M4 18a8 8 0 1 1 16 0"/><path d="m12 14 4-5"/>',
    "book": '<path d="M4 4h6a3 3 0 0 1 3 3v13a2 2 0 0 0-2-2H4Z"/><path d="M20 4h-6a3 3 0 0 0-3 3v13a2 2 0 0 1 2-2h7Z"/>',
    "box": '<path d="m12 3 9 4.5v9L12 21l-9-4.5v-9Z"/><path d="m3 7.5 9 4.5 9-4.5M12 12v9"/>',
    "wifi": '<path d="M2 9a15 15 0 0 1 20 0M5 12.5a10 10 0 0 1 14 0M8.5 16a5 5 0 0 1 7 0"/><circle cx="12" cy="19.5" r="1"/>',
}
ico = lambda k, cls="ico": f'<span class="{cls}"><svg viewBox="0 0 24 24">{I[k]}</svg></span>'

PYR_ART = '''<svg class="pyr-art" viewBox="0 0 200 200" fill="none" stroke="currentColor" stroke-width="1.2">
  <path d="M100 20 180 170H20Z"/><path d="M100 20v150M60 95h80M40 132h120" stroke-dasharray="3 4"/>
  <path d="M100 20 140 170M100 20 60 170" opacity=".5"/><circle cx="100" cy="112" r="16" stroke-dasharray="2 3"/></svg>'''

CSS = f"""
@font-face{{font-family:PJS;src:url('{U("video/fonts/PJS-Medium.ttf")}');font-weight:500}}
@font-face{{font-family:PJS;src:url('{U("video/fonts/PJS-SemiBold.ttf")}');font-weight:600}}
@font-face{{font-family:PJS;src:url('{U("video/fonts/PJS-Bold.ttf")}');font-weight:700}}
@font-face{{font-family:PJS;src:url('{U("video/fonts/PJS-ExtraBold.ttf")}');font-weight:800}}
@page{{size:A4;margin:0}}
:root{{--ink:#16233F;--ink2:#4A5A7A;--muted:#8392AE;--blue:#2F7BFF;--deep:#1646D6;--sky:#8CC6FF;--ice:#DDEBFF;--sd:#C6D2E3;--navy:#08132F;
  --grad:linear-gradient(135deg,#2F7BFF,#1646D6)}}
*{{box-sizing:border-box;margin:0;padding:0}}
html{{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
body{{font-family:PJS,'Segoe UI',sans-serif;font-weight:500;color:var(--ink);font-size:10pt;line-height:1.55}}
.page{{width:210mm;height:297mm;position:relative;overflow:hidden;page-break-after:always;padding:24mm 17mm 22mm;
  background:radial-gradient(130mm 130mm at 108% -8%,rgba(140,198,255,.42),transparent 70%),radial-gradient(120mm 120mm at -12% 110%,rgba(110,160,255,.28),transparent 70%),linear-gradient(170deg,#F8FAFE,#E7EEF8)}}
.page:last-child{{page-break-after:auto}}
.page>*{{position:relative;z-index:1}}
/* ornamen */
.wm{{position:absolute!important;z-index:0!important;right:-4mm;top:6mm;font-size:150pt;font-weight:800;line-height:1;color:rgba(47,123,255,.07);letter-spacing:-.04em}}
.dots{{position:absolute!important;z-index:0!important;width:46mm;height:30mm;background-image:radial-gradient(rgba(47,123,255,.28) .5mm,transparent .6mm);background-size:4.2mm 4.2mm}}
.gridbg{{position:absolute!important;z-index:0!important;inset:0;background-image:linear-gradient(rgba(47,123,255,.06) .25mm,transparent .25mm),linear-gradient(90deg,rgba(47,123,255,.06) .25mm,transparent .25mm);background-size:9mm 9mm;
  -webkit-mask-image:radial-gradient(circle at 85% 10%,#000 0,transparent 55%);mask-image:radial-gradient(circle at 85% 10%,#000 0,transparent 55%)}}
.pyr-art{{position:absolute!important;z-index:0!important;color:rgba(47,123,255,.22);width:52mm;right:10mm;bottom:20mm}}
.orb{{position:absolute!important;z-index:0!important;border-radius:50%;background:radial-gradient(circle,rgba(70,150,255,.38),transparent 68%)}}
.runhead{{position:absolute!important;left:17mm;right:17mm;top:9mm;display:flex;justify-content:space-between;align-items:center;font-size:7.8pt;color:var(--muted);font-weight:700;letter-spacing:.05em}}
.runhead .l{{display:flex;align-items:center;gap:2mm;color:var(--ink);font-weight:800}}
.runhead img{{height:6.5mm;border-radius:2mm}}
.foot{{position:absolute!important;left:17mm;right:17mm;bottom:9mm;display:flex;justify-content:space-between;align-items:center;font-size:7.8pt;color:var(--muted);font-weight:700}}
.foot .pg{{display:inline-grid;place-items:center;min-width:8mm;height:8mm;border-radius:99px;background:var(--grad);color:#fff;font-weight:800;box-shadow:0 1.5mm 4mm rgba(47,123,255,.4)}}
.foot .bar{{flex:1;height:.4mm;margin:0 4mm;background:linear-gradient(90deg,rgba(47,123,255,.35),transparent)}}
/* tipografi */
h1{{font-size:31pt;line-height:1.06;font-weight:800;letter-spacing:-.02em}}
h2{{font-size:20pt;line-height:1.12;font-weight:800;letter-spacing:-.015em}}
h3{{font-size:11pt;font-weight:800;margin-bottom:1.2mm;line-height:1.3}}
.b{{color:var(--blue)}}
.kicker{{display:inline-flex;align-items:center;gap:2mm;font-size:7.5pt;font-weight:800;letter-spacing:.16em;color:var(--blue);background:#fff;padding:1.6mm 3.8mm;border-radius:99px;box-shadow:0 2mm 5mm rgba(47,123,255,.16);margin-bottom:3mm}}
.kicker i{{width:2mm;height:2mm;border-radius:50%;background:var(--grad);display:block}}
.title{{margin-bottom:5mm}}
.title .line{{width:22mm;height:1.6mm;border-radius:2mm;background:var(--grad);margin-top:3mm;box-shadow:0 1mm 3mm rgba(47,123,255,.35)}}
p{{margin-bottom:2.4mm;color:var(--ink2)}}
.lead{{font-size:11pt}}
.small{{font-size:8.6pt}} .muted{{color:var(--muted)}}
mark{{background:#FFF1A8;color:#5C4A00;padding:0 1mm;border-radius:1mm;font-weight:700}}
/* kartu */
.card{{background:linear-gradient(160deg,#FFFFFF,#F0F4FB);border-radius:6mm;padding:5mm;box-shadow:2mm 2.5mm 6mm rgba(92,140,255,.17),-1.5mm -1.5mm 4mm rgba(255,255,255,.95)}}
.card.aura{{background:radial-gradient(circle at 25% 15%,#fff,#E0ECFF);box-shadow:0 0 0 .35mm #fff inset,0 3mm 9mm rgba(47,123,255,.26)}}
.card.blue{{background:linear-gradient(135deg,#2F7BFF,#1646D6);color:#fff;box-shadow:0 4mm 10mm rgba(47,123,255,.4)}}
.card.blue p,.card.blue h3{{color:#fff}} .card.blue p{{opacity:.92}}
.card.dark{{background:radial-gradient(120% 90% at 50% 0%,#12285A,#08132F 60%,#040917);color:#EAF4FF;box-shadow:0 4mm 12mm rgba(8,19,47,.35)}}
.card.dark p,.card.dark h3{{color:#EAF4FF}}
.ico{{display:inline-grid;place-items:center;width:10mm;height:10mm;border-radius:3.2mm;background:var(--grad);box-shadow:0 1.8mm 4.5mm rgba(47,123,255,.4);margin-bottom:2.5mm}}
.ico svg{{width:5.4mm;height:5.4mm;fill:none;stroke:#fff;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}}
.ico.soft{{background:var(--ice);box-shadow:none}} .ico.soft svg{{stroke:var(--deep)}}
.ico.white{{background:rgba(255,255,255,.18);box-shadow:none}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:5mm}}
.grid3{{display:grid;grid-template-columns:repeat(3,1fr);gap:4.5mm}}
.grid4{{display:grid;grid-template-columns:repeat(4,1fr);gap:4mm}}
ul.tick{{list-style:none}}
ul.tick li{{position:relative;padding-left:5.5mm;margin-bottom:1.4mm;color:var(--ink2)}}
ul.tick li::before{{content:"";position:absolute;left:0;top:1.5mm;width:2.8mm;height:2.8mm;border-radius:50%;background:var(--grad)}}
.card.blue ul.tick li{{color:#fff}} .card.blue ul.tick li::before{{background:#fff}}
.kpi b{{display:block;font-size:19pt;font-weight:800;line-height:1.1;white-space:nowrap}}
.kpi span{{font-size:8.3pt;font-weight:600}}
.pill{{display:inline-block;padding:1.4mm 3.4mm;border-radius:99px;background:#fff;color:var(--deep);font-weight:700;font-size:8.4pt;margin:0 1.6mm 1.8mm 0;box-shadow:0 1mm 3mm rgba(47,123,255,.12)}}
.imgcard{{border-radius:6mm;overflow:hidden;border:1.2mm solid #fff;box-shadow:0 3mm 9mm rgba(47,123,255,.3)}}
.imgcard img{{display:block;width:100%;object-fit:cover}}
.phone{{border-radius:6mm;border:2mm solid #0B0F1A;box-shadow:0 4mm 10mm rgba(47,100,235,.3);overflow:hidden;background:#000}}
.phone img{{display:block;width:100%;height:100%;object-fit:cover;object-position:top}}
table{{width:100%;border-collapse:collapse;font-size:9pt}}
th{{text-align:left;font-size:7.4pt;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);padding:1.8mm 2.5mm;border-bottom:.3mm solid var(--sd)}}
td{{padding:2.1mm 2.5mm;border-bottom:.25mm solid rgba(198,210,227,.6);color:var(--ink2);vertical-align:top}}
td b{{color:var(--ink)}}
.yes{{color:#0E7A50;font-weight:800}}
/* timeline */
.tl{{position:relative;padding-left:9mm}}
.tl::before{{content:"";position:absolute;left:3.4mm;top:2mm;bottom:2mm;width:.8mm;border-radius:1mm;background:linear-gradient(var(--blue),var(--sky))}}
.tl-item{{position:relative;margin-bottom:3.2mm}}
.tl-item::before{{content:"";position:absolute;left:-7.6mm;top:1.2mm;width:3.6mm;height:3.6mm;border-radius:50%;background:#fff;border:1mm solid var(--blue);box-shadow:0 0 0 1.2mm rgba(47,123,255,.15)}}
.tl-item .when{{display:inline-block;font-size:7.6pt;font-weight:800;letter-spacing:.06em;color:#fff;background:var(--grad);padding:.8mm 2.6mm;border-radius:99px;margin-bottom:1mm}}
.tl-item h3{{margin:0}}
/* sampul */
.cover{{padding:0;background:#F6F9FE}}
.cover .panel{{position:absolute!important;right:0;top:0;width:112mm;height:206mm;border-bottom-left-radius:60mm;
  background:radial-gradient(90% 70% at 60% 30%,#2A63E8,#1646D6 45%,#0B2A86);overflow:hidden}}
.cover .panel .g{{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.08) .25mm,transparent .25mm),linear-gradient(90deg,rgba(255,255,255,.08) .25mm,transparent .25mm);background-size:10mm 10mm}}
.cover .panel .ring{{position:absolute;border-radius:50%;border:.5mm solid rgba(191,227,255,.35)}}
.cover .float{{position:absolute!important}}
.cover .glow{{position:absolute!important;border-radius:50%;background:radial-gradient(circle,rgba(191,227,255,.55),transparent 65%)}}
.signs{{display:grid;grid-template-columns:1fr 1fr;gap:12mm;text-align:center;margin-top:10mm}}
.signs .sp{{height:17mm}}
.signs u{{font-weight:800;text-decoration:none;border-bottom:.3mm solid var(--ink)}}
.meta td{{border:0;padding:.7mm 0;color:var(--ink)}}
"""


def page(inner, s, n, total, wm="", cls="", deco=True):
    rh = f'<div class="runhead"><span class="l"><img src="{U("assets/icon-512.png")}">HALO-XR</span><span>PROPOSAL KEMITRAAN · {E(s["name"]).upper()}</span></div>'
    ft = f'<div class="foot"><span>Tim HALO-XR · Tahun Ajaran 2026/2027</span><span class="bar"></span><span class="pg">{n}</span></div>'
    orn = (f'<div class="gridbg"></div><div class="wm">{wm}</div><div class="dots" style="left:6mm;bottom:26mm"></div>{PYR_ART}' if deco else "")
    return f'<section class="page {cls}">{orn}{rh if deco else ""}{inner}{ft if deco else ""}</section>'


def title(kick, t1, t2):
    return f'<div class="title"><span class="kicker"><i></i>{kick}</span><h2>{t1} <span class="b">{t2}</span></h2><div class="line"></div></div>'


def build(s):
    lv, nm = s["level"], E(s["name"])
    mapel = "Biologi" if lv == "SMA" else "IPA"
    P = []

    # 1 · SAMPUL -------------------------------------------------------------
    P.append(("", "cover", False, f"""
    <div class="panel"><div class="g"></div>
      <div class="ring" style="width:150mm;height:150mm;left:-10mm;top:20mm"></div>
      <div class="ring" style="width:100mm;height:100mm;left:15mm;top:45mm"></div></div>
    <div class="glow" style="width:120mm;height:120mm;right:-4mm;top:30mm"></div>
    <img class="float" src="{U('deck/build/media/heart_real.png')}" style="right:16mm;top:44mm;width:92mm">
    <img class="float" src="{U('deck/build/media/brain_real.png')}" style="right:76mm;top:20mm;width:40mm;opacity:.95">
    <img class="float" src="{U('deck/build/media/lungs_real.png')}" style="right:4mm;top:150mm;width:36mm">
    <svg class="float" viewBox="0 0 200 200" style="right:62mm;top:158mm;width:30mm;color:rgba(255,255,255,.55)" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M100 20 180 170H20Z"/><path d="M100 20v150M60 95h80" stroke-dasharray="3 4"/></svg>
    <div style="position:absolute;left:17mm;top:20mm;display:flex;align-items:center;gap:3mm">
      <img src="{U('assets/icon-512.png')}" style="height:12mm;border-radius:3.5mm;box-shadow:0 2mm 5mm rgba(47,123,255,.4)">
      <b style="font-size:15pt;font-weight:800">HALO-XR</b></div>
    <div class="dots" style="left:17mm;top:46mm;width:38mm;height:22mm"></div>
    <div style="position:absolute;left:17mm;top:78mm;width:78mm">
      <span class="kicker"><i></i>PROPOSAL KEMITRAAN</span>
      <h1 style="font-size:33pt">Hologram<br>Anatomi<br><span class="b">Interaktif</span><br><span class="b">HALO-XR</span></h1>
      <p class="lead" style="margin-top:5mm">Media belajar anatomi 3D tanpa headset, dikendalikan gestur tangan dan suara, untuk kelas yang lebih aktif dan kolaboratif.</p>
      <div style="margin-top:3mm"><span class="pill">Pepper's Ghost</span><span class="pill">10 model 3D</span><span class="pill">Tanpa sentuh</span></div></div>
    <div class="card aura" style="position:absolute;left:17mm;top:222mm;width:104mm">
      <div style="display:flex;gap:4mm;align-items:center">{ico('school')}
      <div><span class="small muted" style="font-weight:800;letter-spacing:.12em">DIAJUKAN KEPADA</span>
        <h3 style="font-size:13pt;margin:.5mm 0 0">{E(s['head'])}</h3></div></div></div>
    <div style="position:absolute;left:17mm;right:17mm;bottom:12mm;display:flex;justify-content:space-between;align-items:flex-end;gap:8mm">
      <div><span class="small muted" style="font-weight:800;letter-spacing:.12em">DISUSUN OLEH TIM HALO-XR</span>
        <p class="small" style="margin:1mm 0 0">{' · '.join(TEAM)}</p></div>
      <div style="text-align:right;white-space:nowrap"><span class="small muted" style="font-weight:800;letter-spacing:.12em">TAHUN AJARAN</span><p style="margin:0;font-weight:800;color:var(--ink)">2026/2027</p></div></div>
    <div class="card blue" style="position:absolute;right:17mm;top:214mm;width:58mm;padding:4mm 5mm">
      <div class="kpi"><b>1 hari</b><span>program implementasi di kelas · ± 3 jam pelajaran</span></div></div>"""))

    # 2 · RINGKASAN & LATAR BELAKANG -----------------------------------------
    P.append(("01", "", True, f"""
    {title('RINGKASAN', 'Anatomi itu 3D,', 'kelas masih datar.')}
    <div class="card blue" style="margin-bottom:5mm;display:flex;gap:5mm;align-items:center">
      {ico('star', 'ico white')}<p style="margin:0;font-size:10.4pt">HALO-XR mengajak <b>{nm}</b> menjadi <b>sekolah mitra implementasi</b> melalui <b>program satu hari</b> di kelas. Tim membawa unit hologram, aplikasi, dan seluruh perlengkapan serta memandu kegiatan dari awal hingga akhir. Sekolah cukup menyediakan satu kelas, guru pendamping, dan waktu ± 3 jam pelajaran.</p></div>
    <p>Pemahaman anatomi menuntut kemampuan spasial: siswa perlu membayangkan bentuk, letak, dan hubungan antarorgan dalam tiga dimensi. Namun, pembelajaran di kelas masih banyak bertumpu pada buku, gambar, dan video yang datar dan pasif. {s['note']}</p>
    <div class="grid3" style="margin:4mm 0 5mm">
      <div class="card">{ico('book')}<h3>Kesenjangan kognitif</h3><p class="small" style="margin:0">Materi 3D dipelajari lewat media 2D yang statis, sehingga struktur organ sulit dibayangkan.</p></div>
      <div class="card">{ico('vr')}<h3>Hambatan VR</h3><p class="small" style="margin:0">VR imersif, tetapi hanya untuk satu pengguna, dapat memicu pusing, dan menyulitkan diskusi.</p></div>
      <div class="card">{ico('coin')}<h3>Biaya tinggi</h3><p class="small" style="margin:0">Perangkat VR mahal, sehingga tidak realistis disediakan untuk setiap siswa.</p></div></div>
    <div class="grid2" style="align-items:stretch">
      <div class="card aura"><h3>Celah yang dijawab</h3><p class="small">HALO-XR menggabungkan <b>keterjangkauan dan sifat kelompok</b> media konvensional dengan <b>pengalaman 3D interaktif</b> seperti VR.</p>
        <img src="{U('deck/build/media/heart_real_cut.png')}" style="height:36mm;display:block;margin:2mm auto 0"></div>
      <div class="card"><table><tr><th>Kriteria</th><th>Buku</th><th>VR</th><th>HALO-XR</th></tr>
        <tr><td>Tampilan 3D</td><td>Tidak</td><td>Ya</td><td class="yes">✓ 4 sisi</td></tr>
        <tr><td>Untuk kelompok</td><td>Ya</td><td>1 orang</td><td class="yes">✓ Ya</td></tr>
        <tr><td>Interaktif</td><td>Tidak</td><td>Ya</td><td class="yes">✓ Tanpa sentuh</td></tr>
        <tr><td>Biaya</td><td>Rendah</td><td>Tinggi</td><td class="yes">✓ Sangat rendah</td></tr></table></div></div>"""))

    # 3 · TENTANG HALO-XR ----------------------------------------------------
    P.append(("02", "", True, f"""
    {title('PRODUK', 'Mengenal', 'HALO-XR')}
    <p>Ekosistem siber-fisik tanpa sentuh yang terdiri atas tiga unit dan dapat dirakit ulang oleh sekolah.</p>
    <div class="grid3" style="margin:3mm 0 4mm">
      <div class="card">{ico('pyramid')}<h3>Unit optik</h3><p class="small" style="margin:0">Piramida akrilik 45° memantulkan layar sehingga organ 3D tampak melayang.</p></div>
      <div class="card blue">{ico('tablet', 'ico white')}<h3>Unit tampilan</h3><p class="small" style="margin:0">Aplikasi web di tablet sekolah merender 4 tampilan sinkron dari empat sisi.</p></div>
      <div class="card">{ico('hand')}<h3>Unit kontrol</h3><p class="small" style="margin:0">Gestur lewat kamera bawaan, perintah suara, atau sensor inframerah (opsional).</p></div></div>
    <div style="display:grid;grid-template-columns:1.2fr 1fr;gap:6mm">
      <div><div class="imgcard"><img src="{U('deck/build/media/pyramid_heart_real.png')}" style="height:42mm"></div>
        <p class="small muted" style="margin:2mm 0 4mm">Mode piramida: empat tampilan organ dipantulkan ke empat sisi piramida.</p>
        <div class="grid2" style="gap:3mm">
          <div class="card" style="padding:3.5mm">{ico('layers', 'ico soft')}<h3 style="font-size:9.6pt">10 model 3D</h3><p class="small" style="margin:0">Jantung, otak, paru, hati, ginjal, mata, usus, pankreas, kulit, sel.</p></div>
          <div class="card" style="padding:3.5mm">{ico('brain', 'ico soft')}<h3 style="font-size:9.6pt">Kupas lapisan</h3><p class="small" style="margin:0">Lihat bagian dalam organ, lengkap dengan label struktur.</p></div>
          <div class="card" style="padding:3.5mm">{ico('mic', 'ico soft')}<h3 style="font-size:9.6pt">Gestur & suara</h3><p class="small" style="margin:0">9 gestur tangan dan perintah suara berbahasa Indonesia.</p></div>
          <div class="card" style="padding:3.5mm">{ico('chart', 'ico soft')}<h3 style="font-size:9.6pt">Pre/posttest</h3><p class="small" style="margin:0">N-gain dihitung otomatis di menu Kelas.</p></div></div></div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:3.5mm;align-content:start">
        <div class="phone" style="height:56mm"><img src="{U('deck/build/screens/viewer_holo_id.png')}"></div>
        <div class="phone" style="height:56mm;margin-top:6mm"><img src="{U('deck/build/screens/viewer_cut_id.png')}"></div>
        <div class="phone" style="height:56mm"><img src="{U('deck/build/screens/library_id.png')}"></div>
        <div class="phone" style="height:56mm;margin-top:6mm"><img src="{U('deck/build/screens/learn_id.png')}"></div></div></div>
    <div class="grid3" style="margin-top:4mm">
      <div class="card kpi"><b class="b">10 model 3D</b><span class="muted">organ dan sel siap ditampilkan</span></div>
      <div class="card kpi"><b class="b">108,3 ms</b><span class="muted">estimasi latensi (target ≤ 150 ms)</span></div>
      <div class="card kpi"><b class="b">3–6 siswa</b><span class="muted">mengamati bersama per unit</span></div></div>"""))

    # 4 · TUJUAN & MANFAAT ---------------------------------------------------
    mat = "".join(f'<span class="pill">{E(m)}</span>' for m in s["materi"])
    P.append(("03", "", True, f"""
    {title('TUJUAN & MANFAAT', 'Mengapa', 'bermitra?')}
    <div class="grid3" style="margin-bottom:5mm">
      <div class="card"><h3>Menerapkan</h3><p class="small" style="margin:0">HALO-XR secara langsung di kelas {nm} dalam satu hari kegiatan.</p></div>
      <div class="card"><h3>Mengukur</h3><p class="small" style="margin:0">Pengaruhnya terhadap pemahaman konsep dan keterlibatan siswa.</p></div>
      <div class="card"><h3>Menyempurnakan</h3><p class="small" style="margin:0">Produk berdasarkan masukan nyata dari guru dan siswa.</p></div></div>
    <div class="grid3" style="margin-bottom:5mm">
      <div class="card aura">{ico('school')}<h3>Bagi sekolah</h3><ul class="tick small"><li>Media 3D inovatif berbiaya rendah</li><li>Pengalaman langsung tanpa biaya</li><li>Publikasi inovasi bersama</li><li>Tetap memakai aplikasi setelah program</li></ul></div>
      <div class="card blue">{ico('teacher', 'ico white')}<h3>Bagi guru</h3><ul class="tick small"><li>Mengenal media 3D baru secara praktis</li><li>Pre/posttest & N-gain otomatis</li><li>Panduan pemakaian lanjutan</li><li>Sertifikat guru mitra</li></ul></div>
      <div class="card aura">{ico('users')}<h3>Bagi siswa</h3><ul class="tick small"><li>Mengamati organ 3D dari 4 sisi</li><li>Belajar aktif berkelompok</li><li>Interaksi tanpa sentuh, higienis</li><li>Mengenal teknologi Society 5.0</li></ul></div></div>
    <div class="card dark" style="display:grid;grid-template-columns:1fr 62mm;gap:5mm;align-items:center;padding:6mm">
      <div><span class="kicker" style="background:rgba(255,255,255,.12);color:#BFE3FF;box-shadow:none"><i></i>KURIKULUM MERDEKA</span>
        <h3 style="font-size:12.5pt">Selaras dengan materi {mapel}</h3>
        <p class="small">{E(s['kur'])}.</p>
        <div style="margin-top:2mm">{mat}</div>
        <p class="small" style="margin:2mm 0 0;opacity:.8">Pemetaan materi disesuaikan dengan modul ajar guru {nm}.</p></div>
      <img src="{U('deck/build/media/brain_holo.png')}" style="width:62mm;height:62mm;object-fit:cover;border-radius:5mm"></div>"""))

    # 5 · BENTUK KEMITRAAN ---------------------------------------------------
    P.append(("04", "", True, f"""
    {title('BENTUK KEMITRAAN', 'Program implementasi', 'satu hari')}
    <p>Kemitraan berbentuk <b>program implementasi satu hari</b> (± 3 jam pelajaran) pada satu kelas yang ditentukan sekolah, dengan pembagian peran berikut.</p>
    <div class="grid2" style="margin:4mm 0 5mm">
      <div class="card blue">{ico('box', 'ico white')}<h3>Tim HALO-XR menyediakan</h3><ul class="tick small">
        <li>2 unit piramida HALO-XR beserta perangkatnya</li><li>Akses aplikasi HALO-XR tanpa biaya</li><li>Pemandu kegiatan dan briefing guru</li>
        <li>LKPD dan instrumen pre/posttest</li><li>Dukungan teknis selama kegiatan</li><li>Laporan hasil untuk sekolah (H+7)</li></ul></div>
      <div class="card aura">{ico('school')}<h3>Sekolah mitra menyediakan</h3><ul class="tick small">
        <li>Guru pendamping {mapel} dan 1 kelas peserta</li><li>Waktu ± 3 jam pelajaran pada hari kegiatan</li><li>Ruang kelas yang dapat diredupkan</li>
        <li>Akses stopkontak listrik di kelas</li><li>Izin pengambilan data anonim</li><li>Masukan untuk penyempurnaan produk</li></ul></div></div>
    <h3>Ketentuan umum</h3>
    <div class="grid2" style="gap:3.5mm;margin-bottom:5mm">
      <div class="card" style="padding:4mm;display:flex;gap:3mm">{ico('coin', 'ico soft')}<p class="small" style="margin:0"><b>Tanpa biaya</b> bagi sekolah; seluruh unit dan perlengkapan dibawa oleh tim.</p></div>
      <div class="card" style="padding:4mm;display:flex;gap:3mm">{ico('shield', 'ico soft')}<p class="small" style="margin:0"><b>Data anonim</b> (tanpa nama), hanya untuk evaluasi program dan penelitian pendidikan.</p></div>
      <div class="card" style="padding:4mm;display:flex;gap:3mm">{ico('hand', 'ico soft')}<p class="small" style="margin:0"><b>Kamera & mikrofon opsional;</b> video gestur diproses di perangkat, tidak direkam.</p></div>
      <div class="card" style="padding:4mm;display:flex;gap:3mm">{ico('star', 'ico soft')}<p class="small" style="margin:0"><b>Publikasi bersama</b> atas persetujuan sekolah; aplikasi tetap dapat dipakai setelah program.</p></div></div>
    <div class="card aura" style="display:flex;gap:5mm;align-items:center">
      <div style="width:30mm;flex:none;background:#fff;border-radius:4mm;padding:2mm">{(B/'qr_survey.svg').read_text()}</div>
      <div><span class="kicker" style="margin-bottom:2mm"><i></i>LANGKAH AWAL</span><h3>Analisis kebutuhan siswa</h3>
        <p class="small" style="margin:0">Sebelum implementasi, siswa mengisi kuesioner singkat (5 pertanyaan, ± 1 menit, anonim) agar materi dan jadwal sesuai kebutuhan kelas. Pindai QR untuk mencoba.</p></div></div>"""))

    # 6 · RENCANA KEGIATAN -----------------------------------------------
    TL = [("H–7", "Koordinasi & analisis kebutuhan", "Penetapan kelas dan guru mitra; siswa mengisi kuesioner online singkat."),
          ("07.00–07.45", "Persiapan ruang", "Pemasangan dan kalibrasi unit hologram; ruang kelas diredupkan."),
          ("07.45–08.00", "Pembukaan & briefing guru", "Pengenalan HALO-XR dan alur kegiatan kepada guru mitra."),
          ("08.00–08.15", "Pretest", "Mengukur pemahaman awal siswa tentang sistem organ."),
          ("08.15–09.15", "Eksplorasi HALO-XR", "Siswa bergiliran per kelompok (3–6 orang per unit) mengamati dan mengendalikan organ 3D dengan gestur dan suara."),
          ("09.15–09.45", "Posttest & kuesioner SUS", "Mengukur pemahaman akhir dan kepuasan pengguna."),
          ("09.45–10.00", "Penutup & dokumentasi", "Refleksi singkat, foto bersama, dan masukan guru."),
          ("H+7", "Laporan hasil", "Laporan N-gain, skor SUS, dan masukan diserahkan ke sekolah.")]
    tl = "".join(f'<div class="tl-item"><span class="when">{w}</span><h3>{h}</h3><p class="small" style="margin:0">{d}</p></div>' for w, h, d in TL)
    P.append(("05", "", True, f"""
    {title('RENCANA KEGIATAN', 'Susunan', 'kegiatan')}
    <div style="display:grid;grid-template-columns:1.05fr 1fr;gap:6mm">
      <div class="card"><div class="tl">{tl}</div>
        <p class="small muted" style="margin:1mm 0 0">Tanggal pelaksanaan: {PH('tanggal disepakati')}. Waktu dapat disesuaikan dengan jadwal pelajaran {nm}.</p></div>
      <div style="display:flex;flex-direction:column;gap:4.5mm">
        <div class="card blue kpi" style="text-align:center;padding:6mm 5mm">
          {ico('star', 'ico white')}<b style="font-size:24pt">± 3 JP</b><span>durasi kegiatan di kelas<br>satu kelas peserta · dipandu Tim HALO-XR</span></div>
        <div class="card"><h3>Skema kerja sama</h3>
          <div style="display:flex;gap:3mm;margin:2.5mm 0"><span class="ico soft" style="width:8mm;height:8mm;flex:none;font-weight:800;color:var(--deep)">A</span><p class="small" style="margin:0"><b>Implementasi 1 hari (tahap ini):</b> tanpa biaya; unit dibawa tim dan aplikasi gratis.</p></div>
          <div style="display:flex;gap:3mm;margin:2.5mm 0"><span class="ico soft" style="width:8mm;height:8mm;flex:none;font-weight:800;color:var(--deep)">B</span><p class="small" style="margin:0"><b>Pengadaan mandiri:</b> sekolah dapat merakit unit sendiri dengan panduan dan dukungan tim.</p></div>
          <div style="display:flex;gap:3mm;margin:2.5mm 0 0"><span class="ico soft" style="width:8mm;height:8mm;flex:none;font-weight:800;color:var(--deep)">C</span><p class="small" style="margin:0"><b>Kolaborasi lanjutan:</b> pengembangan materi bersama guru, ekstrakurikuler, atau riset siswa.</p></div></div>
        <div class="imgcard"><img src="{U('deck/build/media/heart_holo.png')}" style="height:46mm"></div></div></div>"""))

    # 7 · EVALUASI & PENUTUP -------------------------------------------------
    P.append(("06", "", True, f"""
    {title('EVALUASI', 'Indikator', 'keberhasilan')}
    <div class="grid4" style="margin-bottom:6mm">
      <div class="card">{ico('chart')}<h3>Hasil belajar</h3><p class="small" style="margin:0">N-gain pre/posttest, target <b>≥ 0,3</b> (sedang).</p></div>
      <div class="card">{ico('star')}<h3>Kepuasan</h3><p class="small" style="margin:0">Skor System Usability Scale <b>≥ 70</b>.</p></div>
      <div class="card">{ico('gauge')}<h3>Teknis</h3><p class="small" style="margin:0">Akurasi gestur <b>≥ 90%</b>, <b>≥ 30 fps</b>, latensi <b>≤ 150 ms</b>.</p></div>
      <div class="card">{ico('users')}<h3>Keterlibatan</h3><p class="small" style="margin:0">Observasi keaktifan dan masukan guru mitra.</p></div></div>
    <div class="card dark" style="padding:0;overflow:hidden;display:grid;grid-template-columns:1fr 66mm;margin-bottom:6mm">
      <div style="padding:7mm"><span class="kicker" style="background:rgba(255,255,255,.12);color:#BFE3FF;box-shadow:none"><i></i>PENUTUP</span>
        <h2 style="color:#fff;font-size:17pt">Kelas anatomi yang <span style="color:#8CC6FF">hidup dan terjangkau.</span></h2>
        <p class="small" style="margin-top:3mm">HALO-XR lahir dari keyakinan bahwa pembelajaran 3D yang interaktif tidak harus mahal. Dengan dukungan {nm}, kami berharap HALO-XR menjadi contoh nyata teknologi Society 5.0 yang inklusif, higienis, dan berkelanjutan di sekolah. Kami siap mempresentasikan dan mendemonstrasikannya secara langsung.</p></div>
      <img src="{U('deck/build/media/pyramid_brain_holo.png')}" style="width:100%;height:100%;object-fit:cover"></div>
    <div class="card aura" style="display:grid;grid-template-columns:1fr 34mm 34mm;gap:6mm;align-items:center">
      <div><span class="kicker" style="margin-bottom:2mm"><i></i>COBA SEKARANG</span><h3>Lihat HALO-XR secara langsung</h3>
        <p class="small" style="margin:0">Pindai QR untuk membuka aplikasi HALO-XR atau mengisi kuesioner siswa. Aplikasi juga dapat dibuka di <b style="white-space:nowrap">haloxr-id.web.app</b>.</p></div>
      <div style="text-align:center"><div style="background:#fff;border-radius:4mm;padding:2mm">{(B/'qr_app.svg').read_text()}</div><p class="small" style="margin:1.5mm 0 0"><b>Coba aplikasi</b></p></div>
      <div style="text-align:center"><div style="background:#fff;border-radius:4mm;padding:2mm">{(B/'qr_survey.svg').read_text()}</div><p class="small" style="margin:1.5mm 0 0"><b>Kuesioner siswa</b></p></div></div>"""))

    total = len(P)
    body = "".join(page(inner, s, i + 1, total, wm, cls, deco) for i, (wm, cls, deco, inner) in enumerate(P))
    return f"<!doctype html><html lang='id'><head><meta charset='utf-8'><style>{CSS}</style></head><body>{body}</body></html>"


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page()
        for s in SCHOOLS:
            f = B / f"{s['slug']}.html"; f.write_text(build(s), encoding="utf-8")
            await pg.goto(f.as_uri(), wait_until="networkidle"); await pg.wait_for_timeout(500)
            over = await pg.evaluate("""[...document.querySelectorAll('.page:not(.cover)')].map((p)=>{const r=p.getBoundingClientRect();
              const kids=[...p.children].filter(e=>getComputedStyle(e).position!=='absolute');
              const bottom=Math.max(...kids.map(e=>e.getBoundingClientRect().bottom));return bottom>r.bottom-18*3.78?[...document.querySelectorAll('.page')].indexOf(p)+1:null}).filter(Boolean)""")
            out = OUT / f"Proposal_Kemitraan_HALO-XR_{s['slug']}.pdf"
            await pg.pdf(path=str(out), format="A4", print_background=True, prefer_css_page_size=True)
            print(out.name, "| halaman meluber:", over or "tidak ada")
        await b.close()

asyncio.run(main())
