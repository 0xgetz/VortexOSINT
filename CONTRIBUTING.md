# Berkontribusi ke VortexOSINT

Terima kasih atas minat Anda! 🎉 Kontribusi sangat diterima.

## Cara berkontribusi

1. **Fork** repositori ini.
2. Buat branch: `git checkout -b fitur/sumber-baru`.
3. Lakukan perubahan dan pastikan kode tetap rapi.
4. Commit: `git commit -m "Tambah sumber XYZ"`.
5. Push: `git push origin fitur/sumber-baru`.
6. Buka **Pull Request**.

## Menambah modul / sumber baru

- Modul baru ditempatkan di `vortexosint/modules/`.
- Gunakan helper di `vortexosint/core/http.py` untuk request (mendukung retry & concurrency).
- Gunakan `vortexosint/core/console.py` untuk output agar konsisten.
- Setiap modul harus mengembalikan `dict` agar bisa diekspor ke JSON/HTML.
- **Hanya gunakan sumber gratis tanpa API key wajib.** Ini prinsip utama proyek.

## Aturan etika

- Jangan menambahkan fitur yang mengakses data **non-publik** atau melanggar ToS layanan.
- Jangan menambahkan teknik intrusif (brute force, eksploitasi, dsb.).

## Gaya kode

- Python 3.8+, ikuti PEP 8.
- Tambahkan docstring singkat pada fungsi publik.
- Hindari dependensi berbayar.

Selamat berkontribusi! 🚀
