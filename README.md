# HALO-XR · Hologram Anatomi Interaktif

Web app (HTML, CSS, dan JS native tanpa framework) untuk hologram piramida Pepper's Ghost dengan kontrol gestur tanpa sentuh (ESP32 + PAJ7620U2). Gaya visualnya neumorphism putih-biru. Paket ini juga berisi deck presentasi yang didesain ulang dari `HALO-XR Interactive Anatomy Hologram.pdf`.

## Menjalankan
```
start.cmd                 # atau: python serve.py 8000  → http://localhost:8000
```
App harus dibuka lewat server, bukan `file://`, agar model GLB bisa dimuat. `serve.py` memaksa MIME `.js` yang benar karena registry Windows sering memetakannya ke `text/plain`.

Parameter URL: `?demo` (gestur simulasi), `?pyramid` (langsung masuk mode piramida), `?organ=brain`, `?lang=en`, `?screen=viewer`.
Keyboard: panah = putar/miring · `+`/`-` = zoom · `]`/`[` = kupas/kembalikan · spasi = organ berikutnya · `P` = mode piramida · `Esc` = keluar.

## Kontrol tanpa sensor tambahan (kamera & mikrofon bawaan)
Aktifkan di layar **Perangkat → Kontrol bawaan perangkat**, atau lewat tombol kamera/mikrofon di viewer dan mode piramida. Keduanya butuh HTTPS atau localhost.
- **Gestur kamera:** MediaPipe Gesture Recognizer (WASM, berjalan di perangkat) dengan file lokal di `vendor/mediapipe`. Gerakan dinamis: usap kiri/kanan/atas/bawah, dorong/tarik telapak, lingkaran telunjuk (kupas/kembalikan), lambaian. Gestur statis yang ditahan: 👍 organ berikutnya, ✊ reset, ✌ ganti gaya.
- **Perintah suara:** Web Speech API (Chrome/Edge; Safari iOS terbatas; Firefox tidak didukung), `id-ID`/`en-US` mengikuti bahasa app. Contoh perintah: "putar ke kiri", "perbesar", "kupas", "tampilkan otak", "bilik kiri", "mode hologram", "piramida", "keluar". Bisa memakai kata pemicu "Halo". Audio diproses layanan Google, jadi butuh internet.
- Kalibrasi ambang gestur ada di `js/sense.js` (`COOLDOWN`, `WIN`, ambang usapan 0,22, rasio dorong 1,35/0,72).

## Kuesioner analisis kebutuhan
- **Siswa:** `kuesioner.html` berisi 5 pertanyaan anonim, satu per layar, dalam ID/EN. Jawaban disimpan ke Realtime Database `responses/`.
- **Admin:** `admin.html` memakai login Google. Isinya data live, grafik per pertanyaan, filter sekolah/kelas, ekspor CSV, serta link, QR, dan tombol WhatsApp untuk dibagikan.
- **Keamanan:** diatur di `database.rules.json`. Publik hanya bisa *menambah* jawaban yang valid; membaca dan menghapus hanya untuk email admin. Jika daftar admin berubah, ubah `database.rules.json` **dan** `ADMINS` di `js/firebase.js`.
- **Uji lokal:** jalankan `firebase emulators:start --only database,auth` (butuh Java 21), lalu buka `kuesioner.html?emu` / `admin.html?emu`.

## Struktur
| Path | Isi |
|---|---|
| `index.html`, `css/style.css` | 5 layar (Beranda, Anatomi, Hologram, Kelas, Perangkat), design token AQUENT |
| `js/viewer.js` | Renderer three.js: gaya realistis/hologram (shader fresnel), kupas irisan (clipping plane + warna jaringan dalam), hotspot, **mode piramida 4 tampilan** (atlas 2×2 → canvas 2D, diputar per sisi dan dicerminkan) |
| `js/app.js` | Navigasi, router 9 gestur (BLE/pad/keyboard/demo), Web Bluetooth (Nordic UART), kuis pre/post-test + N-gain, kalibrasi |
| `js/sense.js` | Gestur kamera (MediaPipe) + perintah suara (Web Speech) → 9 aksi yang sama dengan sensor |
| `js/holo.js` | Geometri prosedural model sel hewan berlapis (membran → RE/Golgi → mitokondria → nukleus) |
| `js/organs.js`, `js/organs-{id,en}.js` | Registri 10 model + hotspot, materi organ ID/EN |
| `js/i18n.js` | Teks UI ID/EN, bank soal |
| `assets/models`, `assets/anatomy` | 9 GLB organ + ilustrasi (dari repo anatomy) |
| `vendor/three` | three.js r185 lokal (bisa offline) |
| `firmware/halo_xr_esp32` | Sketsa Arduino ESP32 + PAJ7620U2 → BLE UART (`UP`, `CW`, `WAVE`, …) |
| `deck/` | `shots.py` (aset dari app via Playwright), `build_deck.py [en\|id]`, `export.py` (PDF/PNG via PowerPoint) |
| `output/` | `HALO-XR_Deck_Neumorph_{EN,ID}.pptx/.pdf` |

## Membangun ulang deck
```
python serve.py 8766            # terminal terpisah
python deck/shots.py http://localhost:8766 en
python deck/shots.py http://localhost:8766 id
python deck/build_deck.py en && python deck/export.py output/HALO-XR_Deck_Neumorph_EN.pptx
python deck/build_deck.py id && python deck/export.py output/HALO-XR_Deck_Neumorph_ID.pptx
```

## Asumsi & yang belum selesai
- **Lisensi aset:** model 3D, ilustrasi, dan materi organ diambil dari github.com/thebuggeddev/anatomy. Repo itu **tidak punya file LICENSE**. Mintalah izin pemiliknya sebelum dipublikasikan atau dilombakan.
- **Firmware belum diuji di perangkat fisik.** Orientasi arah gestur mungkin perlu ditukar sesuai pemasangan sensor.
- **Latensi di app** hanya mengukur sisi aplikasi (gestur diterima → frame tergambar). Angka 108,3 ms dan Rp265.000 di deck berasal dari PDF asli.
- **Data deck:** nilai pre/post 40 → 80 di mockup ponsel hanyalah contoh tampilan (ditandai "Sample values shown"). Tahap Implementasi dan Evaluasi ADDIE ditandai "NEXT".
- **Font deck** memakai Segoe UI karena Plus Jakarta Sans belum terpasang di PC ini. App memuat Plus Jakarta Sans dari Google Fonts.
- **Email** `partnership@halo-xr.edu.id` disalin dari PDF dan belum diverifikasi.
