/* HALO-XR · firebase.js — inisialisasi Firebase (Realtime Database + Auth) untuk kuesioner & admin.
 * Config web Firebase memang publik; keamanan data diatur oleh database.rules.json. */
import { initializeApp } from "https://www.gstatic.com/firebasejs/13.0.0/firebase-app.js";
import { getDatabase, connectDatabaseEmulator } from "https://www.gstatic.com/firebasejs/13.0.0/firebase-database.js";

export const firebaseConfig = {
  apiKey: "AIzaSyBS198isTb7WAKPOKdNQT0GbbHvBno8o4A",
  authDomain: "haloxr-id.firebaseapp.com",
  databaseURL: "https://haloxr-id-default-rtdb.firebaseio.com",
  projectId: "haloxr-id",
  storageBucket: "haloxr-id.firebasestorage.app",
  messagingSenderId: "800478133167",
  appId: "1:800478133167:web:5a5129435b4eb965830d5a",
};
export const app = initializeApp(firebaseConfig);
export const db = getDatabase(app);

/* Uji lokal dengan Firebase Emulator: buka http://localhost:PORT/kuesioner.html?emu */
export const EMU = location.hostname === "localhost" && new URLSearchParams(location.search).has("emu");
if (EMU) connectDatabaseEmulator(db, "127.0.0.1", 9000);

/* Email admin — harus sama dengan daftar di database.rules.json. */
export const ADMINS = ["mersif.storage3@gmail.com", "mersif.storage1@gmail.com"];
/* Akun username/password "admin" (Firebase Auth: admin@haloxr-id.web.app) — UID juga tercantum di database.rules.json. */
export const ADMIN_UID = "NnEzYdHTc3gne4IP0G62HNwcfDu2";
export const ADMIN_DOMAIN = "haloxr-id.web.app";
