/* HALO-XR · sense.js — kontrol tanpa sensor tambahan: gestur lewat kamera bawaan (MediaPipe, di perangkat)
 * dan perintah suara (Web Speech API). Keduanya memanggil onGesture(nama) dengan 9 nama yang sama seperti sensor PAJ7620U2,
 * plus onCommand({type, ...}) untuk perintah suara yang lebih kaya (pilih organ, gaya, piramida).
 */

/* =================================================================== KAMERA === */
const MP = new URL("../vendor/mediapipe/", import.meta.url).href;
const COOLDOWN = 750;      // ms setelah satu gestur terpicu
const WIN = 420;           // jendela usapan (ms)

export class CameraGestures {
  constructor({ onGesture, onStatus, onFrame }) {
    this.onGesture = onGesture; this.onStatus = onStatus; this.onFrame = onFrame;
    this.hist = []; this.ang = []; this.last = 0; this.hold = { name: "", t: 0, fired: false };
    this.running = false;
  }

  async start(video, canvas) {
    if (this.running) return;
    this.video = video; this.canvas = canvas; this.ctx = canvas?.getContext("2d");
    this.onStatus?.("loading");
    if (!this.recognizer) {
      const { FilesetResolver, GestureRecognizer } = await import(MP + "vision_bundle.mjs");
      const fs = await FilesetResolver.forVisionTasks(MP + "wasm");
      const opts = (delegate) => ({ baseOptions: { modelAssetPath: MP + "gesture_recognizer.task", delegate }, runningMode: "VIDEO", numHands: 1,
        minHandDetectionConfidence: 0.6, minHandPresenceConfidence: 0.6, minTrackingConfidence: 0.5 });
      try { this.recognizer = await GestureRecognizer.createFromOptions(fs, opts("GPU")); }
      catch { this.recognizer = await GestureRecognizer.createFromOptions(fs, opts("CPU")); }
    }
    this.stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "user", width: { ideal: 640 }, height: { ideal: 480 } }, audio: false });
    video.srcObject = this.stream; video.muted = true; video.playsInline = true;
    await video.play();
    this.running = true; this.onStatus?.("on");
    const loop = () => {
      if (!this.running) return;
      if (video.readyState >= 2 && video.currentTime !== this.vt) { this.vt = video.currentTime; this._detect(performance.now()); }
      this.raf = requestAnimationFrame(loop);
    };
    loop();
  }

  stop() {
    this.running = false; cancelAnimationFrame(this.raf);
    this.stream?.getTracks().forEach((t) => t.stop()); this.stream = null;
    if (this.video) this.video.srcObject = null;
    this.ctx?.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.onStatus?.("off");
  }

  _fire(name, now) {
    this.last = now; this.hist = []; this.ang = [];
    this.onGesture?.(name);
  }

  _detect(now) {
    const r = this.recognizer.recognizeForVideo(this.video, now);
    const lm = r.landmarks?.[0];
    const cat = r.gestures?.[0]?.[0];
    const name = cat && cat.score > 0.6 ? cat.categoryName : "None";
    this._draw(lm, name);
    this.onFrame?.(lm ? name : null);
    if (!lm) { this.hist = []; this.ang = []; this.hold = { name: "", t: 0, fired: false }; return; }
    if (now - this.last < COOLDOWN) return;

    // Koordinat dicerminkan agar kanan pengguna = kanan layar.
    const P = (i) => ({ x: 1 - lm[i].x, y: lm[i].y });
    const palm = P(9), wrist = P(0), tip = P(8);
    const size = Math.hypot(palm.x - wrist.x, palm.y - wrist.y);
    this.hist.push({ t: now, x: palm.x, y: palm.y, s: size, name });
    while (this.hist.length && now - this.hist[0].t > 1300) this.hist.shift();

    // 1) Gestur statis yang ditahan ± 0,7 detik
    const STATIC = { Thumb_Up: "wave", Closed_Fist: "reset", Victory: "style" };
    if (STATIC[name]) {
      if (this.hold.name !== name) this.hold = { name, t: now, fired: false };
      else if (!this.hold.fired && now - this.hold.t > 700) { this.hold.fired = true; return this._fire(STATIC[name], now); }
    } else this.hold = { name: "", t: 0, fired: false };

    // 2) Lingkaran dengan telunjuk (Pointing_Up) → putar searah / berlawanan
    if (name === "Pointing_Up") {
      this.ang.push({ t: now, x: tip.x, y: tip.y });
      while (this.ang.length && now - this.ang[0].t > 1500) this.ang.shift();
      if (this.ang.length > 10) {
        const cx = this.ang.reduce((a, p) => a + p.x, 0) / this.ang.length, cy = this.ang.reduce((a, p) => a + p.y, 0) / this.ang.length;
        let sum = 0, rad = 0;
        for (let i = 1; i < this.ang.length; i++) {
          const a0 = Math.atan2(this.ang[i - 1].y - cy, this.ang[i - 1].x - cx), a1 = Math.atan2(this.ang[i].y - cy, this.ang[i].x - cx);
          let d = a1 - a0; d = Math.atan2(Math.sin(d), Math.cos(d)); sum += d;
          rad += Math.hypot(this.ang[i].x - cx, this.ang[i].y - cy);
        }
        rad /= this.ang.length;
        // sumbu y gambar mengarah ke bawah: sudut bertambah = searah jarum jam di layar
        if (rad > 0.03 && Math.abs(sum) > Math.PI * 1.6) return this._fire(sum > 0 ? "cw" : "ccw", now);
      }
      return;
    }
    this.ang = [];

    // 3) Lambaian: ≥ 3 kali balik arah horizontal dalam 1,3 detik
    const xs = this.hist.map((h) => h.x);
    let flips = 0, dir = 0, ext = xs[0];
    for (let i = 1; i < xs.length; i++) {
      const d = xs[i] - ext;
      if (Math.abs(d) > 0.045) { const nd = Math.sign(d); if (dir && nd !== dir) flips++; dir = nd; ext = xs[i]; }
      else if ((dir > 0 && xs[i] > ext) || (dir < 0 && xs[i] < ext)) ext = xs[i];
    }
    if (flips >= 3 && name === "Open_Palm") return this._fire("wave", now);

    // 4) Usapan & dorong/tarik dalam jendela pendek
    const w = this.hist.filter((h) => now - h.t <= WIN);
    if (w.length < 4) return;
    const a = w[0], b = w[w.length - 1];
    const dx = b.x - a.x, dy = b.y - a.y, ratio = b.s / a.s;
    if (Math.abs(dx) > 0.22 && Math.abs(dx) > 1.8 * Math.abs(dy)) return this._fire(dx > 0 ? "right" : "left", now);
    if (Math.abs(dy) > 0.2 && Math.abs(dy) > 1.8 * Math.abs(dx)) return this._fire(dy < 0 ? "up" : "down", now);
    if (ratio > 1.35) return this._fire("forward", now);
    if (ratio < 0.72) return this._fire("backward", now);
  }

  _draw(lm, name) {
    const c = this.canvas, x = this.ctx; if (!x) return;
    const W = (c.width = c.clientWidth * devicePixelRatio), H = (c.height = c.clientHeight * devicePixelRatio);
    x.clearRect(0, 0, W, H);
    if (!lm) return;
    const E = [[0, 1], [1, 2], [2, 3], [3, 4], [0, 5], [5, 6], [6, 7], [7, 8], [5, 9], [9, 10], [10, 11], [11, 12], [9, 13], [13, 14], [14, 15], [15, 16], [13, 17], [0, 17], [17, 18], [18, 19], [19, 20]];
    const px = (p) => [(1 - p.x) * W, p.y * H];
    x.lineWidth = 2 * devicePixelRatio; x.strokeStyle = "rgba(140,198,255,.9)";
    x.beginPath(); for (const [i, j] of E) { const [a1, b1] = px(lm[i]), [a2, b2] = px(lm[j]); x.moveTo(a1, b1); x.lineTo(a2, b2); } x.stroke();
    x.fillStyle = "#2F7BFF"; for (const p of lm) { const [a1, b1] = px(p); x.beginPath(); x.arc(a1, b1, 3 * devicePixelRatio, 0, 7); x.fill(); }
    if (name !== "None") { x.font = `700 ${12 * devicePixelRatio}px sans-serif`; x.fillStyle = "#fff"; x.fillText(name.replace("_", " "), 8 * devicePixelRatio, 18 * devicePixelRatio); }
  }
}

/* ==================================================================== SUARA === */
const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
export const voiceSupported = !!SR;

// Kata kunci → aksi. Urutan penting: frasa panjang diperiksa dulu (mis. "bilik kiri" sebelum "kiri").
const ACTIONS = [
  [/\b(keluar|exit|tutup piramida|close)\b/, { type: "exitPyramid" }],
  [/\b(piramida|pyramid|mode hologram penuh)\b/, { type: "pyramid" }],
  [/\b(gaya hologram|mode hologram|hologram)\b/, { type: "style", value: "holo" }],
  [/\b(realistis|realistic|asli|nyata)\b/, { type: "style", value: "real" }],
  [/\b(reset|ulang|kembali ke awal|atur ulang)\b/, { type: "reset" }],
  [/\b(kupas|buka lapisan|potong|irisan|peel|cut)\b/, { type: "gesture", value: "cw" }],
  [/\b(kembalikan|tutup lapisan|utuh|restore)\b/, { type: "gesture", value: "ccw" }],
  [/\b(perbesar|zoom in|dekatkan|besar|bigger)\b/, { type: "gesture", value: "forward" }],
  [/\b(perkecil|zoom out|jauhkan|kecil|smaller)\b/, { type: "gesture", value: "backward" }],
  [/\b(berikutnya|selanjutnya|lanjut|next)\b/, { type: "gesture", value: "wave" }],
  [/\b(kiri|left)\b/, { type: "gesture", value: "left" }],
  [/\b(kanan|right)\b/, { type: "gesture", value: "right" }],
  [/\b(atas|naik|up)\b/, { type: "gesture", value: "up" }],
  [/\b(bawah|turun|down)\b/, { type: "gesture", value: "down" }],
];
const ORGAN_WORDS = {
  heart: ["jantung", "heart"], brain: ["otak", "brain"], lungs: ["paru", "lung"], liver: ["hati", "liver"], kidneys: ["ginjal", "kidney"],
  eyeball: ["mata", "eye", "eyeball"], intestine: ["usus", "intestine"], pancreas: ["pankreas", "pancreas"], skin: ["kulit", "skin"], cell: ["sel", "cell"],
};

/** Ubah transkrip menjadi daftar perintah. structures = [{i, label}] untuk organ aktif (mis. "Aorta", "Bilik kiri"). */
export function parseCommand(text, structures = []) {
  const t = " " + text.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "").replace(/[^a-z0-9 ]/g, " ") + " ";
  const out = [];
  // 1) nama struktur organ aktif (frasa paling panjang menang)
  const st = [...structures].sort((a, b) => b.label.length - a.label.length).find((s) => t.includes(" " + s.label.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "") + " "));
  let rest = t;
  if (st) { out.push({ type: "focus", value: st.i }); rest = t.replace(st.label.toLowerCase(), " "); }
  // 2) nama organ
  for (const [id, words] of Object.entries(ORGAN_WORDS)) {
    const re = new RegExp(`\\b(${words.join("|")})(s|nya)?\\b`, "g");
    if (re.test(rest)) { out.push({ type: "organ", value: id }); rest = rest.replace(re, " "); break; }
  }
  // 3) aksi
  for (const [re, cmd] of ACTIONS) if (re.test(rest)) { out.push(cmd); break; }
  return out;
}

export class VoiceCommands {
  constructor({ onCommand, onStatus, onHeard, getStructures }) {
    Object.assign(this, { onCommand, onStatus, onHeard, getStructures });
    this.enabled = false; this.lang = "id-ID"; this.wake = false;
  }
  start(lang) {
    if (!SR) { this.onStatus?.("unsupported"); return; }
    this.lang = lang === "en" ? "en-US" : "id-ID";
    this.enabled = true; this._run();
  }
  setLang(lang) { this.lang = lang === "en" ? "en-US" : "id-ID"; if (this.enabled) { this.rec?.abort(); } }
  stop() { this.enabled = false; this.rec?.abort(); this.onStatus?.("off"); }
  _run() {
    const rec = (this.rec = new SR());
    rec.lang = this.lang; rec.continuous = true; rec.interimResults = false; rec.maxAlternatives = 3;
    rec.onstart = () => this.onStatus?.("on");
    rec.onresult = (e) => {
      for (let i = e.resultIndex; i < e.results.length; i++) {
        if (!e.results[i].isFinal) continue;
        const alts = [...e.results[i]].map((a) => a.transcript.trim());
        let text = alts[0];
        if (this.wake && !/\bhalo\b|\bhello\b/i.test(text)) { this.onHeard?.(text, []); continue; }
        // pakai alternatif pertama yang menghasilkan perintah
        let cmds = [];
        for (const a of alts) { cmds = parseCommand(a, this.getStructures?.() || []); if (cmds.length) { text = a; break; } }
        this.onHeard?.(text, cmds);
        cmds.forEach((c) => this.onCommand?.(c));
      }
    };
    rec.onerror = (e) => {
      if (e.error === "not-allowed" || e.error === "service-not-allowed") { this.enabled = false; this.onStatus?.("denied"); }
      else if (e.error === "network") this.onStatus?.("network");
    };
    rec.onend = () => { if (this.enabled) setTimeout(() => this.enabled && this._run(), 250); else this.onStatus?.("off"); };
    try { rec.start(); } catch {}
  }
}
