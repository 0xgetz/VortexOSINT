<div align="center">

<img src="assets/logo.jpeg" alt="VortexOSINT — dark cyberpunk OSINT toolkit" width="100%">

# 🔍 VortexOSINT

**Toolkit OSINT modern, lengkap & 100% gratis** — investigasi *username*, *email*, *domain*, *IP*, *nomor telepon*, dan *metadata gambar* dari sumber publik tanpa API key berbayar.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![100% Free](https://img.shields.io/badge/cost-100%25%20free-success.svg)](#)
[![Plugins](https://img.shields.io/badge/plugins-supported-orange.svg)](#-plugin-komunitas)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

</div>

---

## ✨ Fitur

| Modul | Kemampuan | Sumber (gratis, tanpa API key) |
|-------|-----------|-------------------------------|
| 👤 **username** | Cek keberadaan akun di **40+ platform** secara paralel | Halaman profil publik |
| 📧 **email** | Validasi sintaks, klasifikasi domain, lookup **Gravatar**, cek **kebocoran data** & **infostealer** | Gravatar, XposedOrNot, HudsonRock |
| 🌐 **domain** | **WHOIS**, record **DNS**, enumerasi **subdomain**, sidik jari HTTP | crt.sh, DNS publik, WHOIS |
| 📡 **ip** | **Geolokasi**, ASN/ISP, reverse DNS, flag VPN/Proxy/Hosting | ip-api.com |
| ☎️ **phone** | Validasi, operator, wilayah, zona waktu (offline) | Google libphonenumber |
| 📷 **image** | Ekstraksi **EXIF**, info kamera, **koordinat GPS** + link peta | Offline (Pillow) |

Plus:
- 🎨 Output terminal cantik dengan **rich** (otomatis fallback ke teks biasa)
- 📄 Ekspor laporan ke **JSON**, **HTML**, dan **PDF**
- 🖥️ **Mode interaktif (TUI)** berbasis menu — tanpa perlu hafal flag
- 🧩 **Sistem plugin komunitas** — tambah sumber data sendiri tanpa mengubah inti
- ⚡ Pemindaian **concurrent** (cepat)
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

# Investigasi email (Gravatar + kebocoran data + infostealer)
python vortex.py email someone@example.com

# Recon domain (WHOIS, DNS, subdomain)
python vortex.py domain example.com

# Geolokasi IP
python vortex.py ip 8.8.8.8

# Profil nomor telepon
python vortex.py phone "+6281234567890"
python vortex.py phone "081234567890" --region ID

# Ekstraksi metadata & GPS dari gambar
python vortex.py image /path/to/photo.jpg
```

### 🖥️ Mode interaktif

Tidak ingin menghafal perintah? Jalankan menu terpandu:

```bash
python vortex.py interactive
```

### 📄 Ekspor laporan (JSON / HTML / PDF)

```bash
# Simpan hasil ke beberapa format sekaligus
python vortex.py domain example.com --json --html --pdf

# Tentukan path keluaran sendiri
python vortex.py username johndoe --json hasil.json --pdf laporan.pdf
```

Jika diinstal via `pip install -e .`, gunakan perintah pendek `vortex`:

```bash
vortex ip 1.1.1.1 --pdf
```

---

## 🧩 Plugin komunitas

VortexOSINT bisa diperluas tanpa menyentuh kode inti. Buat file `.py` yang mengekspos fungsi `register()`:

```python
# ~/.vortexosint/plugins/myplugin.py
from vortexosint.core import console, http

def run(target, **_):
    console.section(f"My plugin: {target}")
    # ... logika Anda ...
    return {"target": target, "result": "..."}

def register():
    return {
        "command": "myplugin",
        "help": "Deskripsi singkat plugin saya",
        "args": [{"name": "target", "help": "Apa yang dicari"}],
        "run": run,
    }
```

Lalu:

```bash
python vortex.py plugins              # daftar plugin terpasang
python vortex.py myplugin nilai-target
```

Plugin dimuat dari `vortexosint/plugins/`, `~/.vortexosint/plugins/`, atau direktori di env `VORTEX_PLUGINS`.
Lihat contoh bawaan: [`example_macvendor.py`](vortexosint/plugins/example_macvendor.py).

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
│   │   ├── report.py         # Ekspor JSON/CSV/HTML/PDF
│   │   ├── interactive.py    # Mode interaktif (TUI)
│   │   └── plugins.py        # Loader plugin komunitas
│   ├── modules/
│   │   ├── username.py       # Enumerasi 40+ situs
│   │   ├── email.py          # Gravatar + breach + infostealer
│   │   ├── domain.py         # WHOIS/DNS/subdomain
│   │   ├── ip.py             # Geolokasi & jaringan
│   │   ├── phone.py          # Parsing nomor telepon
│   │   └── exif.py           # Metadata & GPS gambar
│   └── plugins/
│       └── example_macvendor.py  # Plugin contoh
├── assets/
│   └── logo.jpeg             # Logo dark cyberpunk
├── requirements.txt
├── setup.py
└── README.md
```

---

## 🗺️ Roadmap

- [x] Modul metadata gambar (EXIF)
- [x] Pencarian kebocoran kredensial tambahan (HudsonRock infostealer)
- [x] Mode interaktif (TUI)
- [x] Plugin sumber data komunitas
- [x] Ekspor PDF

🎉 **Semua item roadmap awal telah selesai!** Punya ide baru? Buka [issue](https://github.com/0xgetz/VortexOSINT/issues) atau kirim PR.

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
