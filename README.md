# MosaVerse

**AI-Powered Fashion Design Gallery & Management Platform**

MosaVerse adalah platform galeri desain fashion berbasis AI yang memungkinkan pengguna menjelajahi koleksi desain baju eksklusif, serta menyediakan panel admin untuk mengelola desain dan kategori dengan bantuan kecerdasan buatan.

---

## Fitur Utama

### Public (Pengunjung)
- **Galeri Desain** — Tampilan grid 4 kolom dengan card interaktif dan pagination
- **AI Smart Search** — Cari desain menggunakan bahasa alami (contoh: "baju kasual warna gelap")
- **Detail Desain** — Halaman detail dengan gambar, deskripsi, kategori, dan tanggal upload

### Admin Panel
- **Login Admin** — Autentikasi session-based dengan proteksi CSRF
- **Dashboard** — Statistik total desain, kategori, dan featured designs
- **Manage Designs** — CRUD desain dengan form + katalog side-by-side
  - Upload gambar dengan drag & drop
  - AI Generate Description — generate deskripsi otomatis menggunakan DeepSeek AI
  - AI Generate Category — kategorisasi otomatis
- **Kategori** — Kelola kategori desain

---

## Tech Stack

| Layer | Teknologi |
|-------|-----------|
| Backend | Django 5.0 + Django REST Framework |
| Database | MySQL / MariaDB (via XAMPP) |
| Frontend | HTML5 + Tailwind CSS + Vanilla JavaScript |
| AI | DeepSeek API (OpenAI-compatible) |
| Image Storage | Django media files (local filesystem) |

---

## Struktur Proyek

```
Mosaverse/
├── backend/                  # Django REST API
│   ├── apps/
│   │   ├── authentication/   # Login, logout, CSRF, session
│   │   ├── designs/          # CRUD desain & kategori
│   │   ├── ai/               # AI search, generate description & category
│   │   └── dashboard/        # Statistik dashboard
│   ├── config/               # Django settings, URLs, middleware
│   ├── media/                # Upload images
│   ├── .env                  # Environment variables
│   ├── manage.py
│   └── requirements.txt
├── frontend/                 # Static HTML frontend
│   ├── css/                  # Tailwind + custom styles
│   ├── js/                   # API client, page logic
│   ├── index.html            # Galeri utama
│   ├── detail.html           # Detail desain
│   ├── admin-login.html      # Login admin
│   ├── admin-dashboard.html  # Dashboard admin
│   └── admin-designs.html    # Manage desain (CRUD)
└── docs/design/              # Design reference images
```

---

## API Endpoints

### Authentication
| Method | Endpoint | Keterangan |
|--------|----------|------------|
| POST | `/api/login/` | Login admin |
| POST | `/api/logout/` | Logout admin |
| GET | `/api/csrf/` | Ambil CSRF token |
| GET | `/api/me/` | Info user yang sedang login |

### Designs (Public)
| Method | Endpoint | Keterangan |
|--------|----------|------------|
| GET | `/api/designs/` | List semua desain (paginated) |
| GET | `/api/designs/{id}/` | Detail desain |

### Designs (Admin Only)
| Method | Endpoint | Keterangan |
|--------|----------|------------|
| POST | `/api/designs/create/` | Buat desain baru |
| PUT | `/api/designs/{id}/update/` | Update desain |
| DELETE | `/api/designs/{id}/delete/` | Hapus desain |

### Categories
| Method | Endpoint | Keterangan |
|--------|----------|------------|
| GET/POST | `/api/categories/` | List / buat kategori |
| GET/PUT/DELETE | `/api/categories/{id}/` | Detail / update / hapus |

### AI (Admin Only)
| Method | Endpoint | Keterangan |
|--------|----------|------------|
| POST | `/api/ai/search/` | AI Smart Search |
| POST | `/api/ai/generate-description/` | Generate deskripsi dari judul |
| POST | `/api/ai/generate-category/` | Generate kategori dari deskripsi |

### Dashboard (Admin Only)
| Method | Endpoint | Keterangan |
|--------|----------|------------|
| GET | `/api/dashboard/stats/` | Statistik dashboard |

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- MySQL / MariaDB (via [XAMPP](https://www.apachefriends.org/))
- DeepSeek API key (untuk fitur AI)

### 1. Clone & Setup Backend

```bash
cd backend

# Buat virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Konfigurasi Environment

Salin `.env.example` menjadi `.env`:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# MySQL
DB_ENGINE=django.db.backends.mysql
DB_NAME=mosaverse_db
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306

# DeepSeek AI
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_API_URL=https://api.deepseek.com/v1
```

### 3. Setup Database

Pastikan MySQL/MariaDB sudah berjalan, lalu buat database:

```bash
# Opsi 1: Script otomatis
python setup_mysql.py

# Opsi 2: Manual
mysql -u root -e "CREATE DATABASE IF NOT EXISTS mosaverse_db;"
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Jalankan Backend

```bash
python manage.py runserver
```

Backend berjalan di `http://127.0.0.1:8000`

### 5. Jalankan Frontend

Buka frontend menggunakan Live Server (VS Code) atau server lokal lainnya di port 5500:

```bash
# Menggunakan VS Code Live Server extension
# Klik kanan frontend/index.html → Open with Live Server
```

Frontend berjalan di `http://127.0.0.1:5500`

---

## Default Admin Credentials

| Field | Value |
|-------|-------|
| Username | `admin` |
| Password | `admin123` |

> **Penting:** Ganti password setelah setup awal untuk keamanan.

---

## Halaman Frontend

| Halaman | URL | Deskripsi |
|---------|-----|-----------|
| Galeri | `/frontend/index.html` | Tampilan grid desain dengan AI search |
| Detail | `/frontend/detail.html?id={id}` | Detail desain |
| Admin Login | `/frontend/admin-login.html` | Halaman login admin |
| Dashboard | `/frontend/admin-dashboard.html` | Statistik & recent designs |
| Manage Designs | `/frontend/admin-designs.html` | Form tambah/edit + katalog |

---

## Catatan

- Django 5.0.x digunakan untuk kompatibilitas dengan MariaDB 10.4 (XAMPP default)
- CSRF protection di-disable untuk cross-origin request (frontend terpisah dari backend)
- Gambar desain disimpan di `backend/media/designs/`
- DeepSeek API menggunakan format OpenAI-compatible

---

## Lisensi

Project ini dibuat untuk keperluan UAS Pemrograman Web Lanjut.
