/* HALO-XR · survey.js — kuesioner siswa (anonim, 5 pertanyaan, satu per layar). */
import { db } from "./firebase.js";
import { ref, push, serverTimestamp } from "https://www.gstatic.com/firebasejs/13.0.0/firebase-database.js";
import { QUESTIONS, PROFILE } from "./survey-data.js";

const $ = (s) => document.querySelector(s);
const store = {
  get(k, d) { try { const v = localStorage.getItem("haloxr.survey." + k); return v === null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem("haloxr.survey." + k, JSON.stringify(v)); } catch {} },
};
const params = new URLSearchParams(location.search);

const T = {
  id: {
    sub: "Kuesioner analisis kebutuhan", chip: "± 1 MENIT · ANONIM",
    t1: "Bantu kami membuat", t2: "kelas anatomi lebih seru.",
    desc: "Ada 5 pertanyaan singkat tentang cara kamu belajar anatomi. Tidak perlu menulis nama, dan tidak ada jawaban benar atau salah.",
    profile: "Boleh isi (opsional)", start: "Mulai", back: "Kembali", of: "dari", q: "Pertanyaan",
    sending: "Mengirim jawaban…", thanks1: "Terima kasih!", thanks2: "Jawabanmu sudah tercatat.",
    thanksDesc: "Masukanmu membantu tim HALO-XR menyiapkan hologram anatomi yang cocok untuk kelasmu.",
    offline: "Kamu sedang offline. Jawaban akan terkirim otomatis saat internet tersambung kembali.",
    tryApp: "Coba aplikasi HALO-XR", again: "Isi lagi (perangkat lain / teman)", done: "Kamu sudah mengisi kuesioner ini di perangkat ini.",
    error: "Gagal mengirim. Periksa koneksi lalu coba lagi.", retry: "Coba lagi",
  },
  en: {
    sub: "Needs-analysis survey", chip: "≈ 1 MINUTE · ANONYMOUS",
    t1: "Help us make", t2: "anatomy class more fun.",
    desc: "There are 5 short questions about how you learn anatomy. No names needed, and there are no right or wrong answers.",
    profile: "Optional", start: "Start", back: "Back", of: "of", q: "Question",
    sending: "Sending your answers…", thanks1: "Thank you!", thanks2: "Your answers are saved.",
    thanksDesc: "Your feedback helps the HALO-XR team build an anatomy hologram that fits your class.",
    offline: "You're offline. Your answers will be sent automatically when you're back online.",
    tryApp: "Try the HALO-XR app", again: "Fill in again (another device / friend)", done: "You've already filled in this survey on this device.",
    error: "Couldn't send. Check your connection and try again.", retry: "Try again",
  },
};
const S = { lang: params.get("lang") || store.get("lang", "id"), step: -1, ans: {}, profile: {} };
const L = () => T[S.lang];

function render() {
  document.documentElement.lang = S.lang;
  $("#langBtn").textContent = S.lang.toUpperCase();
  $("#brandSub").textContent = L().sub;
  if (S.step === -1) return intro();
  if (S.step < QUESTIONS.length) return question(S.step);
}

function intro() {
  const prof = Object.entries(PROFILE).map(([k, p]) => `
    <div class="prof"><span class="label">${p[S.lang]}</span><div class="chips">${p.options.map((o) =>
      `<button type="button" data-prof="${k}" data-v="${o.v}" class="${S.profile[k] === o.v ? "on" : ""}">${o[S.lang]}</button>`).join("")}</div></div>`).join("");
  const already = store.get("submitted", false) && !params.has("again");
  $("#view").innerHTML = `
    <section class="screen active">
      <div class="head"><span class="chip">${L().chip}</span>
        <h1>${L().t1}<br><span class="grad-text">${L().t2}</span></h1>
        <p class="desc">${L().desc}</p></div>
      ${already ? `<div class="card soft-note">${L().done}</div>` : ""}
      <div class="card"><h3>${L().profile}</h3>${prof}</div>
      <button class="btn-primary big" id="startBtn">${L().start} →</button>
    </section>`;
  $("#startBtn").onclick = () => { S.step = 0; render(); };
}

function question(i) {
  const q = QUESTIONS[i], cur = S.ans[q.key];
  $("#view").innerHTML = `
    <section class="screen active">
      <div class="q-progress"><span class="muted small">${L().q} ${i + 1} ${L().of} ${QUESTIONS.length}</span>
        <div class="q-bar"><i style="width:${(i / QUESTIONS.length) * 100}%"></i></div></div>
      <div class="card hero qcard">
        <span class="chip">${String(i + 1).padStart(2, "0")}</span>
        <h2 class="q-title">${q[S.lang]}</h2>
        <div class="answers ${q.type}">${q.options.map((o) =>
          `<button type="button" class="ans ${cur === o.v ? "on" : ""}" data-v="${o.v}"><span class="emo" aria-hidden="true">${o.e}</span><span>${o[S.lang]}</span></button>`).join("")}</div>
      </div>
      <div class="row nav-row"><button class="btn" id="backBtn">← ${L().back}</button></div>
    </section>`;
  requestAnimationFrame(() => { const b = $(".q-bar i"); if (b) b.style.width = `${((i + (cur !== undefined ? 1 : 0)) / QUESTIONS.length) * 100}%`; });
  $("#backBtn").onclick = () => { S.step--; render(); };
  document.querySelectorAll(".ans").forEach((b) => b.onclick = () => {
    const raw = b.dataset.v; S.ans[q.key] = q.type === "scale" ? +raw : raw;
    document.querySelectorAll(".ans").forEach((x) => x.classList.toggle("on", x === b));
    $(".q-bar i").style.width = `${((i + 1) / QUESTIONS.length) * 100}%`;
    setTimeout(() => { if (i < QUESTIONS.length - 1) { S.step++; render(); } else submit(); }, 280);
  });
}

async function submit() {
  $("#view").innerHTML = `<section class="screen active center"><div class="spinner"></div><p class="muted">${L().sending}</p></section>`;
  const data = { ...S.ans, lang: S.lang, ts: serverTimestamp() };
  if (S.profile.grade) data.grade = S.profile.grade;
  if (S.profile.school) data.school = S.profile.school;
  const p = push(ref(db, "responses"), data);
  // Saat offline, SDK mengantre penulisan; tampilkan terima kasih tanpa menunggu lama.
  const offlineNote = setTimeout(() => thanks(true), 4000);
  try { await p; clearTimeout(offlineNote); store.set("submitted", true); thanks(false); }
  catch (e) {
    clearTimeout(offlineNote); console.error(e);
    $("#view").innerHTML = `<section class="screen active center"><p class="desc">${L().error}</p><button class="btn-primary" id="retry">${L().retry}</button></section>`;
    $("#retry").onclick = submit;
  }
}

function thanks(pending) {
  $("#view").innerHTML = `
    <section class="screen active center">
      <div class="done-badge"><svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg></div>
      <h1>${L().thanks1}<br><span class="grad-text">${L().thanks2}</span></h1>
      <p class="desc">${L().thanksDesc}</p>
      ${pending ? `<div class="card soft-note">${L().offline}</div>` : ""}
      <a class="btn-primary big" href="./">${L().tryApp}</a>
      <button class="btn ghost" id="againBtn">${L().again}</button>
    </section>`;
  $("#againBtn").onclick = () => { S.ans = {}; S.step = 0; render(); };
}

document.addEventListener("click", (e) => {
  const b = e.target.closest("[data-prof]"); if (!b) return;
  const k = b.dataset.prof; S.profile[k] = S.profile[k] === b.dataset.v ? undefined : b.dataset.v;
  b.parentElement.querySelectorAll("button").forEach((x) => x.classList.toggle("on", S.profile[k] === x.dataset.v));
});
$("#langBtn").onclick = () => { S.lang = S.lang === "id" ? "en" : "id"; store.set("lang", S.lang); render(); };
render();
