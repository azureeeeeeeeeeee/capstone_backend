# Quickstart

Panduan singkat untuk menjalankan proyek ini,

## Requirements
- Python 3.10+
- pip
- virtualenv (opsional)

## 1. Clone Repository
```bash
git clone https://github.com/azureeeeeeeeeeee/capstone_backend.git
cd capstone_backend
```

## 2. Buat Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
```

## 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## 5. Migrate Database
```bash
python manage.py migrate
```

## 6. Buat Superuser
```bash
python manage.py createsupueruser
```

## 7. Jalankan Seeder
```bash
python manage.py seed
```

## 8. Jalankan Server
```bash
python manage.py runserver
```

## 9. Ubah role user yang baru dibuat
Masuk ke admin panel ke url di bawah, dan ubah role user ke role yang ingin dicoba. 
```bash
/admin/
```

Server berjalan di:
```
http://127.0.0.1:8000
```

## 10. API Documentation
Swagger dapat diakses di:
```
/swagger
```