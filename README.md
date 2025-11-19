# TalentaTalk - Sistem Pelatihan Pengucapan & Wawancara Bahasa Inggris

> **⚠️ Status Proyek:** Development Preview / Purwarupa Fungsional (Tugas Akhir D3)

---

## 📢 Pemberitahuan Penting: Kualitas Kode & Hak Cipta

Repositori ini berfungsi sebagai **arsip portofolio** dan **bukti teknis** dari pengerjaan Tugas Akhir di Politeknik Negeri Bandung.

**Harap perhatikan konteks berikut terkait kode sumber (source code) ini:**

1.  **Versi Pengembangan (Development Snapshot):** Kode yang tersimpan di sini adalah versi snapshot saat sidang akhir. Ini adalah **purwarupa fungsional** di mana semua fitur berjalan sepenuhnya, namun **belum** melalui tahap *Refactoring*, penerapan *Clean Code* menyeluruh, dan *Performance Optimization* tingkat lanjut.
2.  **Hak Kekayaan Intelektual (HKI) & NDA:** Versi final yang siap produksi (*production-ready*) yang telah dioptimasi adalah milik bersama antara pengembang, rekan tim, dan dosen pembimbing, serta diserahkan kepada **Perusahaan Mitra**. Karena adanya **Non-Disclosure Agreement (NDA)** dan perlindungan HKI, versi final tersebut tidak dipublikasikan di sini.
3.  **Tujuan:** Repositori ini ditujukan semata-mata untuk **demonstrasi kemampuan teknis**, logika pemrograman, integrasi sistem (Mobile-Web-Backend), dan implementasi AI yang telah dibangun selama masa pengembangan.

---

## 📖 Ringkasan Proyek

**TalentaTalk** adalah platform terintegrasi yang dirancang untuk membantu pengguna meningkatkan kemampuan berbicara bahasa Inggris melalui umpan balik berbasis AI. Sistem ini menciptakan ekosistem pembelajaran yang menghubungkan aplikasi seluler untuk pelajar dan dasbor web untuk manajemen konten.

**Fitur Utama:**
* **Penilaian Pengucapan (Pronunciation):** Menggunakan AI untuk menganalisis akurasi pengucapan pengguna hingga level fonem (huruf bunyi).
* **Simulasi Wawancara (Interview):** Simulasi wawancara kerja berbasis AI yang memberikan pertanyaan tindak lanjut (follow-up) secara dinamis serta umpan balik terkait tata bahasa (grammar) dan kelancaran (WPM).
* **Pelacakan Progres:** Analitik mendalam untuk memantau perkembangan pengguna bagi admin dan mentor.

---

## 📂 Struktur Repositori

Proyek ini menggunakan struktur **Monorepo** yang mencakup tiga komponen utama:

| Folder | Komponen | Deskripsi Teknologi |
| :--- | :--- | :--- |
| `front-end-talent-english` | **Aplikasi Mobile** | Dibangun dengan **Flutter (Dart)**. [cite_start]Menggunakan arsitektur BLoC untuk manajemen state dan menangani perekaman audio real-time. [cite: 1] |
| `Front-End-English-Manajemen` | **Web Dashboard** | Dibangun dengan **React.js 19 (Vite)** & Material UI. [cite_start]Berfungsi untuk manajemen pengguna, konten, dan bulk import data via Excel. [cite: 3498] |
| `Backend_TalentaTalk` | **Backend API** | Dibangun dengan **FastAPI (Python)**. [cite_start]Berfungsi sebagai otak pemrosesan AI (ASR, LLM Wrapper) dan manajemen database. [cite: 5644] |

---

## 🛠 Teknologi & Tools

* **Bahasa Pemrograman:** Dart, JavaScript/JSX, Python.
* **Database:** PostgreSQL & SQLAlchemy.
* **Infrastruktur:** Docker & Docker Compose.
* **AI & Machine Learning:**
    * **ASR:** HuggingFace Transformers (`wav2vec2`) untuk pengenalan fonem.
    * **LLM:** Integrasi Google Gemini API untuk logika wawancara.
    * **Transkripsi:** OpenAI Whisper.

---

## 👤 Kredit & Pengembang

Proyek ini dikembangkan sebagai bagian dari Tugas Akhir di **Politeknik Negeri Bandung**.

**Pengembang Utama:**
* **Vico Triansyah Nasril** - Full Stack Developer (Mobile, Web, & Backend)

**Kontributor & Supervisi:**
* **Rekan Tim:** (Turut berkontribusi dalam pengembangan sistem)
* **Dosen Pembimbing:** (Memberikan arahan teknis dan akademis)
* **Perusahaan Mitra:** (Pihak penerima manfaat implementasi sistem)

---
*© 2025 Vico Triansyah Nasril & Tim. Kode ini diunggah untuk keperluan portofolio dan verifikasi akademik.*
