# Instruksi untuk Claude

- Setiap perubahan pada website WAJIB langsung di-commit dan di-push ke GitHub (`origin main`) tanpa menunggu diminta.
- Vercel (proyek `portfolio-live-streaming`) otomatis deploy dari branch `main`; link publik: https://portfolio-live-streaming.vercel.app
- Situs statis tanpa build: `index.html` + folder `media/`. Alamat video diatur di blok `VIDEO SOURCES` dalam `index.html`.
- Setelah push, cek bahwa deployment Vercel untuk commit tersebut berstatus READY.

## Menambah frame ke portfolio (alur dengan Studio Frame Live)
- Pelacak kerja: artifact Studio Frame Live https://claude.ai/artifact/SQfEmuYk92KDrFoyvmH95m (koleksi `tasks`; field `status`, `brand`, `tema`).
- Hanya request berstatus `selesai` yang masuk portfolio. `frames.json` → `source.tracker` mencatat id request yang sudah masuk.
- File video diambil dari komputer user (folder kerja lokal, mis. D:\FREELANCE CLAVEY\...), bukan dari Drive. Pakai versi gabungan/jadi: file `PREVIEW ...` atau `FRAME ...` di folder `FA`. Abaikan ALPHA CHANNEL, GREEN SCREEN, GS, BLUE SCREEN, PODIUM.
- Langkah: `python3 tools/add_frame.py SUMBER.mp4 KEY` → tambah entri di `frames.json` (terbaru di atas) → `python3 tools/build_frames.py` → cek → commit & push.
- Kategori brand: FreshCare, Madu TJ, Hotin Cream, Tresno Joyo, TJ Joybee, MyWell, Welmove, Om3heart, Fitbes, Fresh Living, Bebio masuk grup `ultra-sakti` (PT Ultra Sakti). VIVA → `viva`, Red-A → `reda`. Grup baru ditambah di `groups`.
