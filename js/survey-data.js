/* HALO-XR · survey-data.js — 5 pertanyaan analisis kebutuhan (dipakai kuesioner & admin).
 * Kunci jawaban (value) harus sama dengan daftar yang divalidasi di database.rules.json. */
export const QUESTIONS = [
  { key: "q1", type: "scale",
    id: "Seberapa sulit memahami bentuk dan letak organ tubuh hanya dari buku atau gambar?",
    en: "How hard is it to understand the shape and position of organs from books or pictures alone?",
    options: [
      { v: 1, e: "😀", id: "Sangat mudah", en: "Very easy" }, { v: 2, e: "🙂", id: "Mudah", en: "Easy" },
      { v: 3, e: "😐", id: "Biasa saja", en: "Neutral" }, { v: 4, e: "😕", id: "Sulit", en: "Hard" },
      { v: 5, e: "😣", id: "Sangat sulit", en: "Very hard" }] },
  { key: "q2", type: "single",
    id: "Media apa yang paling sering dipakai saat belajar anatomi di kelas?",
    en: "Which media is used most often when learning anatomy in class?",
    options: [
      { v: "book", e: "📘", id: "Buku / LKS", en: "Textbook / worksheet" }, { v: "poster", e: "🖼️", id: "Gambar / poster", en: "Pictures / posters" },
      { v: "video", e: "🎬", id: "Video", en: "Video" }, { v: "torso", e: "🧍", id: "Model / torso", en: "Physical model / torso" },
      { v: "app3d", e: "📱", id: "Aplikasi 3D / AR / VR", en: "3D / AR / VR app" }] },
  { key: "q3", type: "single",
    id: "Pernahkah kamu belajar memakai media 3D, AR, VR, atau hologram?",
    en: "Have you ever learned with 3D, AR, VR or hologram media?",
    options: [
      { v: "never", e: "🙅", id: "Belum pernah", en: "Never" }, { v: "once", e: "🤏", id: "Pernah 1–2 kali", en: "Once or twice" },
      { v: "often", e: "🙌", id: "Sering", en: "Often" }] },
  { key: "q4", type: "scale",
    id: "Seberapa tertarik kamu belajar anatomi dengan hologram 3D yang bisa digerakkan dengan tangan atau suara?",
    en: "How interested are you in learning anatomy with a 3D hologram you control by hand or voice?",
    options: [
      { v: 1, e: "😴", id: "Tidak tertarik", en: "Not interested" }, { v: 2, e: "🤔", id: "Kurang tertarik", en: "Slightly" },
      { v: 3, e: "🙂", id: "Cukup tertarik", en: "Somewhat" }, { v: 4, e: "😃", id: "Tertarik", en: "Interested" },
      { v: 5, e: "🤩", id: "Sangat tertarik", en: "Very interested" }] },
  { key: "q5", type: "single",
    id: "Organ apa yang paling ingin kamu lihat dalam bentuk hologram 3D?",
    en: "Which organ would you most like to see as a 3D hologram?",
    options: [
      { v: "heart", e: "❤️", id: "Jantung", en: "Heart" }, { v: "brain", e: "🧠", id: "Otak", en: "Brain" },
      { v: "lungs", e: "🫁", id: "Paru-paru", en: "Lungs" }, { v: "eye", e: "👁️", id: "Mata", en: "Eye" },
      { v: "digestive", e: "🌀", id: "Pencernaan", en: "Digestive system" }, { v: "kidneys", e: "🫘", id: "Ginjal", en: "Kidneys" },
      { v: "skin", e: "✋", id: "Kulit", en: "Skin" }, { v: "cell", e: "🔬", id: "Sel", en: "Cell" }] },
];

/* Profil opsional (tanpa nama — kuesioner anonim). */
export const PROFILE = {
  grade: { id: "Kelas", en: "Grade", options: [{ v: "X", id: "X", en: "10" }, { v: "XI", id: "XI", en: "11" }, { v: "XII", id: "XII", en: "12" }, { v: "other", id: "Lainnya", en: "Other" }] },
  school: { id: "Sekolah", en: "School", options: [
    { v: "smamuh", id: "SMA Muhammadiyah PK Kottabarat", en: "SMA Muhammadiyah PK Kottabarat" },
    { v: "man1", id: "MAN 1 Surakarta", en: "MAN 1 Surakarta" },
    { v: "sman4", id: "SMA Negeri 4 Surakarta", en: "SMA Negeri 4 Surakarta" },
    { v: "other", id: "Sekolah lain", en: "Other school" }] },
};

export const label = (q, v, lang) => (q.options.find((o) => o.v === v) || {})[lang] ?? v ?? "—";
export const SURVEY_URL = "https://haloxr-id.web.app/kuesioner.html";
