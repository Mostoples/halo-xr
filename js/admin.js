/* HALO-XR · admin.js — dasbor kuesioner (login username/password atau Google, data live, grafik, filter, CSV, QR). */
import { app, db, ADMINS, ADMIN_UID, ADMIN_DOMAIN, EMU } from "./firebase.js";
import { ref, onValue, query, orderByChild } from "https://www.gstatic.com/firebasejs/13.0.0/firebase-database.js";
import { getAuth, GoogleAuthProvider, signInWithPopup, signInWithRedirect, onAuthStateChanged, signOut, connectAuthEmulator, signInWithCredential, signInWithEmailAndPassword, updatePassword, browserSessionPersistence, setPersistence } from "https://www.gstatic.com/firebasejs/13.0.0/firebase-auth.js";
import { QUESTIONS, PROFILE, label, SURVEY_URL } from "./survey-data.js";

const $ = (s) => document.querySelector(s);
const auth = getAuth(app);
if (EMU) {
  connectAuthEmulator(auth, "http://127.0.0.1:9099", { disableWarnings: true });
  // hanya untuk uji emulator: login Google palsu dengan email tertentu
  window.__emuLogin = (email) => signInWithCredential(auth, GoogleAuthProvider.credential(JSON.stringify({ sub: email, email, email_verified: true })));
}
const LANG = "id";
let all = [], unsub = null;
const F = { school: "all", grade: "all" };

/* ---------- auth ---------- */
function show(view) { ["loginView", "dashView"].forEach((v) => $("#" + v).classList.toggle("active", v === view)); }
// Username tanpa "@" dipetakan ke akun Firebase Auth: admin → admin@haloxr-id.web.app
const toEmail = (u) => (u.includes("@") ? u : `${u}@${ADMIN_DOMAIN}`);
const isAdmin = (u) => u.uid === ADMIN_UID || (u.emailVerified && ADMINS.includes(u.email));
// Sesi hanya bertahan selama tab terbuka (aman untuk komputer bersama di sekolah)
setPersistence(auth, browserSessionPersistence).catch(() => {});

$("#loginForm").onsubmit = async (e) => {
  e.preventDefault();
  const btn = $("#pwBtn"); btn.disabled = true; $("#loginMsg").textContent = "";
  try { await signInWithEmailAndPassword(auth, toEmail($("#user").value.trim().toLowerCase()), $("#pass").value); }
  catch (err) {
    $("#loginMsg").textContent = ["auth/invalid-credential", "auth/wrong-password", "auth/user-not-found", "auth/invalid-email"].includes(err.code)
      ? "Username atau password salah." : err.code === "auth/too-many-requests" ? "Terlalu banyak percobaan. Tunggu beberapa menit." : "Gagal masuk: " + (err.code || err.message);
  } finally { btn.disabled = false; }
};
$("#loginBtn").onclick = async () => {
  const provider = new GoogleAuthProvider(); provider.setCustomParameters({ prompt: "select_account" });
  $("#loginMsg").textContent = "";
  try { await signInWithPopup(auth, provider); }
  catch (e) {
    if (e.code === "auth/popup-blocked" || e.code === "auth/cancelled-popup-request") return signInWithRedirect(auth, provider);
    $("#loginMsg").textContent = e.code === "auth/operation-not-allowed" || e.code === "auth/configuration-not-found"
      ? "Login Google belum diaktifkan di Firebase Console (Authentication → Sign-in method → Google)."
      : "Gagal masuk: " + (e.code || e.message);
  }
};
$("#logoutBtn").onclick = () => signOut(auth);

onAuthStateChanged(auth, (user) => {
  unsub?.(); unsub = null;
  $("#who").hidden = $("#logoutBtn").hidden = !user;
  if (!user) { show("loginView"); return; }
  $("#whoText").textContent = user.uid === ADMIN_UID ? "admin" : user.email;
  $("#pwOpen").hidden = !user.providerData.some((p) => p.providerId === "password");
  if (!isAdmin(user)) {
    show("loginView");
    $("#loginMsg").innerHTML = `Akun <b>${user.email}</b> bukan admin. Keluar lalu masuk dengan akun admin.`;
    return;
  }
  $("#who").classList.add("on");
  show("dashView");
  unsub = onValue(query(ref(db, "responses"), orderByChild("ts")), (snap) => {
    all = []; snap.forEach((c) => { all.push({ id: c.key, ...c.val() }); });
    all.reverse(); render();
  }, (err) => { show("loginView"); $("#loginMsg").textContent = "Akses ditolak oleh aturan database: " + err.message; });
});

/* ---------- ganti password ---------- */
$("#pwOpen").onclick = () => { $("#pwCard").hidden = !$("#pwCard").hidden; $("#pwMsg").textContent = ""; };
$("#pwForm").onsubmit = async (e) => {
  e.preventDefault();
  const a = $("#pw1").value, b = $("#pw2").value;
  if (a.length < 8) return ($("#pwMsg").textContent = "Minimal 8 karakter.");
  if (a !== b) return ($("#pwMsg").textContent = "Kedua password tidak sama.");
  try { await updatePassword(auth.currentUser, a); $("#pwCard").hidden = true; e.target.reset(); toast("Password berhasil diganti"); }
  catch (err) { $("#pwMsg").textContent = err.code === "auth/requires-recent-login" ? "Keluar lalu masuk lagi, kemudian ulangi." : "Gagal: " + (err.code || err.message); }
};

/* ---------- bagikan ---------- */
$("#shareUrl").textContent = SURVEY_URL.replace("https://", "");
$("#copyBtn").onclick = async () => { try { await navigator.clipboard.writeText(SURVEY_URL); toast("Link disalin"); } catch { prompt("Salin link:", SURVEY_URL); } };
$("#waBtn").href = "https://wa.me/?text=" + encodeURIComponent("Halo! Bantu isi kuesioner singkat HALO-XR tentang belajar anatomi (± 1 menit, anonim): " + SURVEY_URL);
const qr = qrcode(0, "M"); qr.addData(SURVEY_URL); qr.make();
$("#qr").innerHTML = qr.createSvgTag({ cellSize: 5, margin: 2, scalable: true });
$("#qrBtn").onclick = () => {
  const n = qr.getModuleCount(), cell = 16, m = 4, size = (n + m * 2) * cell, c = document.createElement("canvas");
  c.width = c.height = size; const x = c.getContext("2d"); x.fillStyle = "#fff"; x.fillRect(0, 0, size, size); x.fillStyle = "#16233F";
  for (let r = 0; r < n; r++) for (let k = 0; k < n; k++) if (qr.isDark(r, k)) x.fillRect((k + m) * cell, (r + m) * cell, cell, cell);
  const a = document.createElement("a"); a.download = "kuesioner-haloxr-qr.png"; a.href = c.toDataURL("image/png"); a.click();
};

/* ---------- filter ---------- */
function filters() {
  const mk = (key, el) => {
    const opts = [{ v: "all", id: "Semua" }, ...PROFILE[key].options, { v: "none", id: "Tidak diisi" }];
    $(el).innerHTML = opts.map((o) => `<button data-f="${key}" data-v="${o.v}" class="${F[key] === o.v ? "on" : ""}">${o.id}</button>`).join("");
  };
  mk("school", "#fSchool"); mk("grade", "#fGrade");
}
document.addEventListener("click", (e) => {
  const b = e.target.closest("[data-f]"); if (!b) return;
  F[b.dataset.f] = b.dataset.v; render();
});
const rows = () => all.filter((r) => ["school", "grade"].every((k) => F[k] === "all" || (F[k] === "none" ? !r[k] : r[k] === F[k])));

/* ---------- render ---------- */
const pct = (a, b) => (b ? Math.round((a / b) * 100) : 0);
const mean = (xs) => (xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : null);
const fmt = (v) => (v === null ? "—" : v.toFixed(2).replace(".", ","));

function render() {
  filters();
  const R = rows(), n = R.length;
  const today = new Date().toDateString();
  $("#kTotal").textContent = n;
  $("#kToday").textContent = `${R.filter((r) => r.ts && new Date(r.ts).toDateString() === today).length} hari ini${n !== all.length ? ` · total semua ${all.length}` : ""}`;
  $("#kQ1").textContent = fmt(mean(R.map((r) => r.q1)));
  $("#kQ4").textContent = fmt(mean(R.map((r) => r.q4)));
  $("#kQ4b").textContent = `${pct(R.filter((r) => r.q4 >= 4).length, n)}% tertarik / sangat tertarik`;
  $("#kQ3").textContent = n ? pct(R.filter((r) => r.q3 === "never").length, n) + "%" : "—";

  $("#charts").innerHTML = QUESTIONS.map((q, i) => {
    const counts = q.options.map((o) => ({ o, c: R.filter((r) => r[q.key] === o.v).length }));
    const max = Math.max(1, ...counts.map((x) => x.c));
    const top = [...counts].sort((a, b) => b.c - a.c)[0];
    const m = q.type === "scale" ? mean(R.map((r) => r[q.key])) : null;
    return `<div class="card chart">
      <div class="chart-head"><span class="chip">${String(i + 1).padStart(2, "0")}</span>
        <span class="muted small">${q.type === "scale" ? `rata-rata <b>${fmt(m)}</b>` : n ? `terbanyak: <b>${top.o.id}</b>` : ""}</span></div>
      <h3>${q.id}</h3>
      <div class="bars">${counts.map(({ o, c }) => `
        <div class="bar-row" data-tip="${o.id}: ${c} responden (${pct(c, n)}%)">
          <span class="bar-label"><span aria-hidden="true">${o.e}</span> ${o.id}</span>
          <span class="bar-track"><i style="width:${(c / max) * 100}%"></i></span>
          <span class="bar-val">${pct(c, n)}%<small> · ${c}</small></span>
        </div>`).join("")}</div>
    </div>`;
  }).join("");

  const cols = ["Waktu", "Sekolah", "Kelas", ...QUESTIONS.map((q, i) => "P" + (i + 1))];
  $("#thead").innerHTML = `<tr>${cols.map((c) => `<th>${c}</th>`).join("")}</tr>`;
  $("#tbody").innerHTML = R.slice(0, 100).map((r) => `<tr>
    <td>${r.ts ? new Date(r.ts).toLocaleString("id-ID", { dateStyle: "short", timeStyle: "short" }) : "…"}</td>
    <td>${r.school ? label(PROFILE.school, r.school, LANG) : "—"}</td><td>${r.grade ? label(PROFILE.grade, r.grade, LANG) : "—"}</td>
    ${QUESTIONS.map((q) => `<td>${label(q, r[q.key], LANG)}</td>`).join("")}</tr>`).join("") || `<tr><td colspan="${cols.length}" class="muted">Belum ada jawaban. Bagikan link atau QR di atas ke siswa.</td></tr>`;
  $("#tableNote").textContent = n > 100 ? `menampilkan 100 dari ${n} · unduh CSV untuk semua` : `${n} jawaban`;
}

/* ---------- CSV ---------- */
$("#csvBtn").onclick = () => {
  const head = ["id", "waktu", "sekolah", "kelas", ...QUESTIONS.map((q, i) => `P${i + 1} ${q.id}`), ...QUESTIONS.filter((q) => q.type === "scale").map((q) => `${q.key}_skor`), "bahasa"];
  const esc = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
  const lines = rows().map((r) => [r.id, r.ts ? new Date(r.ts).toISOString() : "", r.school ? label(PROFILE.school, r.school, LANG) : "", r.grade || "",
    ...QUESTIONS.map((q) => label(q, r[q.key], LANG)), ...QUESTIONS.filter((q) => q.type === "scale").map((q) => r[q.key]), r.lang || ""].map(esc).join(","));
  const blob = new Blob(["﻿" + [head.map(esc).join(","), ...lines].join("\r\n")], { type: "text/csv;charset=utf-8" });
  const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = `kuesioner-haloxr-${new Date().toISOString().slice(0, 10)}.csv`; a.click();
};

/* ---------- tooltip & toast ---------- */
const tip = $("#tip");
document.addEventListener("pointermove", (e) => {
  const r = e.target.closest("[data-tip]");
  if (!r) { tip.classList.remove("show"); return; }
  tip.textContent = r.dataset.tip; tip.classList.add("show");
  tip.style.left = Math.min(innerWidth - tip.offsetWidth - 8, e.clientX + 14) + "px"; tip.style.top = e.clientY + 16 + "px";
});
let tt; function toast(m) { const t = $("#toast"); t.textContent = m; t.classList.add("show"); clearTimeout(tt); tt = setTimeout(() => t.classList.remove("show"), 2000); }
filters();
