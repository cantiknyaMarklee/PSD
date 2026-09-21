# Business Understanding

## Latar Belakang

Kualitas udara merupakan salah satu aspek penting dalam pemantauan kondisi lingkungan. Beberapa polutan udara yang dapat digunakan untuk mengamati perubahan kondisi kualitas udara antara lain **Carbon Monoxide (CO)**, **Nitrogen Dioxide (NO₂)**, dan **Sulfur Dioxide (SO₂)**.

Pada proyek ini dilakukan analisis terhadap data deret waktu (*time series*) polutan **CO, NO₂, dan SO₂** pada wilayah **Kecamatan Kota Sumenep**. Data polutan diperoleh dari data satelit **Sentinel-5P** melalui layanan **openEO Copernicus Data Space Ecosystem**.

Analisis tidak hanya dilakukan terhadap nilai polutan dari waktu ke waktu, tetapi dilanjutkan dengan ekstraksi karakteristik sinyal menggunakan **Time Series Feature Extraction Library (TSFEL)**. Hasil ekstraksi fitur kemudian digunakan dalam proses reduksi dimensi dan *clustering* untuk mengetahui pola pengelompokan data berdasarkan karakteristik masing-masing polutan.

---

## Permasalahan

Berdasarkan latar belakang tersebut, permasalahan yang dianalisis dalam proyek ini adalah:

1. Bagaimana karakteristik deret waktu (*time series*) dari polutan **CO, NO₂, dan SO₂** di Kecamatan Kota Sumenep?
2. Bagaimana karakteristik statistik, temporal, dan spektral dari masing-masing polutan berdasarkan hasil ekstraksi fitur?
3. Bagaimana membentuk representasi data menggunakan **68 fitur TSFEL** dari masing-masing polutan?
4. Bagaimana hasil penggabungan fitur dari tiga polutan, yaitu **68 fitur CO, 68 fitur NO₂, dan 68 fitur SO₂**, sehingga menghasilkan **204 fitur**?
5. Bagaimana melakukan reduksi dimensi data menggunakan **Principal Component Analysis (PCA)**?
6. Bagaimana menentukan jumlah cluster pada **K-Means Clustering** dan mengevaluasi kualitas hasil clustering?
7. Bagaimana hasil clustering apabila analisis dilakukan kembali pada **68 fitur masing-masing polutan**?

---

## Tujuan

Tujuan dari proyek ini adalah:

1. Melakukan eksplorasi data deret waktu pada polutan **CO, NO₂, dan SO₂**.
2. Mengekstraksi karakteristik sinyal polutan menggunakan **TSFEL**.
3. Memahami fitur yang digunakan melalui konsep dasar, deskripsi fitur, dan contoh perhitungan sebelum proses ekstraksi fitur.
4. Menghasilkan **68 fitur** untuk setiap polutan CO, NO₂, dan SO₂.
5. Menggabungkan fitur ketiga polutan menjadi **204 fitur** untuk analisis clustering.
6. Melakukan reduksi dimensi menggunakan **PCA hingga PCA1–PCA37**.
7. Menentukan jumlah cluster pada **K-Means Clustering** serta mengevaluasi kualitas cluster.
8. Melakukan analisis clustering secara terpisah pada **68 fitur CO, NO₂, dan SO₂** menggunakan workflow KNIME.

---

## Alur Analisis

Secara umum, tahapan yang dilakukan pada proyek ini meliputi:

**Pengambilan Data → Eksplorasi Time Series → Ekstraksi Fitur TSFEL → Penggabungan Fitur CO, NO₂, dan SO₂ → Normalisasi Data → PCA → K-Means Clustering → Evaluasi Cluster**

Selain analisis gabungan 204 fitur, clustering juga dilakukan pada **68 fitur masing-masing polutan** untuk melihat hasil pengelompokan CO, NO₂, dan SO₂ secara terpisah.