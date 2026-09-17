# Pipeline Cloud & KNIME

Bab ini membahas perancangan arsitektur integrasi data berbasis cloud dan otomatisasi alur kerja analitik menggunakan **KNIME Analytics Platform** untuk pemantauan data polutan di Kota Sumenep.

---

## 1. Arsitektur Pipeline Data

Pipeline data dirancang untuk mengalirkan data deret waktu polutan dari sumber pengunduhan ke penyimpanan database terkelola di cloud, lalu diproses secara otomatis di KNIME:

1. **Ingestion Layer**: Pengambilan data deret waktu satelit Sentinel-5P melalui API openEO / Google Earth Engine.
2. **Storage Layer (Cloud Database)**: Penyimpanan data time series bersih ke dalam database cloud terkelola (Aiven Cloud Database).
3. **Analytics & Transformation Layer**: Pengolahan alur data, integrasi, dan eksekusi model menggunakan alur kerja visual KNIME.
4. **Reporting Layer**: Ekspor fitur dan visualisasi ringkasan untuk kebutuhan buku digital / dashboard.

---

## 2. Integrasi Cloud Database (Aiven)

Penyimpanan terpusat menggunakan layanan **Aiven Cloud Database** memastikan data polutan tersimpan secara aman, terkelola, dan dapat diakses kapan saja oleh pipeline analitik tanpa membebani memori lokal.

```python
import pandas as pd
from sqlalchemy import create_engine

# Konfigurasi koneksi database Aiven
DB_HOST = "your-aiven-host.aivencloud.com"
DB_PORT = "12345"
DB_NAME = "defaultdb"
DB_USER = "avnadmin"
DB_PASSWORD = "your_password"

# Membuat URI koneksi PostgreSQL/MySQL
connection_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
engine = create_engine(connection_url)

# Mengunggah data bersih ke Cloud Database
df_clean = pd.read_csv("Polutan-Sumenep-Clean.csv")
df_clean.to_sql("polutan_sumenep", engine, if_exists="replace", index=False)
print("Data polutan berhasil disimpan ke Aiven Cloud!")