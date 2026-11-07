/* HALO-XR · viewer.js — renderer three.js untuk tampilan tunggal & mode piramida Pepper's Ghost.
 * Mode piramida: 4 kamera (depan/kanan/belakang/kiri) dirender ke atlas 2×2, lalu dikomposisi ke canvas 2D
 * dengan rotasi per sisi (bagian atas objek menghadap keluar) + cermin opsional untuk pantulan akrilik.
 */
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { MeshoptDecoder } from "three/addons/libs/meshopt_decoder.module.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";

const FIT_SIZE = 3.8;
const _v = new THREE.Vector3();
const CELL_SCALE = 1.55;
const PEEL_Z = [99, 0.95, 0.35, -0.25]; // posisi bidang potong per level irisan (ruang dunia, sumbu +z = depan)
const HOLO_A = new THREE.Color("#8CC6FF"), HOLO_B = new THREE.Color("#4F9BFF");

const HOLO_VERT = /* glsl */ `
#include <common>
#include <clipping_planes_pars_vertex>
varying vec3 vN; varying vec3 vV; varying vec2 vUv;
void main(){
  vUv = uv;
  vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
  vN = normalize(normalMatrix * normal); vV = normalize(-mvPosition.xyz);
  gl_Position = projectionMatrix * mvPosition;
  #include <clipping_planes_vertex>
}`;
const HOLO_FRAG = /* glsl */ `
#include <common>
#include <clipping_planes_pars_fragment>
uniform sampler2D map; uniform float hasMap; uniform vec3 cA; uniform vec3 cB; uniform float uTime;
varying vec3 vN; varying vec3 vV; varying vec2 vUv;
void main(){
  #include <clipping_planes_fragment>
  float f = pow(1.0 - abs(dot(normalize(vN), normalize(vV))), 2.2);
  float lum = hasMap > 0.5 ? dot(texture2D(map, vUv).rgb, vec3(0.299, 0.587, 0.114)) : 0.5;
  float scan = 0.88 + 0.12 * sin(vUv.y * 420.0 - uTime * 5.0);
  vec3 col = cA * (0.12 + lum * 0.55) + cB * f * 1.5;
  #if NUM_CLIPPING_PLANES > 0
    float cd = clippingPlanes[0].w - dot(vClipPosition, clippingPlanes[0].xyz);
    col += vec3(0.55, 0.85, 1.0) * smoothstep(0.07, 0.0, cd) * 1.6;
  #endif
  gl_FragColor = vec4(col * scan, 1.0);
}`;
// Bagian dalam irisan: back-face diberi warna jaringan dalam + garis glow di tepi potongan.
const CUT_FRAG = /* glsl */ `#include <dithering_fragment>
  if (!gl_FrontFacing) gl_FragColor.rgb = mix(gl_FragColor.rgb, vec3(0.36, 0.05, 0.08), 0.7);
  #if NUM_CLIPPING_PLANES > 0
    float cd = clippingPlanes[0].w - dot(vClipPosition, clippingPlanes[0].xyz);
    gl_FragColor.rgb += vec3(0.35, 0.75, 1.0) * smoothstep(0.06, 0.0, cd) * 1.4;
  #endif`;

export class HoloViewer {
  constructor(stage) {
    this.stage = stage;
    this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
    this.renderer.setClearColor(0x000000, 0);
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.renderer.toneMapping = THREE.NeutralToneMapping;
    this.renderer.localClippingEnabled = true;
    stage.appendChild(this.renderer.domElement);

    this.scene = new THREE.Scene();
    const pm = new THREE.PMREMGenerator(this.renderer);
    this.scene.environment = pm.fromScene(new RoomEnvironment(), 0.04).texture;
    const key = new THREE.DirectionalLight(0xffffff, 1.4); key.position.set(3, 4, 5);
    const rim = new THREE.DirectionalLight(0x8cc6ff, 1.2); rim.position.set(-4, 2, -5);
    this.scene.add(key, rim, new THREE.AmbientLight(0xffffff, 0.25));

    this.turn = new THREE.Group(); // yaw/pitch dari kontrol & gestur
    this.pivot = new THREE.Group(); this.pivot.rotation.set(0.05, -0.28, 0); // ruang hotspot (sama seperti repo anatomy)
    this.turn.add(this.pivot); this.scene.add(this.turn);
    this.camera = new THREE.PerspectiveCamera(30, 1, 0.1, 100);
    this.pyrCam = new THREE.PerspectiveCamera(30, 1, 0.1, 100);

    this.clip = new THREE.Plane(new THREE.Vector3(0, 0, -1), PEEL_Z[0]);
    this.loader = new GLTFLoader().setMeshoptDecoder(MeshoptDecoder);
    this.cache = new Map();
    this.markers = [];
    this.state = { yaw: 0, pitch: 0, zoom: 1, tYaw: 0, tPitch: 0, tZoom: 1, peel: 0, focus: 0, style: "real", auto: true };
    this.lastInteract = 0;
    this.pendingInput = null;
    this.onLatency = null; this.onLabels = null; this.onLoad = null;
    this.pyr = null;
    this.tPrev = performance.now(); this.t = 0;

    this._resize = this._resize.bind(this);
    new ResizeObserver(this._resize).observe(stage);
    this._resize();
    this._controls(stage);
    this.renderer.setAnimationLoop(() => this._frame());
  }

  /* ---------- pemuatan model ---------- */
  async show(id, entry) {
    this.current = id;
    this.entry = entry;
    this.state.peel = 0; this.state.focus = 0; this.clip.constant = PEEL_Z[0];
    let obj = this.cache.get(id);
    if (!obj) {
      obj = entry.layered ? this._buildCell() : await this._loadGLB(entry.model);
      if (this.current !== id) return; // pengguna sudah pindah organ
      this.cache.set(id, obj);
    }
    while (this.pivot.children.length) this.pivot.remove(this.pivot.children[0]);
    this.pivot.add(obj.root);
    this.obj = obj;
    this._buildMarkers(entry);
    this.setStyle(this.state.style);
    this._applyPeel(true);
    this.onLoad?.(id);
  }

  async _loadGLB(url) {
    const gltf = await this.loader.loadAsync(url);
    const model = gltf.scene;
    const box = new THREE.Box3().setFromObject(model);
    const size = box.getSize(new THREE.Vector3()), center = box.getCenter(new THREE.Vector3());
    const s = FIT_SIZE / Math.max(size.x, size.y, size.z, 0.001);
    model.scale.setScalar(s); model.position.copy(center.multiplyScalar(-s));
    const meshes = [];
    model.traverse((c) => {
      if (!c.isMesh) return;
      c.frustumCulled = false;
      const m = c.material;
      if (m.isMeshStandardMaterial) {
        m.roughness = THREE.MathUtils.clamp(m.roughness ?? 0.5, 0.42, 0.62);
        m.metalness = 0; m.envMapIntensity = 0.45;
        if (m.isMeshPhysicalMaterial) { m.transmission = 0; m.thickness = 0; m.clearcoat = Math.min(m.clearcoat, 0.12); }
      }
      m.clippingPlanes = [this.clip];
      m.onBeforeCompile = (sh) => { sh.fragmentShader = sh.fragmentShader.replace("#include <dithering_fragment>", CUT_FRAG); };
      c.userData.real = m;
      c.userData.holo = new THREE.ShaderMaterial({
        vertexShader: HOLO_VERT, fragmentShader: HOLO_FRAG, clipping: true, clippingPlanes: [this.clip],
        side: THREE.DoubleSide, blending: THREE.AdditiveBlending, depthWrite: false, transparent: true,
        uniforms: { map: { value: m.map || null }, hasMap: { value: m.map ? 1 : 0 }, cA: { value: HOLO_A }, cB: { value: HOLO_B }, uTime: { value: 0 } },
      });
      meshes.push(c);
    });
    return { root: model, meshes, layered: false };
  }

  _buildCell() {
    const m = Holo.cell(); // global dari holo.js (skrip klasik)
    const root = new THREE.Group(); root.scale.setScalar(CELL_SCALE);
    const layers = m.layers.map((L) => {
      const pos = [];
      for (const l of L.lines) for (let i = 0; i < l.length - 1; i++) pos.push(...l[i], ...l[i + 1]);
      const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
      const mat = new THREE.LineBasicMaterial({ color: L.color, transparent: true, opacity: 1, blending: THREE.AdditiveBlending, depthWrite: false });
      const seg = new THREE.LineSegments(g, mat); root.add(seg);
      return { key: L.key, seg, mat, anchor: new THREE.Vector3(...L.anchor).multiplyScalar(CELL_SCALE), alpha: 1 };
    });
    return { root, layers, layered: true };
  }

  _buildMarkers(entry) {
    for (const mk of this.markers) this.pivot.remove(mk);
    this.markers = [];
    const pts = this.obj.layered ? this.obj.layers.map((L) => L.anchor) : entry.hotspots.map(([, p]) => new THREE.Vector3(...p));
    const geo = new THREE.SphereGeometry(0.055, 16, 12);
    pts.forEach((p) => {
      const mk = new THREE.Mesh(geo, new THREE.MeshBasicMaterial({ color: 0xffffff, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false }));
      mk.position.copy(p); this.pivot.add(mk); this.markers.push(mk);
    });
    this._label(null);
  }

  // Sprite label untuk mode piramida (ikut berotasi bersama gambar tiap sisi).
  _label(text) {
    if (this.sprite) { this.pivot.remove(this.sprite); this.sprite.material.map.dispose(); this.sprite = null; }
    if (!text) return;
    const c = document.createElement("canvas"), x = c.getContext("2d");
    c.width = 512; c.height = 96;
    x.font = "700 46px 'Plus Jakarta Sans', 'Segoe UI', sans-serif";
    x.fillStyle = "rgba(10,30,80,.65)"; x.strokeStyle = "rgba(140,198,255,.9)"; x.lineWidth = 3;
    const w = Math.min(500, x.measureText(text).width + 56);
    x.beginPath(); x.roundRect((512 - w) / 2, 10, w, 76, 38); x.fill(); x.stroke();
    x.fillStyle = "#EAF4FF"; x.textAlign = "center"; x.textBaseline = "middle"; x.fillText(text, 256, 50);
    const tex = new THREE.CanvasTexture(c); tex.colorSpace = THREE.SRGBColorSpace;
    this.sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, depthTest: false, transparent: true }));
    this.sprite.scale.set(2.6, 0.49, 1);
    this.sprite.renderOrder = 10;
    this.pivot.add(this.sprite);
  }

  /* ---------- API kontrol ---------- */
  setStyle(style) {
    this.state.style = style;
    if (!this.obj) return;
    if (this.obj.layered) return;
    for (const c of this.obj.meshes) c.material = style === "holo" ? c.userData.holo : c.userData.real;
    this._applyPeel(true);
  }
  rotate(dYaw, dPitch = 0) {
    this.state.tYaw += dYaw;
    this.state.tPitch = THREE.MathUtils.clamp(this.state.tPitch + dPitch, -1.1, 1.1);
    this.lastInteract = performance.now();
  }
  zoomBy(f) { this.state.tZoom = THREE.MathUtils.clamp(this.state.tZoom * f, 0.55, 2.4); this.lastInteract = performance.now(); }
  reset() { Object.assign(this.state, { tYaw: 0, tPitch: 0, tZoom: 1 }); this.setPeel(0); }
  setAuto(v) { this.state.auto = v; }
  get peelMax() { return 3; }
  setPeel(n) {
    this.state.peel = THREE.MathUtils.clamp(n, 0, this.peelMax);
    if (this.obj?.layered) this.state.focus = this.state.peel;
    this._applyPeel(false);
    return this.state.peel;
  }
  focus(i) {
    this.state.focus = i;
    const p = this.markers[i]?.position;
    if (p && !this.obj.layered) {
      // putar agar hotspot menghadap kamera depan
      const v = p.clone().applyEuler(this.pivot.rotation);
      const want = -Math.atan2(v.x, v.z);
      let d = want - this.state.tYaw; d = Math.atan2(Math.sin(d), Math.cos(d));
      this.state.tYaw += d; this.lastInteract = performance.now();
    }
  }
  setLabelText(t) { this._labelText = t; if (this.pyr) this._label(t); }
  markInput() { this.pendingInput = performance.now(); }

  _applyPeel(instant) {
    if (!this.obj) return;
    if (this.obj.layered) {
      this.obj.layers.forEach((L, i) => { L.target = i < this.state.peel ? 0 : 1; if (instant) L.alpha = L.target; });
      return;
    }
    const cut = this.state.peel > 0;
    for (const c of this.obj.meshes) {
      c.userData.real.side = cut ? THREE.DoubleSide : THREE.FrontSide;
      c.userData.real.needsUpdate = true;
    }
    this.clipTarget = PEEL_Z[this.state.peel];
    if (instant) this.clip.constant = this.clipTarget;
  }

  /* ---------- mode piramida ---------- */
  enterPyramid(canvas, opts) {
    this.pyr = { canvas, ctx: canvas.getContext("2d"), opts };
    this.stage.style.visibility = "hidden";
    this._label(this._labelText);
    this._resize();
  }
  updatePyramid(opts) { if (this.pyr) { this.pyr.opts = { ...this.pyr.opts, ...opts }; this._resize(); } }
  exitPyramid() {
    this.pyr = null; this._label(null);
    this.stage.style.visibility = "";
    this._resize();
  }

  _resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    if (this.pyr) {
      const { canvas, opts } = this.pyr;
      const W = Math.round(innerWidth * dpr), H = Math.round(innerHeight * dpr);
      canvas.width = W; canvas.height = H;
      const s = Math.round(Math.min(W, H) * opts.size);
      this.pyr.s = s; this.pyr.W = W; this.pyr.H = H;
      this.renderer.setPixelRatio(1);
      this.renderer.setSize(s * 2, s * 2, false);
    } else {
      const r = this.stage.getBoundingClientRect();
      if (!r.width) return;
      this.renderer.setPixelRatio(dpr);
      this.renderer.setSize(r.width, r.height, false);
      this.renderer.domElement.style.width = "100%"; this.renderer.domElement.style.height = "100%";
      this.camera.aspect = r.width / r.height; this.camera.updateProjectionMatrix();
    }
  }

  _frame() {
    const now = performance.now(), dt = Math.min((now - this.tPrev) / 1000, 0.1), st = this.state;
    this.tPrev = now; const t = (this.t += dt);
    if (st.auto && performance.now() - this.lastInteract > 3000) st.tYaw += dt * 0.35;
    const k = 1 - Math.exp(-dt * 7);
    st.yaw += (st.tYaw - st.yaw) * k; st.pitch += (st.tPitch - st.pitch) * k; st.zoom += (st.tZoom - st.zoom) * k;
    this.turn.rotation.set(st.pitch, st.yaw, 0, "XYZ");
    if (this.clipTarget !== undefined) this.clip.constant += (this.clipTarget - this.clip.constant) * k;

    if (this.obj?.layered) {
      this.obj.layers.forEach((L, i) => {
        L.alpha += ((L.target ?? 1) - L.alpha) * k;
        L.mat.opacity = L.alpha * (i === st.focus ? 1 : 0.5);
        L.seg.visible = L.alpha > 0.01;
      });
    } else if (this.obj) {
      for (const c of this.obj.meshes) c.userData.holo.uniforms.uTime.value = t;
    }
    this.markers.forEach((mk, i) => {
      const f = i === st.focus;
      mk.material.color.set(f ? 0xffffff : 0x8cc6ff);
      mk.scale.setScalar(f ? 1.3 + 0.35 * Math.sin(t * 5) : 0.8);
      mk.visible = this.obj?.layered ? i >= st.peel : mk.getWorldPosition(_v).z <= this.clip.constant + 0.05;
    });
    if (this.sprite && this.markers[st.focus]) {
      const p = this.markers[st.focus].position;
      this.sprite.position.set(p.x * 1.08, p.y + 0.42, p.z * 1.08);
    }

    const dist = 10 / st.zoom;
    if (this.pyr) this._renderPyramid(dist);
    else {
      this.camera.position.set(0, 0, dist); this.camera.lookAt(0, 0, 0);
      this.renderer.render(this.scene, this.camera);
      this._emitLabels();
    }
    if (this.pendingInput !== null) {
      const ms = performance.now() - this.pendingInput; this.pendingInput = null;
      this.onLatency?.(ms);
    }
  }

  _renderPyramid(dist) {
    const { ctx, s, W, H, opts } = this.pyr, R = this.renderer, cam = this.pyrCam;
    cam.aspect = 1; cam.updateProjectionMatrix();
    R.setClearColor(0x000000, 1);
    R.setScissorTest(true);
    // sisi: [sudut kamera, kolom atlas, baris atlas]
    const views = [[0, 0, 0], [Math.PI / 2, 1, 0], [Math.PI, 0, 1], [-Math.PI / 2, 1, 1]];
    for (const [a, cx, cy] of views) {
      R.setViewport(cx * s, cy * s, s, s); R.setScissor(cx * s, cy * s, s, s);
      cam.position.set(Math.sin(a) * dist, 0, Math.cos(a) * dist); cam.lookAt(0, 0, 0);
      R.render(this.scene, cam);
    }
    R.setScissorTest(false);
    R.setClearColor(0x000000, 0);

    // komposisi: depan → bawah layar (rotasi 180°), kanan → kanan (90°), belakang → atas (0°), kiri → kiri (−90°)
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.fillStyle = "#000"; ctx.fillRect(0, 0, W, H);
    const gap = Math.min(W, H) * opts.gap, cxs = W / 2, cys = H / 2, src = R.domElement, S2 = s * 2;
    const place = [
      [cxs, cys + gap + s / 2, Math.PI],          // depan
      [cxs + gap + s / 2, cys, Math.PI / 2],      // kanan
      [cxs, cys - gap - s / 2, 0],                // belakang
      [cxs - gap - s / 2, cys, -Math.PI / 2],     // kiri
    ];
    views.forEach(([, col, row], i) => {
      const [x, y, rot] = place[i];
      ctx.setTransform(1, 0, 0, 1, x, y); ctx.rotate(rot);
      if (opts.mirror) ctx.scale(-1, 1);
      // atlas WebGL: baris 0 ada di bawah kanvas
      ctx.drawImage(src, col * s, S2 - (row + 1) * s, s, s, -s / 2, -s / 2, s, s);
    });
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    if (opts.guide) {
      ctx.strokeStyle = "rgba(140,198,255,.35)"; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(cxs - gap, cys - gap); ctx.lineTo(cxs + gap, cys + gap); ctx.moveTo(cxs + gap, cys - gap); ctx.lineTo(cxs - gap, cys + gap); ctx.stroke();
      ctx.strokeRect(cxs - gap, cys - gap, gap * 2, gap * 2);
    }
  }

  _emitLabels() {
    if (!this.onLabels) return;
    const r = this.renderer.domElement.getBoundingClientRect(), out = [];
    const v = new THREE.Vector3(), n = new THREE.Vector3(), toCam = new THREE.Vector3();
    this.markers.forEach((mk, i) => {
      mk.getWorldPosition(v);
      n.copy(v).normalize(); toCam.copy(this.camera.position).sub(v).normalize();
      const facing = this.obj?.layered ? mk.visible : n.dot(toCam) > 0.05 && v.z <= this.clip.constant + 0.05;
      const p = v.clone().project(this.camera);
      out.push({ i, x: (p.x * 0.5 + 0.5) * r.width, y: (-p.y * 0.5 + 0.5) * r.height, visible: facing });
    });
    this.onLabels(out);
  }

  /* ---------- seret / cubit / scroll ---------- */
  _controls(el) {
    const pts = new Map(); let pinch0 = 0;
    el.addEventListener("pointerdown", (e) => { el.setPointerCapture(e.pointerId); pts.set(e.pointerId, [e.clientX, e.clientY]); });
    el.addEventListener("pointermove", (e) => {
      if (!pts.has(e.pointerId)) return;
      const [px, py] = pts.get(e.pointerId); pts.set(e.pointerId, [e.clientX, e.clientY]);
      if (pts.size === 1) { this.rotate((e.clientX - px) * 0.008, (e.clientY - py) * 0.006); }
      else if (pts.size === 2) {
        const [a, b] = [...pts.values()], d = Math.hypot(a[0] - b[0], a[1] - b[1]);
        if (pinch0) this.zoomBy(d / pinch0); pinch0 = d;
      }
    });
    const up = (e) => { pts.delete(e.pointerId); pinch0 = 0; };
    el.addEventListener("pointerup", up); el.addEventListener("pointercancel", up);
    el.addEventListener("wheel", (e) => { e.preventDefault(); this.zoomBy(e.deltaY < 0 ? 1.08 : 1 / 1.08); }, { passive: false });
  }
}
