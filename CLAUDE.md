# Instruksi untuk Claude

- Setiap perubahan pada website WAJIB langsung di-commit dan di-push ke GitHub (`origin main`) tanpa menunggu diminta.
- Vercel (proyek `portfolio-live-streaming`) otomatis deploy dari branch `main`; link publik: https://portfolio-live-streaming.vercel.app
- Situs statis tanpa build: `index.html` + folder `media/`. Alamat video diatur di blok `VIDEO SOURCES` dalam `index.html`.
- Setelah push, cek bahwa deployment Vercel untuk commit tersebut berstatus READY.
