/* HALO-XR · holo.js
 * Generator geometri prosedural (tanpa library) untuk model sel hewan berlapis.
 * Lapisan = kumpulan polyline 3D [[x,y,z],...]; viewer.js mengubahnya menjadi THREE.LineSegments.
 */
const Holo = (() => {
  const TAU = Math.PI * 2;

  /* ---------- util vektor ---------- */
  const norm = (v) => { const l = Math.hypot(v[0], v[1], v[2]) || 1; return [v[0] / l, v[1] / l, v[2] / l]; };
  const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const lerp = (a, b, t) => a + (b - a) * t;
  const dirOf = (theta, phi) => [Math.sin(phi) * Math.cos(theta), Math.cos(phi), Math.sin(phi) * Math.sin(theta)];
  let seed = 7;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);

  /* ---------- generator geometri ---------- */
  // Permukaan radial: rFn(dir) → jarak dari pusat. Menghasilkan cincin lintang + meridian.
  function radial(rFn, o = {}) {
    const { lat = 16, lon = 24, c = [0, 0, 0], s = [1, 1, 1], keep } = o;
    const P = (th, ph) => {
      const d = dirOf(th, ph), r = rFn(d);
      return [c[0] + d[0] * r * s[0], c[1] + d[1] * r * s[1], c[2] + d[2] * r * s[2]];
    };
    const lines = [];
    const push = (pts) => {
      // pecah polyline bila ada titik yang dibuang oleh keep()
      let cur = [];
      for (const p of pts) {
        if (!keep || keep(p)) cur.push(p);
        else { if (cur.length > 1) lines.push(cur); cur = []; }
      }
      if (cur.length > 1) lines.push(cur);
    };
    for (let i = 1; i < lat; i++) {
      const ph = Math.PI * i / lat, ring = [];
      for (let j = 0; j <= lon * 2; j++) ring.push(P(TAU * j / (lon * 2), ph));
      push(ring);
    }
    for (let j = 0; j < lon; j++) {
      const th = TAU * j / lon, mer = [];
      for (let i = 0; i <= lat * 2; i++) mer.push(P(th, Math.PI * i / (lat * 2)));
      push(mer);
    }
    return lines;
  }
  const ellipsoid = (c, s, o = {}) => radial(() => 1, { ...o, c, s });

  // Akar fungsi implisit sepanjang arah d (f<0 di dalam).
  function implicitR(f, d, rmax = 2.2) {
    let a = 0, b = 0;
    for (let r = 0.02; r <= rmax; r += 0.02) { if (f(d[0] * r, d[1] * r, d[2] * r) > 0) { b = r; break; } a = r; }
    if (!b) return rmax;
    for (let k = 0; k < 14; k++) { const m = (a + b) / 2; if (f(d[0] * m, d[1] * m, d[2] * m) > 0) b = m; else a = m; }
    return (a + b) / 2;
  }

  // Tabung sepanjang jalur titik.
  function tube(path, rad, o = {}) {
    const { sides = 8, ringEvery = 1, longi = 4 } = o;
    const R = typeof rad === "function" ? rad : () => rad;
    const rings = [], frames = [];
    for (let i = 0; i < path.length; i++) {
      const T = norm(sub(path[Math.min(i + 1, path.length - 1)], path[Math.max(i - 1, 0)]));
      let N = cross(T, [0, 1, 0]); if (Math.hypot(...N) < 0.1) N = cross(T, [1, 0, 0]);
      N = norm(N); const B = cross(T, N);
      frames.push([N, B]);
    }
    const ptAt = (i, a) => {
      const [N, B] = frames[i], r = R(i / (path.length - 1)), p = path[i];
      return [p[0] + (N[0] * Math.cos(a) + B[0] * Math.sin(a)) * r, p[1] + (N[1] * Math.cos(a) + B[1] * Math.sin(a)) * r, p[2] + (N[2] * Math.cos(a) + B[2] * Math.sin(a)) * r];
    };
    for (let i = 0; i < path.length; i += ringEvery) {
      const ring = []; for (let k = 0; k <= sides; k++) ring.push(ptAt(i, TAU * k / sides)); rings.push(ring);
    }
    for (let k = 0; k < longi; k++) {
      const a = TAU * k / longi, l = []; for (let i = 0; i < path.length; i++) l.push(ptAt(i, a)); rings.push(l);
    }
    return rings;
  }

  function bezier(p0, p1, p2, p3, n = 24) {
    const out = [];
    for (let i = 0; i <= n; i++) {
      const t = i / n, u = 1 - t;
      out.push([0, 1, 2].map((k) => u * u * u * p0[k] + 3 * u * u * t * p1[k] + 3 * u * t * t * p2[k] + t * t * t * p3[k]));
    }
    return out;
  }

  // Kurva di atas permukaan radial (lingkaran besar miring) — untuk fisura/garis anatomi.
  function surfaceCurve(rFn, axis, o = {}) {
    const { c = [0, 0, 0], s = [1, 1, 1], n = 80, from = 0, to = TAU } = o;
    const A = norm(axis); let U = norm(cross(A, [0, 0, 1])); if (Math.hypot(...cross(A, [0, 0, 1])) < 0.1) U = norm(cross(A, [1, 0, 0]));
    const V = cross(A, U), pts = [];
    for (let i = 0; i <= n; i++) {
      const t = lerp(from, to, i / n), d = norm([U[0] * Math.cos(t) + V[0] * Math.sin(t), U[1] * Math.cos(t) + V[1] * Math.sin(t), U[2] * Math.cos(t) + V[2] * Math.sin(t)]);
      const r = rFn(d) * 1.005; pts.push([c[0] + d[0] * r * s[0], c[1] + d[1] * r * s[1], c[2] + d[2] * r * s[2]]);
    }
    return [pts];
  }

  function buildCell() {
    seed = 23;
    const membrane = radial((d) => 1 + 0.05 * Math.sin(3 * Math.atan2(d[2], d[0]) + 2 * d[1]) + 0.03 * Math.sin(7 * d[1]), { lat: 16, lon: 26, s: [1.15, 0.95, 1.05] });
    const er = [];
    for (let k = 0; k < 4; k++) {
      const r = 0.5 + k * 0.08;
      er.push(...surfaceCurve((d) => r * (1 + 0.08 * Math.sin(12 * d[0] + k)), [0.2, 1, 0.1 * k], { from: 0.2 + k * 0.1, to: 3.6 + k * 0.2, n: 70 }));
    }
    const golgi = [];
    for (let k = 0; k < 5; k++) golgi.push(...surfaceCurve(() => 0.22 + k * 0.035, [0, 0, 1], { c: [0.45, -0.45, 0.3], from: 3.4, to: 6.0, n: 30, s: [1, 0.7, 1] }));
    const mito = [];
    for (let k = 0; k < 6; k++) {
      const a = rnd() * TAU, ph = 0.6 + rnd() * 1.9, rr = 0.68 + rnd() * 0.12, c = dirOf(a, ph).map((v) => v * rr);
      const s = [0.17, 0.08, 0.08];
      mito.push(...ellipsoid(c, s, { lat: 6, lon: 10 }));
      const cr = []; for (let i = 0; i <= 14; i++) cr.push([c[0] - s[0] * 0.8 + (i / 14) * s[0] * 1.6, c[1] + (i % 2 ? 1 : -1) * s[1] * 0.6, c[2]]);
      mito.push(cr);
    }
    const nucleus = [
      ...radial(() => 1, { lat: 14, lon: 20, s: [0.36, 0.34, 0.36] }),
      ...ellipsoid([0.06, 0.05, 0.04], [0.12, 0.12, 0.12], { lat: 7, lon: 10 }),
    ];
    return {
      key: "cell",
      layers: [
        { key: "membrane", color: "#BFE3FF", lines: membrane, anchor: [1.1, 0.4, 0.3] },
        { key: "er", color: "#8CC6FF", lines: [...er, ...golgi], anchor: [0.45, -0.45, 0.3] },
        { key: "mito", color: "#FFB36B", lines: mito, anchor: [-0.7, 0.2, 0.2] },
        { key: "nucleus", color: "#FF7A85", lines: nucleus, anchor: [0.3, 0.25, 0.2] },
      ],
    };
  }

  return { cell: buildCell };
})();
