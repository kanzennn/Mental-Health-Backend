# Backend Compro API

REST API backend untuk analisis teks kesehatan mental menggunakan FastAPI, PostgreSQL, dan layanan AI eksternal.

## Daftar Isi

- [Teknologi](#teknologi)
- [Arsitektur](#arsitektur)
- [Instalasi](#instalasi)
- [Konfigurasi](#konfigurasi)
- [Menjalankan Aplikasi](#menjalankan-aplikasi)
- [Migrasi Database](#migrasi-database)
- [Dokumentasi API](#dokumentasi-api)
  - [Auth](#auth)
  - [Analysis](#analysis)
- [Struktur Proyek](#struktur-proyek)

---

## Teknologi

| Teknologi | Versi | Keterangan |
|-----------|-------|------------|
| Python | 3.11+ | |
| FastAPI | 0.135.3 | Web framework |
| SQLAlchemy | 2.0.49 | ORM |
| PostgreSQL | - | Database |
| Alembic | 1.18.4 | Migrasi database |
| Argon2 | 23.1.0 | Hashing password |
| python-jose | 3.5.0 | JWT token |
| httpx | 0.28.1 | HTTP client untuk layanan AI |
| uvicorn | 0.44.0 | ASGI server |

---

## Arsitektur

Aplikasi menggunakan layered architecture:

```
app/
├── routes/       # HTTP handler (controller)
├── services/     # Business logic
├── repositories/ # Database access
├── models/       # SQLAlchemy models
├── schemas/      # Pydantic request/response
└── core/         # Config, security, database
```

Sistem terhubung ke dua layanan AI eksternal:

- **AI API** (`AI_API_URL`) — transkripsi audio ke teks
- **XAI API** (`XAI_API_URL`) — prediksi kesehatan mental + penjelasan LIME via endpoint `/explain`

### Alur Analisis

Setiap kali pengguna mengirim teks atau audio, satu panggilan ke `XAI_API_URL/explain` dieksekusi. Hasilnya disimpan ke dua tabel:

```
POST /analysis/text atau /analysis/audio
        │
        ▼
  XAI_API_URL/explain
        │
        ├──► analysis_sessions  (input teks, top category, confidence, model_version, method)
        └──► analysis_results   (skor + penjelasan LIME per kategori, diurutkan descending by score)
```

### Skema Database

| Tabel | Kolom utama |
|-------|-------------|
| `users` | `id`, `name`, `email`, `password` |
| `analysis_sessions` | `id`, `user_id`, `input_text`, `category`, `confidence`, `model_version`, `method` |
| `analysis_results` | `id`, `analysis_session_id`, `result_type`, `score`, `detail` (JSON LIME) |

---

## Instalasi

```bash
# Clone repository
git clone <repo-url>
cd backend_compro

# Buat virtual environment
python -m venv .venv

# Aktifkan virtual environment
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Konfigurasi

Salin `.env.example` menjadi `.env` dan sesuaikan nilainya:

```bash
cp .env.example .env
```

| Variabel | Default | Keterangan |
|----------|---------|------------|
| `DB_HOST` | `localhost` | Host PostgreSQL |
| `DB_PORT` | `5432` | Port PostgreSQL |
| `DB_USER` | `postgres` | Username database |
| `DB_PASSWORD` | `password` | Password database |
| `DB_NAME` | `compro_db` | Nama database |
| `SECRET_KEY` | `kuncirahasia` | Secret key JWT (wajib diganti di produksi) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Masa berlaku token (menit) |
| `CORS_ORIGINS` | `http://localhost:3000,...` | Daftar origin yang diizinkan, dipisah koma |
| `AI_API_URL` | `http://localhost:8001` | URL layanan transkripsi audio |
| `XAI_API_URL` | `http://localhost:8002` | URL layanan prediksi + XAI |

---

## Menjalankan Aplikasi

```bash
uvicorn app.main:app --reload
```

Aplikasi berjalan di `http://localhost:8000`.

Swagger UI tersedia di `http://localhost:8000/docs`.

---

## Migrasi Database

```bash
# Jalankan semua migrasi
alembic upgrade head

# Rollback ke versi sebelumnya
alembic downgrade -1
```

---

## Dokumentasi API

Semua endpoint berada di bawah prefix `/api/v1`.

Format respons standar:

```json
{
  "success": true,
  "message": "...",
  "data": { ... }
}
```

---

### Auth

Base path: `/api/v1/auth`

#### `POST /register`

Mendaftarkan pengguna baru.

**Request Body:**
```json
{
  "name": "string",
  "email": "user@example.com",
  "password": "string"
}
```

**Response `200`:**
```json
{
  "success": true,
  "message": "Registration successful",
  "data": {
    "id": "uuid",
    "name": "string",
    "email": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
}
```

**Error:**
- `400` — Email sudah terdaftar

---

#### `POST /login`

Login dan mendapatkan JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "string"
}
```

**Response `200`:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "string",
    "token_type": "bearer"
  }
}
```

**Error:**
- `401` — Email atau password salah

---

#### `GET /me`

Mengambil data pengguna yang sedang login.

**Header:** `Authorization: Bearer <token>`

**Response `200`:**
```json
{
  "success": true,
  "message": "User retrieved successfully",
  "data": {
    "id": "uuid",
    "name": "string",
    "email": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
}
```

---

#### `PUT /me`

Memperbarui nama dan/atau email pengguna.

**Header:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "string (opsional)",
  "email": "user@example.com (opsional)"
}
```

**Response `200`:** Data pengguna terbaru.

---

#### `PUT /me/password`

Mengganti password pengguna.

**Header:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "old_password": "string",
  "new_password": "string"
}
```

**Error:**
- `400` — Password lama salah

---

### Analysis

Base path: `/api/v1/analysis`

Semua endpoint memerlukan header `Authorization: Bearer <token>`.

Modul ini menganalisis teks atau audio untuk mendeteksi indikasi **depresi**, **kecemasan**, dan **stres**. Setiap pengiriman teks/audio secara otomatis menjalankan prediksi dan penjelasan XAI (LIME) sekaligus — hasilnya tersimpan di `analysis_sessions` dan `analysis_results`.

#### `GET /`

Mengambil semua sesi analisis milik pengguna.

**Response `200`:**
```json
{
  "success": true,
  "message": "Sessions retrieved successfully",
  "data": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "input_text": "string",
      "category": "depression",
      "confidence": 0.87,
      "model_version": "v1",
      "method": "LIME",
      "created_at": "datetime",
      "updated_at": "datetime",
      "results": []
    }
  ]
}
```

---

#### `GET /{analysis_session_id}`

Mengambil detail satu sesi analisis beserta skor per kategori.

**Path Param:** `analysis_session_id` (UUID)

**Response `200`:**
```json
{
  "success": true,
  "message": "Analysis Session retrieved successfully",
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "input_text": "string",
    "category": "depression",
    "confidence": 0.87,
    "model_version": "v1",
    "method": "LIME",
    "created_at": "datetime",
    "updated_at": "datetime",
    "results": [
      {
        "id": "uuid",
        "analysis_session_id": "uuid",
        "result_type": "depression | anxiety | stress",
        "score": 87.5,
        "detail": { "kata1": 0.45, "kata2": -0.12, "kata3": 0.08 },
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ]
  }
}
```

`results` diurutkan descending berdasarkan `score`.

**Error:**
- `404` — Sesi tidak ditemukan

---

#### `POST /text`

Mengirim teks untuk dianalisis.

**Request Body:**
```json
{
  "input_text": "string (tidak boleh kosong)"
}
```

**Response `200`:**
```json
{
  "success": true,
  "message": "Analysis created successfully",
  "data": {
    "id": "uuid",
    "user_id": "uuid",
    "input_text": "string",
    "category": "depression",
    "confidence": 0.87,
    "model_version": "v1",
    "method": "LIME",
    "created_at": "datetime",
    "updated_at": "datetime",
    "results": [
      {
        "id": "uuid",
        "analysis_session_id": "uuid",
        "result_type": "depression",
        "score": 87.5,
        "detail": { "saya": 0.45, "merasa": 0.38, "cemas": -0.12 },
        "created_at": "datetime",
        "updated_at": "datetime"
      },
      {
        "result_type": "anxiety",
        "score": 10.2,
        "detail": { ... }
      },
      {
        "result_type": "stress",
        "score": 2.3,
        "detail": { ... }
      }
    ]
  }
}
```

`results` diurutkan descending berdasarkan `score`. Field `detail` berisi bobot kontribusi tiap kata dari LIME (positif = mendukung kategori, negatif = menentang).

**Proses internal:**
1. Teks dikirim ke `XAI_API_URL/explain`
2. Top kategori, confidence, model_version, method disimpan ke `analysis_sessions`
3. Skor + penjelasan LIME per kategori disimpan ke `analysis_results`

**Error:**
- `502` — Layanan XAI error
- `504` — Layanan XAI timeout (>120 detik)

---

#### `POST /audio`

Mengirim file audio untuk ditranskripsi lalu dianalisis.

**Form Data:** `file` (audio file)

**Response `200`:** Format sama dengan `POST /text`.

**Proses internal:**
1. Audio dikirim ke `AI_API_URL/transcribe`
2. Teks hasil transkripsi diproses seperti `POST /text`

**Error:**
- `422` — Transkripsi menghasilkan teks kosong
- `502` / `504` — Error layanan AI

---

#### `DELETE /{analysis_session_id}`

Menghapus sesi analisis.

**Path Param:** `analysis_session_id` (UUID)

**Error:**
- `404` — Sesi tidak ditemukan

---


## Struktur Proyek

```
backend_compro/
├── app/
│   ├── main.py                    # Entry point FastAPI
│   ├── dependencies.py            # Dependency injection (DB, auth, service)
│   ├── core/
│   │   ├── config.py              # Environment settings
│   │   ├── cors.py                # CORS setup
│   │   ├── database.py            # SQLAlchemy engine & session
│   │   ├── exception_handler.py   # Global exception handler
│   │   ├── labels.py              # Mapping label AI ke bahasa Inggris
│   │   └── security.py            # JWT & Argon2 password hashing
│   ├── middlewares/
│   │   └── logger_middleware.py   # HTTP request logging
│   ├── models/
│   │   ├── user_model.py
│   │   ├── analysis_session_model.py  # + category, confidence, model_version, method
│   │   └── analysis_result_model.py
│   ├── repositories/              # Data access layer
│   ├── routes/
│   │   ├── auth_router.py
│   │   └── analysis_router.py
│   ├── schemas/                   # Pydantic schemas
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── analysis_service.py    # Memanggil /explain + menyimpan semua hasil
│   │   └── transcriber_service.py
│   └── utils/
│       └── response.py            # ResponseBuilder helper
├── alembic/
│   └── versions/
│       ├── 0001_init_schema.py    # Migrasi awal
│       ├── 0002_alter_analysis_results_detail_to_json.py  # detail: Text → JSON
│       └── 0003_merge_prediction_xai_into_analysis_sessions.py  # hapus predictions & xai_results, tambah kolom ke analysis_sessions
├── alembic.ini
├── requirements.txt
└── .env.example
```
