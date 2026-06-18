<div align="center">

# 🔍 VortexOSINT

**Toolkit OSINT modern, lengkap & 100% gratis** — investigasi *username*, *email*, *domain*, *IP*, dan *nomor telepon* dari sumber publik tanpa API key berbayar.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![100% Free](https://img.shields.io/badge/cost-100%25%20free-success.svg)](#)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

</div>

---

## ✨ Fitur

| Modul | Kemampuan | Sumber (gratis, tanpa API key) |
|-------|-----------|-------------------------------|
| 👤 **username** | Cek keberadaan akun di **40+ platform** secara paralel | Halaman profil publik |
| 📧 **email** | Validasi sintaks, klasifikasi domain, lookup **Gravatar**, cek **kebocoran data** | Gravatar, XposedOrNot |
| 🌐 **domain** | **WHOIS**, record **DNS**, enumerasi **subdomain**, sidik jari HTTP | crt.sh, DNS publik, WHOIS |
| 📡 **ip** | **Geolokasi**, ASN/ISP, reverse DNS, flag VPN/Proxy/Hosting | ip-api.com |
| ☎️ **phone** | Validasi, operator, wilayah, zona waktu (offline) | Google libphonenumber |

Plus:
- 🎨 Output terminal cantik dengan **rich** (otomatis fallback ke teks biasa)
- 📄 Ekspor laporan ke **JSON** dan **HTML** yang rapi
- ⚡ Pemindaian **concurrent** (cepat)
- 🔌 Arsitektur modular — mudah menambah sumber baru
- 🆓 **Tanpa biaya, tanpa API key wajib, sepenuhnya open source**

---

## 🚀 Instalasi

```bash
git clone https://github.com/0xgetz/VortexOSINT.git
cd VortexOSINT
pip install -r requirements.txt

# (opsional) install sebagai perintah global `vortex`
pip install -e .
```

> Butuh Python 3.8+. Semua dependensi gratis dan open source.

---

## 🧑‍💻 Penggunaan

```bash
# Cari username di 40+ situs
python vortex.py username johndoe

# Investigasi email (Gravatar + kebocoran data)
python vortex.py email someone@example.com

# Recon domain (WHOIS, DNS, subdomain)
python vortex.py domain example.com

# Geolokasi IP
python vortex.py ip 8.8.8.8

# Profil nomor telepon
python vortex.py phone "+6281234567890"
python vortex.py phone "081234567890" --region ID
```

### Ekspor laporan

```bash
# Simpan hasil ke JSON dan HTML
python vortex.py domain example.com --json --html

# Tentukan path keluaran sendiri
python vortex.py username johndoe --json hasil.json --html laporan.html
```

Jika diinstal via `pip install -e .`, gunakan perintah pendek `vortex` di mana saja:

```bash
vortex ip 1.1.1.1 --html
```

---

## 📂 Struktur Proyek

```
VortexOSINT/
├── vortex.py                 # Peluncur CLI
├── vortexosint/
│   ├── cli.py                # Antarmuka baris perintah
│   ├── core/
│   │   ├── http.py           # Sesi HTTP + concurrency
│   │   ├── console.py        # Output rich/plaintext
│   │   └── report.py         # Ekspor JSON/CSV/HTML
│   └── modules/
│       ├── username.py       # Enumerasi 40+ situs
│       ├── email.py          # Gravatar + breach
│       ├── domain.py         # WHOIS/DNS/subdomain
│       ├── ip.py             # Geolokasi & jaringan
│       └── phone.py          # Parsing nomor telepon
├── requirements.txt
├── setup.py
└── README.md
```

---

## 🗺️ Roadmap

- [ ] Modul metadata gambar (EXIF)
- [ ] Pencarian kebocoran kredensial tambahan
- [ ] Mode interaktif (TUI)
- [ ] Plugin sumber data komunitas
- [ ] Ekspor PDF

Punya ide? Buka [issue](https://github.com/0xgetz/VortexOSINT/issues) atau kirim PR!

---

## ⚖️ Disclaimer Etika & Hukum

VortexOSINT dibuat **hanya untuk tujuan edukasi, riset keamanan, dan investigasi yang sah**.
Gunakan **hanya** pada target yang Anda miliki atau yang Anda punya izin eksplisit untuk diselidiki.
Seluruh data yang diakses bersifat **publik**. Penyalahgunaan untuk pelecehan, *stalking*, atau aktivitas ilegal **sepenuhnya menjadi tanggung jawab pengguna**. Penulis tidak bertanggung jawab atas penyalahgunaan.

---

## 📜 Lisensi

Dirilis di bawah [Lisensi MIT](LICENSE) — bebas digunakan, dimodifikasi, dan didistribusikan.

<div align="center">
Dibuat dengan ❤️ untuk komunitas OSINT — <strong>100% gratis selamanya</strong>.
</div>
