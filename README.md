# Tweet Classification API 🚀

Repositori ini berisi layanan Backend/API untuk proyek **Tweet Classification**, yang bertugas membangun pipeline NLP untuk mengklasifikasikan topik dari dataset Twitter ke dalam 6 kategori. 

Sistem ini dibangun menggunakan **FastAPI** untuk performa tinggi, **SQLite** untuk logging data prediksi secara dinamis, dan model klasifikasi dari Hugging Face yang dikembangkan oleh tim Machine Learning.

## 🛠️ Tech Stack
* **Framework:** FastAPI, Pydantic
* **Machine Learning:** Hugging Face `transformers`, PyTorch
* **Database:** SQLite, SQLAlchemy
* **Deployment:** Docker, Docker Compose
* **Server:** Uvicorn

## 📦 Fitur Utama
1. **Model Inference:** Mengunduh dan menjalankan model `.safetensors` secara lokal untuk prediksi label tweet.
2. **REST API Endpoint:** * `POST /predict`: Endpoint untuk memproses teks tweet murni dan mengembalikan label klasifikasi beserta *confidence score* dan probabilitas masing-masing kategori.
   * `GET /statistics`: Endpoint untuk melayani kebutuhan data Halaman Monitoring (Dashboard Panitia), mencakup total tweet, distribusi label, data tren harian, dan tabel log terbaru.
3. **Database Logging:** Setiap hasil klasifikasi otomatis disimpan ke dalam database SQLite.
4. **Error Handling:** Validasi input ketat. Menolak *payload* kosong, tipe data salah, atau *string* melebihi 10.000 karakter dengan respons `400 Bad Request`.

## 🚀 Cara Menjalankan secara Lokal (Tanpa Docker)

**1. Persiapan Environment**
Pastikan Python 3.10+ sudah terinstal. Buat *virtual environment* dan aktifkan:
```bash
python3 -m venv venv
source venv/bin/activate  # Untuk Mac/Linux
# venv\Scripts\activate   # Untuk Windows