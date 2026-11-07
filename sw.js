/* HALO-XR service worker — cache-first untuk aset statis agar bisa dipakai offline di kelas.
 * Naikkan VERSION setiap deploy. */
const VERSION = "haloxr-v5";
const CORE = [
  "./", "index.html", "css/style.css", "manifest.json", "assets/icon.svg", "assets/cell.svg",
  "js/app.js", "js/viewer.js", "js/sense.js", "js/holo.js", "js/i18n.js", "js/organs.js", "js/organs-id.js", "js/organs-en.js",
  "vendor/three/three.module.js", "vendor/three/three.core.js",
  "vendor/three/addons/loaders/GLTFLoader.js", "vendor/three/addons/libs/meshopt_decoder.module.js",
  "vendor/three/addons/environments/RoomEnvironment.js", "vendor/three/addons/utils/BufferGeometryUtils.js", "vendor/three/addons/utils/SkeletonUtils.js",
];
self.addEventListener("install", (e) => { e.waitUntil(caches.open(VERSION).then((c) => c.addAll(CORE)).then(() => self.skipWaiting())); });
self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== VERSION).map((k) => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  const u = new URL(e.request.url);
  // Firebase (database/auth/SDK) & layanan lain lintas-origin dilewatkan langsung, kecuali font.
  if (u.origin !== location.origin && !u.hostname.startsWith("fonts.g")) return;
  e.respondWith(caches.match(e.request).then((hit) => hit || fetch(e.request).then((res) => {
    // model GLB & ilustrasi ikut di-cache saat pertama dibuka
    if (res.ok && (new URL(e.request.url).origin === location.origin || e.request.url.includes("fonts.g"))) {
      const copy = res.clone(); caches.open(VERSION).then((c) => c.put(e.request, copy));
    }
    return res;
  })));
});
