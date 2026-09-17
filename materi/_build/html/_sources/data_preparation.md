# Data Preparation

Tahap **Data Preparation** bertujuan untuk membersihkan, mentransformasikan, dan menstrukturkan data mentah deret waktu konsentrasi gas $NO_2$ hasil ekstraksi satelit (Sentinel-5P / Google Earth Engine) sebelum dilakukan ekstraksi fitur sinyal (*TSFEL*) dan analisis lanjutan.

---

##  Pembersihan Data (*Data Cleaning*)

Data penginderaan jauh (*remote sensing*) sering kali memiliki *gap* atau nilai kosong (*missing values*) akibat tutupan awan (*cloud masking*) tebal atau ketidaktersediaan citra satelit pada hari tertentu.

### Penanganan Missing Values
1. **Pemeriksaan Gap Tanggal**: Memastikan indeks temporal bersifat harian secara kontinu tanpa ada tanggal yang melompat.
2. **Imputasi Interpolasi Temporal**: Mengisi nilai kosong menggunakan metode interpolasi linear atau *forward-fill* (*ffill*) / *backward-fill* (*bfill*), tergantung pada pola gap data:
