/* HALO-XR · app.js — navigasi, bahasa, gestur (BLE/pad/keyboard/demo), kuis N-gain, kalibrasi piramida. */
import { HoloViewer } from "./viewer.js";
import { CameraGestures, VoiceCommands, voiceSupported } from "./sense.js";

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const store = {
  get(k, d) { try { const v = localStorage.getItem("haloxr." + k); return v === null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem("haloxr." + k, JSON.stringify(v)); } catch {} },
};

const params = new URLSearchParams(location.search);
const S = {
  lang: params.get("lang") || store.get("lang", "id"),
  screen: "home",
  organ: store.get("organ", "heart"),
  style: store.get("style", "real"),
  auto: store.get("auto", true),
  gap: store.get("gap", 0.07), size: store.get("size", 0.32), mirror: store.get("mirror", true), guide: store.get("guide", false),
  conn: "off", // off | on | demo
  lastGesture: null,
  lat: [],
  quiz: store.get("quiz", { pre: null, post: null }),
  cam: "off", mic: voiceSupported ? "off" : "unsupported", wake: store.get("wake", false),
};
const T = () => TEXT[S.lang];
const get = (path) => path.split(".").reduce((o, k) => o?.[k], T());

/* ---------- ikon gestur ---------- */
const GI = {
  up: '<path d="M12 19V5M6 11l6-6 6 6"/>',
  down: '<path d="M12 5v14M6 13l6 6 6-6"/>',
  left: '<path d="M19 12H5M11 6l-6 6 6 6"/>',
  right: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  forward: '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3" fill="currentColor"/>',
  backward: '<circle cx="12" cy="12" r="8"/><path d="M8.5 8.5l7 7M15.5 8.5l-7 7"/>',
  cw: '<path d="M20 12a8 8 0 1 1-2.3-5.6"/><path d="M20 4v4h-4"/>',
  ccw: '<path d="M4 12a8 8 0 1 0 2.3-5.6"/><path d="M4 4v4h4"/>',
  wave: '<path d="M7 11V6.5a1.5 1.5 0 0 1 3 0V11M10 10V4.5a1.5 1.5 0 0 1 3 0V10M13 10V5.5a1.5 1.5 0 0 1 3 0V12M16 9.5a1.5 1.5 0 0 1 3 0V14a7 7 0 0 1-7 7h-1a6 6 0 0 1-5-2.7L3.5 14a1.5 1.5 0 0 1 2.5-1.7L7 14"/>',
};
const G_ORDER = ["up", "down", "left", "right", "forward", "backward", "cw", "ccw", "wave"];
const icon = (g) => `<svg viewBox="0 0 24 24">${GI[g]}</svg>`;

/* ---------- viewer ---------- */
const viewer = new HoloViewer($("#stage"));
viewer.state.style = S.style;
viewer.setAuto(S.auto);
viewer.onLatency = (ms) => { S.lat.push(ms); if (S.lat.length > 60) S.lat.shift(); renderLatency(); };
viewer.onLabels = updateLabels;
viewer.onLoad = () => $("#loading").classList.add("done");

/* ---------- kontrol bawaan: kamera & mikrofon ---------- */
const cam = new CameraGestures({
  onGesture: (g) => {
    if (g === "reset") { viewer.markInput(); viewer.reset(); renderPeel(); toast(T().sense.reset); }
    else if (g === "style") { viewer.markInput(); setStyle(S.style === "holo" ? "real" : "holo"); toast(T().sense.style); }
    else gesture(g, "cam");
  },
  onStatus: (st) => { S.cam = st; renderSense(); },
  onFrame: (name) => { $("#camLabel").textContent = name ? name.replace("_", " ") : ""; },
});
const voice = new VoiceCommands({
  getStructures: () => hotspotList().map((h, i) => ({ i, label: h.label })),
  onStatus: (st) => { S.mic = st; renderSense(); },
  onHeard: (text, cmds) => { $("#heard").textContent = `“${text}”`; if (cmds.length && (S.screen !== "device" || !$("#pyramid").hidden)) toast(`🎙 ${text}`); },
  onCommand: (c) => {
    switch (c.type) {
      case "gesture": gesture(c.value, "voice"); break;
      case "organ": selectOrgan(c.value); if ($("#pyramid").hidden) go("viewer"); break;
      case "focus": setFocus(c.value); break;
      case "style": setStyle(c.value); break;
      case "reset": viewer.markInput(); viewer.reset(); renderPeel(); break;
      case "pyramid": if ($("#pyramid").hidden) enterPyramid(); break;
      case "exitPyramid": if (!$("#pyramid").hidden) exitPyramid(); break;
    }
  },
});
voice.wake = S.wake;

async function toggleCam(on = S.cam === "off" || S.cam === "denied") {
  if (!on) { cam.stop(); $("#campip").hidden = true; return; }
  $("#campip").hidden = false;
  try { await cam.start($("#camVideo"), $("#camCanvas")); }
  catch (e) { console.error(e); cam.stop(); $("#campip").hidden = true; S.cam = "denied"; renderSense(); toast(T().sense.st.denied); }
}
function toggleMic(on = S.mic !== "on") {
  if (!voiceSupported) { toast(T().sense.st.unsupported); return; }
  on ? voice.start(S.lang) : voice.stop();
}
function renderSense() {
  const st = T().sense.st;
  const pill = (el, v) => { el.textContent = st[v] || v; el.className = "pill soft " + (v === "on" ? "on" : v === "denied" || v === "unsupported" || v === "network" ? "err" : ""); };
  pill($("#camSt"), S.cam); pill($("#micSt"), S.mic);
  $("#camToggle").checked = S.cam === "on" || S.cam === "loading";
  $("#micToggle").checked = S.mic === "on" || S.mic === "network"; $("#micToggle").disabled = !voiceSupported;
  $$('[data-sense="cam"]').forEach((b) => b.classList.toggle("on", S.cam === "on"));
  $$('[data-sense="mic"]').forEach((b) => b.classList.toggle("on", S.mic === "on"));
  renderStatus();
}

/* ---------- navigasi ---------- */
function go(screen) {
  S.screen = screen;
  $$(".screen").forEach((s) => s.classList.toggle("active", s.id === "s-" + screen));
  $$("#nav button").forEach((b) => b.classList.toggle("on", b.dataset.go === screen));
  scrollTo({ top: 0, behavior: "instant" in window ? "instant" : "auto" });
  if (screen === "viewer") requestAnimationFrame(() => viewer._resize());
}

async function selectOrgan(id) {
  if (!ORGAN_BY_ID[id]) id = "heart";
  S.organ = id; store.set("organ", id);
  $("#loading").classList.remove("done");
  renderOrganText();
  renderLibrary();
  try { await viewer.show(id, ORGAN_BY_ID[id]); }
  catch (e) { console.error(e); $("#loading span").textContent = location.protocol === "file:" ? "Jalankan start.cmd (server lokal) untuk memuat model." : "Gagal memuat model."; return; }
  renderPeel(); renderHotspots(); setFocus(0);
}

/* ---------- teks ---------- */
function applyLang() {
  document.documentElement.lang = S.lang;
  $$("[data-t]").forEach((el) => { const v = get(el.dataset.t); if (typeof v === "string") el.textContent = v; });
  $("#langBtn").textContent = S.lang.toUpperCase();
  $$("#langSeg button").forEach((b) => b.classList.toggle("on", b.dataset.lang === S.lang));
  $("#search").placeholder = T().library.search;
  $("#accNote").textContent = S.lang === "id" ? "Target uji prototipe" : "Prototype test target";
  $("#cmpList").innerHTML = T().home.cmp.map(([a, b], i) => `<li><i>${i + 1}</i><div><b>${a}</b><span>${b}</span></div></li>`).join("");
  $("#gmap").innerHTML = G_ORDER.map((g) => `<div data-gm="${g}">${icon(g)}<b>${T().gestures[g]}</b><span>${T().actions[g]}</span></div>`).join("");
  $("#pad").innerHTML = G_ORDER.map((g) => `<button data-g="${g}" title="${T().actions[g]}">${icon(g)}${T().gestures[g]}</button>`).join("");
  renderStatus(); renderOrganText(); renderLibrary(); renderPeel(); renderHotspots(); setFocus(viewer.state.focus);
  renderLast(); renderQuiz(); renderLatency(); renderTopics();
  const SE = T().sense;
  $("#camGuide").innerHTML = SE.guideCam.map(([a, b]) => `<li><b>${a}</b>${b}</li>`).join("");
  $("#voiceEx").innerHTML = SE.examples.map((e) => `<span>“${e}”</span>`).join("");
  voice.setLang(S.lang); renderSense();
}

function renderOrganText() {
  const o = organText(S.organ, S.lang), e = ORGAN_BY_ID[S.organ], V = T().viewer;
  $("#vName").textContent = o.name; $("#vSci").textContent = e.sci; $("#vDesc").textContent = o.description;
  $("#heroName").textContent = o.name; $("#heroSys").textContent = `${o.system} · ${e.sci}`;
  $("#heroImg").src = S.organ === "cell" ? "assets/cell.svg" : `assets/anatomy/${S.organ}/organ.webp`;
  const facts = [[V.size, o.size], [V.weight, o.weight], [V.location, o.location], [V.fn, o.function], [V.blood, o.bloodSupply], [V.tissue, o.tissue]];
  $("#facts").innerHTML = facts.map(([k, v]) => `<div><dt>${k}</dt><dd>${v}</dd></div>`).join("");
  $("#did").innerHTML = `<b>${V.didYou}</b>${o.funFact}`;
  $("#illus").innerHTML = S.organ === "cell" ? "" :
    [[V.where, "location"], [V.micro, "microscopic"]].map(([k, f]) => `<figure class="card illu"><img loading="lazy" src="assets/anatomy/${S.organ}/${f}.webp" alt="${o.name} — ${k}" /><span class="label">${k}</span></figure>`).join("");
  $("#conds").innerHTML = o.conditions.map((c) => `<span>${c}</span>`).join("");
}

function renderLibrary() {
  const q = ($("#search").value || "").toLowerCase().trim();
  $("#organGrid").innerHTML = ORGAN_LIST.map((e) => {
    const o = organText(e.id, S.lang);
    if (q && !(o.name + " " + o.system + " " + e.sci).toLowerCase().includes(q)) return "";
    const n = e.layered ? `4 ${T().library.layers}` : `${e.hotspots.length} ${T().library.structures}`;
    const img = e.id === "cell" ? `<div class="thumb cellthumb"><img src="assets/cell.svg" alt="" /><span class="tag">3D · ${n}</span></div>` : `<div class="thumb"><img src="assets/anatomy/${e.id}/thumb.webp" alt="" /><span class="tag">3D · ${n}</span></div>`;
    return `<button class="card organ ${e.id === S.organ ? "sel" : ""}" data-organ="${e.id}">${img}<div><b>${o.name}</b><small>${o.system}</small></div></button>`;
  }).join("");
}

function renderPeel() {
  const e = ORGAN_BY_ID[S.organ], V = T().viewer;
  const names = e.layered ? Holo_layerNames() : V.peelLv;
  $("#peelTitle").textContent = e.layered ? V.layers : V.peel;
  $("#peelSeg").innerHTML = names.map((n, i) => `<button data-peel="${i}" class="${i === viewer.state.peel ? "on" : ""}">${e.layered && i ? "− " : ""}${n}</button>`).join("");
  $("#peelNow").textContent = `${viewer.state.peel}/3`;
}
const Holo_layerNames = () => ["membrane", "er", "mito", "nucleus"].map((k) => CELL_INFO[S.lang].layers[k][0]);

function hotspotList() {
  const e = ORGAN_BY_ID[S.organ];
  if (e.layered) return ["membrane", "er", "mito", "nucleus"].map((k) => { const [label, detail] = CELL_INFO[S.lang].layers[k]; return { label, detail, color: "#8CC6FF" }; });
  const o = organText(S.organ, S.lang);
  return e.hotspots.map(([id]) => ({ ...o.hotspots[id], color: e.accent }));
}

function renderHotspots() {
  const list = hotspotList();
  $("#hotspots").innerHTML = list.map((h, i) => `<button data-hs="${i}">${h.label}</button>`).join("");
  $("#labels").innerHTML = list.map((h, i) => `<span class="hs hide" data-l="${i}">${h.label}</span>`).join("");
}

function setFocus(i) {
  const list = hotspotList(); if (!list.length) return;
  i = ((i % list.length) + list.length) % list.length;
  if (ORGAN_BY_ID[S.organ].layered) { viewer.setPeel(i); renderPeel(); }
  else viewer.focus(i);
  $$("#hotspots button").forEach((b) => b.classList.toggle("on", +b.dataset.hs === i));
  $("#focusBox").innerHTML = `<b>${list[i].label}</b><p>${list[i].detail}</p>`;
  viewer.setLabelText(list[i].label);
}

function updateLabels(pts) {
  const els = $("#labels").children;
  for (const p of pts) {
    const el = els[p.i]; if (!el) continue;
    el.style.left = p.x + "px"; el.style.top = p.y + "px";
    el.classList.toggle("hide", !p.visible);
    el.classList.toggle("focus", p.i === viewer.state.focus);
  }
}

/* ---------- gestur ---------- */
function gesture(g, src = "pad") {
  if (!GI[g]) return;
  viewer.markInput();
  const e = ORGAN_BY_ID[S.organ];
  switch (g) {
    case "left": viewer.rotate(-Math.PI / 4); break;
    case "right": viewer.rotate(Math.PI / 4); break;
    case "up": viewer.rotate(0, -0.35); break;
    case "down": viewer.rotate(0, 0.35); break;
    case "forward": viewer.zoomBy(1.2); break;
    case "backward": viewer.zoomBy(1 / 1.2); break;
    case "cw": {
      const before = viewer.state.peel, now = viewer.setPeel(before + 1);
      if (now === before) toast(T().toast.peelMax);
      if (e.layered) setFocus(now); renderPeel(); break;
    }
    case "ccw": {
      const before = viewer.state.peel, now = viewer.setPeel(before - 1);
      if (now === before) toast(T().toast.restoreMax);
      if (e.layered) setFocus(now); renderPeel(); break;
    }
    case "wave": {
      const i = ORGAN_LIST.findIndex((o) => o.id === S.organ);
      selectOrgan(ORGAN_LIST[(i + 1) % ORGAN_LIST.length].id); break;
    }
  }
  S.lastGesture = { g, src };
  renderLast();
  flash(`[data-g="${g}"]`); flash(`[data-gm="${g}"]`);
}
function flash(sel) { $$(sel).forEach((el) => { el.classList.add("flash"); setTimeout(() => el.classList.remove("flash"), 260); }); }
function renderLast() {
  const L = S.lastGesture;
  $("#lastIco").innerHTML = icon(L ? L.g : "wave");
  $("#lastG").textContent = L ? T().gestures[L.g] : "—";
  $("#lastA").textContent = L ? T().actions[L.g] : T().home.noG;
}

/* ---------- Bluetooth LE (ESP32, Nordic UART) ---------- */
const NUS = "6e400001-b5a3-f393-e0a9-e50e24dcca9e", NUS_TX = "6e400003-b5a3-f393-e0a9-e50e24dcca9e";
const TOKENS = { UP: "up", DOWN: "down", LEFT: "left", RIGHT: "right", FORWARD: "forward", BACKWARD: "backward", CW: "cw", CLOCKWISE: "cw", CCW: "ccw", ANTICLOCKWISE: "ccw", WAVE: "wave" };
let ble = null, rx = "";
async function bleConnect() {
  if (ble) { ble.gatt.disconnect(); return; }
  if (!navigator.bluetooth) { toast(T().device.noBle); return; }
  try {
    const dev = await navigator.bluetooth.requestDevice({ filters: [{ namePrefix: "HALO" }, { services: [NUS] }], optionalServices: [NUS] });
    const srv = await dev.gatt.connect();
    const ch = await (await srv.getPrimaryService(NUS)).getCharacteristic(NUS_TX);
    await ch.startNotifications();
    ch.addEventListener("characteristicvaluechanged", (ev) => {
      rx += new TextDecoder().decode(ev.target.value);
      let k; while ((k = rx.search(/[\n;]/)) >= 0) { const tok = rx.slice(0, k).trim().toUpperCase(); rx = rx.slice(k + 1); if (TOKENS[tok]) gesture(TOKENS[tok], "ble"); }
      if (rx.length > 64) rx = "";
    });
    dev.addEventListener("gattserverdisconnected", () => { ble = null; setConn("off"); toast(T().toast.disconnected); });
    ble = dev; stopDemo(); setConn("on", dev.name); toast(T().toast.connected);
  } catch (e) { if (e.name !== "NotFoundError") toast(e.message); }
}

/* ---------- demo ---------- */
const DEMO = ["right", "right", "cw", "forward", "cw", "left", "ccw", "ccw", "backward", "up", "down", "right", "wave"];
let demoT = null, demoI = 0;
function startDemo() { if (ble) return; clearInterval(demoT); setConn("demo"); demoT = setInterval(() => gesture(DEMO[demoI++ % DEMO.length], "demo"), 2600); }
function stopDemo() { clearInterval(demoT); demoT = null; if (S.conn === "demo") setConn("off"); }

function setConn(c, name = "") {
  S.conn = c; renderStatus(name);
}
function renderStatus(name = "") {
  const D = T().device, pill = $("#statusPill");
  pill.classList.toggle("on", S.conn === "on"); pill.classList.toggle("demo", S.conn === "demo");
  const sp = T().sense.pill, camOn = S.cam === "on", micOn = S.mic === "on";
  $("#statusText").textContent = S.conn === "off" && (camOn || micOn) ? (camOn && micOn ? sp.both : camOn ? sp.cam : sp.mic) : T().status[S.conn];
  if (S.conn === "off" && (camOn || micOn)) pill.classList.add("on");
  $(".conn").classList.toggle("on", S.conn !== "off");
  $("#connState").textContent = T().status[S.conn];
  $("#connInfo").textContent = S.conn === "on" ? (name || ble?.name || "HALO-XR") + " · BLE UART" : navigator.bluetooth ? "Web Bluetooth ✓" : D.noBle;
  $("#bleBtn").textContent = S.conn === "on" ? D.disconnect : D.connect;
  $("#demoBtn").textContent = S.conn === "demo" ? D.stopDemo : D.demo;
}

/* ---------- latensi & fps ---------- */
function renderLatency() {
  const D = T().device, a = S.lat;
  if (!a.length) { ["#latLast", "#latAvg", "#latMax"].forEach((s) => ($(s).textContent = "—")); $("#latStatus").textContent = D.noData; $("#latStatus").className = "pill soft"; $("#stLat").textContent = "—"; return; }
  const last = a[a.length - 1], avg = a.reduce((x, y) => x + y, 0) / a.length, max = Math.max(...a);
  $("#latLast").textContent = last.toFixed(1) + " ms"; $("#latAvg").textContent = avg.toFixed(1) + " ms"; $("#latMax").textContent = max.toFixed(1) + " ms";
  $("#stLat").textContent = avg.toFixed(0) + " ms";
  const ok = avg <= 150;
  $("#latStatus").textContent = (ok ? "✓ " : "! ") + (ok ? D.within : D.over); $("#latStatus").className = "pill soft " + (ok ? "ok" : "warn");
  $("#latBar").style.width = Math.min(100, (avg / 200) * 100) + "%"; $("#latBar").classList.toggle("over", !ok);
  $("#latMeter").setAttribute("aria-valuenow", avg.toFixed(0));
}
let frames = 0, fpsT = performance.now();
(function fps() { frames++; const now = performance.now(); if (now - fpsT > 1000) { $("#stFps").textContent = Math.round((frames * 1000) / (now - fpsT)); frames = 0; fpsT = now; } requestAnimationFrame(fps); })();

/* ---------- mode piramida ---------- */
let hudT = null;
function pyrOpts() { return { gap: S.gap, size: S.size, mirror: S.mirror, guide: S.guide }; }
async function enterPyramid() {
  const p = $("#pyramid"); p.hidden = false; document.body.classList.add("pyr-on");
  viewer.enterPyramid($("#pyrCanvas"), pyrOpts());
  try { await p.requestFullscreen?.({ navigationUI: "hide" }); } catch {}
  try { S.wake = await navigator.wakeLock?.request("screen"); } catch {}
  showHud();
}
function exitPyramid() {
  $("#pyramid").hidden = true; viewer.exitPyramid(); document.body.classList.remove("pyr-on");
  if (document.fullscreenElement) document.exitFullscreen().catch(() => {});
  S.wake?.release?.(); S.wake = null;
}
function showHud() { const h = $("#pyrHud"); h.classList.remove("hide"); clearTimeout(hudT); hudT = setTimeout(() => h.classList.add("hide"), 3500); }
document.addEventListener("fullscreenchange", () => { if (!document.fullscreenElement && !$("#pyramid").hidden) exitPyramid(); });
addEventListener("resize", () => { if (!$("#pyramid").hidden) viewer.updatePyramid(pyrOpts()); });

/* ---------- kuis & N-gain ---------- */
function renderQuiz() {
  const L = T().learn;
  for (const k of ["pre", "post"]) {
    const v = S.quiz[k];
    $(`#${k}Card`).innerHTML = `<div class="num">${v === null ? "—" : Math.round(v)}</div><div class="meta"><b>${L[k]}</b><span class="muted small">${QUIZ.length} ${L.q.toLowerCase()} · ${v === null ? "—" : L.score + " " + Math.round(v)}</span></div><button class="${v === null ? "btn-primary" : "btn"}" data-quiz="${k}">${v === null ? L.start : L.redo}</button>`;
  }
  const { pre, post } = S.quiz;
  const g = pre !== null && post !== null && pre < 100 ? (post - pre) / (100 - pre) : null;
  $("#gainNum").textContent = g === null ? "—" : g.toFixed(2).replace(".", S.lang === "id" ? "," : ".");
  const cat = g === null ? "" : g >= 0.7 ? "high" : g >= 0.3 ? "mid" : "low";
  $("#gainCat").textContent = cat ? L.cat[cat] : ""; $("#gainCat").style.display = cat ? "" : "none";
  $("#gainNote").textContent = g === null ? L.need : `${L.pre} ${Math.round(pre)} → ${L.post} ${Math.round(post)}`;
  $("#gaugeVal").style.strokeDashoffset = 502.65 * (1 - Math.max(0, Math.min(1, g ?? 0)));
}
function renderTopics() {
  $("#topics").innerHTML = ORGAN_LIST.map((e) => `<button data-topic="${e.id}">${e.id === "cell" ? '<img src="assets/cell.svg" alt="" style="background:#08132F">' : `<img loading="lazy" src="assets/anatomy/${e.id}/thumb.webp" alt="">`}${organText(e.id, S.lang).name}</button>`).join("");
}
function runQuiz(kind) {
  const L = T().learn, qs = [...QUIZ].sort(() => Math.random() - 0.5);
  let i = 0, right = 0;
  const sheet = $("#sheet"), card = $("#sheetCard");
  sheet.hidden = false;
  const draw = () => {
    const q = qs[i][S.lang];
    card.innerHTML = `<div class="q-top"><span class="chip">${L[kind].toUpperCase()}</span><span class="muted small">${L.q} ${i + 1} ${L.of} ${qs.length}</span></div>
      <div class="q-bar"><i style="width:${(i / qs.length) * 100}%"></i></div>
      <p class="q-text">${q[0]}</p><div class="opts">${q[1].map((o, k) => `<button data-o="${k}">${o}</button>`).join("")}</div>
      <div class="row"><button class="btn ghost" data-close>✕</button><button class="btn-primary" data-next disabled>${i === qs.length - 1 ? L.finish : L.next}</button></div>`;
    $$(".opts button", card).forEach((b) => b.onclick = () => {
      const k = +b.dataset.o, ok = k === qs[i].a; if (ok) right++;
      $$(".opts button", card).forEach((x) => { x.disabled = true; if (+x.dataset.o === qs[i].a) x.classList.add("right"); });
      if (!ok) b.classList.add("wrong");
      $("[data-next]", card).disabled = false;
    });
    $("[data-next]", card).onclick = () => { if (++i < qs.length) draw(); else finish(); };
    $("[data-close]", card).onclick = () => (sheet.hidden = true);
  };
  const finish = () => {
    S.quiz[kind] = (right / qs.length) * 100; store.set("quiz", S.quiz);
    sheet.hidden = true; renderQuiz(); toast(`${L[kind]} · ${L.score} ${Math.round(S.quiz[kind])}`);
  };
  draw();
}

/* ---------- toast ---------- */
let toastT = null;
function toast(msg) { const t = $("#toast"); t.textContent = msg; t.classList.add("show"); clearTimeout(toastT); toastT = setTimeout(() => t.classList.remove("show"), 2200); }

/* ---------- kalibrasi ---------- */
function initCalib() {
  const bind = (id, key, fmt) => {
    const el = $("#" + id), out = $("#" + id + "Out");
    el.value = S[key]; out.textContent = fmt(S[key]);
    el.oninput = () => { S[key] = +el.value; store.set(key, S[key]); out.textContent = fmt(S[key]); viewer.updatePyramid(pyrOpts()); };
  };
  bind("gap", "gap", (v) => Math.round(v * 100) + "%");
  bind("size", "size", (v) => Math.round(v * 100) + "%");
  for (const k of ["mirror", "guide"]) { const el = $("#" + k); el.checked = S[k]; el.onchange = () => { S[k] = el.checked; store.set(k, S[k]); viewer.updatePyramid(pyrOpts()); }; }
  const ar = $("#autoRot"); ar.checked = S.auto; ar.onchange = () => { S.auto = ar.checked; store.set("auto", S.auto); viewer.setAuto(S.auto); };
}
function setStyle(s) { S.style = s; store.set("style", s); viewer.setStyle(s); $$("#styleSeg button").forEach((b) => b.classList.toggle("on", b.dataset.style === s)); }
function setLang(l) { S.lang = l; store.set("lang", l); applyLang(); }

/* ---------- event ---------- */
document.addEventListener("click", (ev) => {
  const t = ev.target.closest("button,[data-go]"); if (!t) return;
  const d = t.dataset;
  if (d.go) go(d.go);
  else if (d.g) gesture(d.g, "pad");
  else if (d.organ) { selectOrgan(d.organ); go("viewer"); }
  else if (d.topic) { selectOrgan(d.topic); go("viewer"); }
  else if (d.peel !== undefined) { const n = viewer.setPeel(+d.peel); if (ORGAN_BY_ID[S.organ].layered) setFocus(n); renderPeel(); }
  else if (d.hs !== undefined) setFocus(+d.hs);
  else if (d.style) setStyle(d.style);
  else if (d.lang) setLang(d.lang);
  else if (d.quiz) runQuiz(d.quiz);
  else if (d.act === "pyramid") enterPyramid();
  else if (d.act === "reset") { viewer.reset(); renderPeel(); }
  else if (d.sense === "cam") toggleCam();
  else if (d.sense === "mic") toggleMic();
});
$("#langBtn").onclick = () => setLang(S.lang === "id" ? "en" : "id");
$("#camToggle").onchange = (e) => toggleCam(e.target.checked);
$("#campip").onclick = (e) => e.currentTarget.classList.toggle("mini");
$("#micToggle").onchange = (e) => toggleMic(e.target.checked);
$("#wakeToggle").checked = S.wake;
$("#wakeToggle").onchange = (e) => { S.wake = voice.wake = e.target.checked; store.set("wake", S.wake); };
$("#bleBtn").onclick = bleConnect;
$("#demoBtn").onclick = () => (S.conn === "demo" ? stopDemo() : startDemo());
$("#pyrExit").onclick = exitPyramid;
$("#pyramid").addEventListener("pointerdown", showHud);
$("#search").addEventListener("input", renderLibrary);
$("#resetQuiz").onclick = () => { S.quiz = { pre: null, post: null }; store.set("quiz", S.quiz); renderQuiz(); };
$("#sheet").addEventListener("click", (e) => { if (e.target.id === "sheet") e.currentTarget.hidden = true; });

const KEYS = { ArrowLeft: "left", ArrowRight: "right", ArrowUp: "up", ArrowDown: "down", "+": "forward", "=": "forward", "-": "backward", "]": "cw", "[": "ccw", " ": "wave" };
document.addEventListener("keydown", (e) => {
  if (e.target.matches("input")) return;
  if (e.key === "Escape" && !$("#pyramid").hidden) return exitPyramid();
  if (e.key === "p" || e.key === "P") return $("#pyramid").hidden ? enterPyramid() : exitPyramid();
  const g = KEYS[e.key];
  if (g && (S.screen === "viewer" || !$("#pyramid").hidden)) { e.preventDefault(); gesture(g, "key"); }
});

/* ---------- start ---------- */
if (location.protocol === "file:") $("#fileBanner").hidden = false;
initCalib();
setStyle(S.style);
applyLang();
go(params.get("screen") || "home");
selectOrgan(params.get("organ") || S.organ);
if (params.has("demo")) startDemo();
if (params.has("pyramid")) setTimeout(enterPyramid, 300);
if ("serviceWorker" in navigator && location.protocol.startsWith("http") && !params.has("nosw")) navigator.serviceWorker.register("sw.js").catch(() => {});

// API untuk perekam/presentasi (Playwright): APP.go('viewer'), APP.set({organ:'brain', style:'holo'}), APP.gesture('cw')
window.APP = {
  go, gesture, viewer, enterPyramid, exitPyramid, cam, voice, toggleCam, toggleMic,
  async set(o = {}) {
    if (o.lang) setLang(o.lang);
    if (o.style) setStyle(o.style);
    if (o.organ) await selectOrgan(o.organ);
    if (o.peel !== undefined) { viewer.setPeel(o.peel); renderPeel(); }
    if (o.focus !== undefined) setFocus(o.focus);
    if (o.auto !== undefined) viewer.setAuto(o.auto);
    if (o.quiz) { S.quiz = o.quiz; renderQuiz(); }
    if (o.lat) { S.lat = o.lat; renderLatency(); }
  },
};
