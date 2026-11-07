/* HALO-XR · organs.js — registri model (struktur saja; teks ada di organs-*.js & i18n.js).
 * 9 organ GLB + posisi hotspot diadaptasi dari github.com/thebuggeddev/anatomy (app/lib/anatomy-data.ts).
 * Koordinat hotspot berada di ruang model ternormalisasi FIT_SIZE = 3.8.
 */
const ORGAN_LIST = [
  { id: "heart", model: "assets/models/heart.glb", accent: "#ee7c6a", sci: "Cor", hotspots: [
    ["aorta", [-0.35, 1.65, 0.55]], ["left-atrium", [0.82, 0.65, 0.5]], ["right-atrium", [-0.9, 0.35, 0.55]],
    ["left-ventricle", [0.7, -0.75, 0.65]], ["right-ventricle", [-0.65, -0.68, 0.66]], ["mitral", [0.18, -1.35, 0.48]]] },
  { id: "brain", model: "assets/models/brain.glb", accent: "#c58696", sci: "Encephalon", hotspots: [
    ["frontal", [-0.7, 0.65, 0.8]], ["parietal", [0.15, 1.1, 0.65]], ["temporal", [0.75, -0.1, 0.82]], ["cerebellum", [0.72, -0.9, 0.55]]] },
  { id: "lungs", model: "assets/models/lungs.glb", accent: "#dd8f8b", sci: "Pulmones", hotspots: [
    ["trachea", [0, 1.6, 0.2]], ["right-lung", [-1.2, 0.1, 0.7]], ["left-lung", [1.2, 0.1, 0.7]], ["bronchus", [-0.03, 0.3, 0.35]], ["base", [-1.14, -1.2, 1]]] },
  { id: "liver", model: "assets/models/liver.glb", accent: "#b86858", sci: "Hepar", hotspots: [
    ["right-lobe", [-0.75, 0.35, 0.75]], ["left-lobe", [0.85, 0.25, 0.75]], ["portal", [0.1, -0.3, 0.82]]] },
  { id: "kidneys", model: "assets/models/kidneys.glb", accent: "#c96963", sci: "Renes", hotspots: [
    ["cortex", [-0.9, 0.55, 0.7]], ["medulla", [0.85, 0.2, 0.7]], ["ureter", [0.4, -1.1, 0.5]]] },
  { id: "eyeball", model: "assets/models/eyeball.glb", accent: "#7294b9", sci: "Oculus", hotspots: [
    ["cornea", [-0.94, 0.05, 1.47]], ["iris", [-1.22, -0.53, 1.15]], ["optic", [1.61, -0.18, 0.54]]] },
  { id: "intestine", model: "assets/models/intestine.glb", accent: "#d78b77", sci: "Intestinum", hotspots: [
    ["duodenum", [0.6, 0.8, 0.75]], ["jejunum", [-0.45, 0.1, 0.82]], ["colon", [0.75, -0.55, 0.72]]] },
  { id: "pancreas", model: "assets/models/pancreas.glb", accent: "#c69a5e", sci: "Pancreas", hotspots: [
    ["head", [-1.32, -0.36, 0.55]], ["body", [0.05, 0.25, 0.45]], ["tail", [1.55, 0.3, 0.35]], ["duct", [-0.61, 0.39, 0.5]]] },
  { id: "skin", model: "assets/models/skin.glb", accent: "#c99277", sci: "Integumentum", hotspots: [
    ["epidermis", [-0.05, 0.88, 1.4]], ["dermis", [0.29, 0.05, 1.4]], ["hypodermis", [-0.39, -1.15, 1.4]], ["follicle", [0.89, -0.44, 1.4]]] },
  // Model prosedural berlapis (holo.js). Hotspot = jangkar tiap lapisan.
  { id: "cell", model: null, accent: "#2F7BFF", sci: "Cellula", layered: true, hotspots: [] },
];
const ORGAN_BY_ID = Object.fromEntries(ORGAN_LIST.map((o) => [o.id, o]));

/* Teks organ untuk bahasa aktif — menyatukan ORGAN_INFO (repo) dan CELL_INFO. */
function organText(id, lang) {
  return id === "cell" ? CELL_INFO[lang] : ORGAN_INFO[lang][id];
}
