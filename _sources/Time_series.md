# Analisis Time Series

Tahap **Analisis Time Series** dilakukan untuk mengeksplorasi pola temporal dari tiga parameter polutan udara, yaitu **Karbon Monoksida (CO)**, **Nitrogen Dioksida (NO₂)**, dan **Sulfur Dioksida (SO₂)** di Kecamatan Kota Sumenep.

Data yang digunakan pada tahap ini merupakan data hasil **Data Preparation** yang telah melalui penyesuaian format, deteksi *outlier*, serta penanganan *missing value*. Masing-masing dataset memiliki **365 observasi harian** pada periode **31 Agustus 2025 hingga 30 Agustus 2026**.

Visualisasi deret waktu dilakukan secara terpisah untuk setiap polutan agar perubahan nilai CO, NO₂, dan SO₂ terhadap waktu dapat diamati dengan lebih jelas.

---

## 1. Memuat Data Time Series Hasil Cleaning

Dataset yang digunakan terdiri dari:

- `CO_Kota_Sumenep_clean.csv`
- `NO2_Kota_Sumenep_clean.csv`
- `SO2_Kota_Sumenep_clean.csv`

### 1.1 Code Memuat Data

```python
import pandas as pd
import matplotlib.pyplot as plt

co = pd.read_csv("CO_Kota_Sumenep_clean.csv")
no2 = pd.read_csv("NO2_Kota_Sumenep_clean.csv")
so2 = pd.read_csv("SO2_Kota_Sumenep_clean.csv")

# Mengubah kolom tanggal menjadi datetime
co["date"] = pd.to_datetime(co["date"])
no2["date"] = pd.to_datetime(no2["date"])
so2["date"] = pd.to_datetime(so2["date"])

print("Shape CO :", co.shape)
print("Shape NO2:", no2.shape)
print("Shape SO2:", so2.shape)
```

Ketiga dataset memiliki struktur yang sama, yaitu **365 baris dan 2 kolom**. Kolom `date` menunjukkan waktu pengamatan, sedangkan kolom kedua berisi nilai masing-masing polutan.

| Dataset | Jumlah Observasi | Kolom |
|---|---:|---|
| CO | 365 | `date`, `CO` |
| NO₂ | 365 | `date`, `NO2` |
| SO₂ | 365 | `date`, `SO2` |

