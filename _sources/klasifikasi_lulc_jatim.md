# UTS: Sistem Informasi Geografis dan Klasifikasi Tutupan Lahan Jawa Timur

## 1. Data Understanding dan Tujuan Analisis LULC

### 1.1 Tujuan analisis

Proyek ini mengkaji penggunaan dan tutupan lahan (*Land Use and Land Cover*, LULC) di Jawa Timur, termasuk Pulau Madura, menggunakan data penginderaan jauh Sentinel-2 Level-2A, sampel poligon, dan algoritma *machine learning*. Enam kelas operasional yang digunakan ialah **sawah, bangunan, mangrove, lahan hijau, laut, dan danau**.

Analisis ini diarahkan untuk mendukung pembahasan kebijakan spasial, terutama:

1. **Perlindungan sawah dan LP2B:** mengidentifikasi karakteristik spektral lokasi sampel persawahan sebagai masukan awal untuk kajian perlindungan lahan pertanian pangan berkelanjutan (UU No. 41 Tahun 2009).
2. **Konservasi mangrove pesisir:** membedakan contoh vegetasi mangrove dari kelas lain sebagai informasi pendukung kajian ekosistem pesisir (UU No. 27 Tahun 2007 sebagaimana diubah dengan UU No. 1 Tahun 2014).
3. **Perlindungan danau/ranu:** menganalisis contoh badan air darat. Status **danau alami** perlu diperiksa tersendiri; waduk atau kolam buatan tidak otomatis dikategorikan sebagai danau alami. Perpres No. 60 Tahun 2021 berkenaan dengan penyelamatan danau prioritas nasional, sehingga penerapannya perlu disesuaikan dengan danau yang memang tercakup.
4. **Dukungan evaluasi tata ruang:** menyediakan eksperimen klasifikasi tutupan lahan untuk bahan kajian RTRW Jawa Timur. Proyek ini **belum** melakukan *overlay* dengan layer zonasi RTRW resmi, sehingga belum dapat menyatakan kepatuhan atau pelanggaran tata ruang.

**Ruang lingkup keluaran:** evaluasi model pada 180 poligon sampel dan demonstrasi prediksi raster pada satu area contoh. Proyek ini **bukan** pemetaan lengkap seluruh Jawa Timur, dan satu periode citra tidak cukup untuk menghitung laju alih fungsi lahan dari waktu ke waktu.

### 1.2 Sumber data dan karakteristik Sentinel-2 MSI

Data reflektansi diperoleh melalui **Copernicus Data Space Ecosystem**, menggunakan koleksi **Sentinel-2 Level-2A (surface reflectance)** dan layanan Statistical API. Koleksi tersebut tidak dengan sendirinya membuktikan bahwa setiap akuisisi berasal khusus dari platform Sentinel-2A; identitas platform perlu diperiksa lewat metadata akuisisi apabila hendak diklaim secara spesifik.

Sensor MSI Sentinel-2 memiliki 13 band. Sepuluh band digunakan sebagai fitur langsung dalam model.

| Band | Spektrum | Panjang gelombang pusat (perkiraan) | Resolusi asli | Dipakai dalam model |
|---|---|---:|---:|---|
| B01 | Coastal aerosol | 443 nm | 60 m | Tidak |
| B02 | Blue | 490 nm | 10 m | Ya |
| B03 | Green | 560 nm | 10 m | Ya |
| B04 | Red | 665 nm | 10 m | Ya |
| B05 | Red edge 1 | 705 nm | 20 m | Ya |
| B06 | Red edge 2 | 740 nm | 20 m | Ya |
| B07 | Red edge 3 | 783 nm | 20 m | Ya |
| B08 | NIR | 842 nm | 10 m | Ya |
| B8A | Narrow NIR | 865 nm | 20 m | Ya |
| B09 | Water vapour | 945 nm | 60 m | Tidak |
| B10 | Cirrus | 1375 nm | 60 m | Tidak; tidak tersedia sebagai band reflektansi permukaan L2A standar |
| B11 | SWIR 1 | 1610 nm | 20 m | Ya |
| B12 | SWIR 2 | 2190 nm | 20 m | Ya |

Resolusi pada tabel adalah **resolusi band asli**, bukan resolusi aktual hasil agregasi Statistical API. Band dengan resolusi asli berbeda digunakan bersama melalui pemrosesan layanan satelit.

### 1.3 Pengumpulan sampel dan pembagian data

| Komponen | Nilai / penjelasan |
|---|---|
| Wilayah kajian | Jawa Timur, termasuk Madura |
| Kelas | 6 kelas: sawah, bangunan, mangrove, lahan hijau, laut, dan danau |
| Poligon kandidat referensi | 180 poligon, masing-masing 30 per kelas |
| Unit sampel untuk pelatihan | **1 baris statistik rata-rata spektral per poligon** |
| Jumlah baris dataset model | **180**, bukan 7.200 sampel piksel |
| Fitur model | 10 band reflektansi + 8 indeks = **18 fitur** |
| Pembagian *train/test* | Stratifikasi 80:20, `random_state=42` |
| Data latih | **144 poligon** (24 per kelas) |
| Data uji | **36 poligon** (6 per kelas) |

Poligon disimpan dalam `PSD_180_polygon_gabungan.geojson`. Nilai reflektansi diekstraksi dari Copernicus ke `dataset_sentinel2_asli_180_polygon_diperbaiki.csv`, kemudian indeks dihitung dan disimpan dalam `dataset_sentinel2_fitur_asli.csv`.

Seluruh 180 baris telah diperiksa secara numerik dan tidak mengandung `NaN` pada sepuluh band. **Validitas numerik tidak sama dengan validasi label di lapangan.** Sumber kandidat poligon beragam, dan kesesuaian tiap poligon dengan kelas rujukannya masih perlu pengecekan citra resolusi tinggi atau survei independen.

**Batasan keseragaman data:** sebagian poligon diekstraksi dari rentang **Juli–September 2026**, sementara poligon yang diperbaiki memakai rentang **April–September 2026**; parameter resolusi/sampling juga tidak seluruhnya seragam. Hal ini dapat memengaruhi komparabilitas spektral antarsampel dan perlu diperbaiki pada pengembangan berikutnya.

---

## 2. Data Preparation dan Ekstraksi Fitur Spektral

### 2.1 Alur pengolahan

1. Menggabungkan enam kumpulan poligon menjadi 180 sampel dengan ID dan label kelas.
2. Meminta statistik reflektansi **10 band** Sentinel-2 L2A per poligon melalui Copernicus Statistical API.
3. Memeriksa respons API, nilai kosong, `NaN`, duplikasi ID, dan distribusi kelas. Lima poligon yang sempat memiliki nilai `NaN` kemudian diekstraksi ulang; dataset akhir berisi 180 baris numerik valid.
4. Menghitung **8 indeks spektral dari rata-rata band per poligon**, bukan menghitung indeks setiap piksel lalu merata-ratakannya.
5. Membagi dataset menjadi data latih dan data uji terstratifikasi, lalu membandingkan enam algoritma.

### 2.2 Delapan indeks spektral dan rumus

Gunakan notasi `B02` (biru), `B03` (hijau), `B04` (merah), `B08` (NIR), `B11` (SWIR 1). Perhitungan program memakai konstanta kecil pada penyebut untuk menghindari pembagian nol.

**1. NDVI — Normalized Difference Vegetation Index**

$$
\mathrm{NDVI}=\frac{B08-B04}{B08+B04}
$$

Indikator kehijauan/aktivitas vegetasi.

**2. NDWI — Normalized Difference Water Index (McFeeters)**

$$
\mathrm{NDWI}=\frac{B03-B08}{B03+B08}
$$

Indeks untuk membantu membedakan air permukaan dari daratan.

**3. MNDWI — Modified Normalized Difference Water Index**

$$
\mathrm{MNDWI}=\frac{B03-B11}{B03+B11}
$$

Memanfaatkan kanal SWIR untuk memperkuat perbedaan badan air terhadap beberapa tutupan darat.

**4. NDBI — Normalized Difference Built-up Index**

$$
\mathrm{NDBI}=\frac{B11-B08}{B11+B08}
$$

Indikator spektral yang dapat membantu identifikasi lahan terbangun, tetapi tidak selalu unik terhadap bangunan.

**5. BSI — Bare Soil Index**

$$
\mathrm{BSI}=\frac{(B11+B04)-(B08+B02)}{(B11+B04)+(B08+B02)}
$$

Indikator untuk membantu membedakan tanah terbuka dari vegetasi.

**6. EVI — Enhanced Vegetation Index**

$$
\mathrm{EVI}=2.5\frac{B08-B04}{B08+6B04-7.5B02+1}
$$

Indeks vegetasi yang turut menggunakan kanal biru untuk penyesuaian pengaruh atmosfer dan latar belakang.

**7. SAVI — Soil Adjusted Vegetation Index** ($L=0.5$)

$$
\mathrm{SAVI}=1.5\frac{B08-B04}{B08+B04+0.5}
$$

Indeks vegetasi dengan penyesuaian pengaruh latar tanah.

**8. NDMI — Normalized Difference Moisture Index**

$$
\mathrm{NDMI}=\frac{B08-B11}{B08+B11}
$$

Indikator kandungan kelembapan vegetasi.

Nilai ambang indeks tidak diperlakukan sebagai aturan mutlak: sinyal tiap kelas dapat tumpang tindih menurut musim, kondisi permukaan, dan lokasi.

---

## 3. Acuan Klasifikasi Indonesia dan Kebijakan Spasial

### 3.1 Keterkaitan dengan SNI 7645

Klasifikasi penutup lahan Indonesia dapat mengacu pada keluarga **SNI 7645**. Enam label yang digunakan dalam proyek ini merupakan **penyederhanaan operasional**, bukan seluruh kelas atau padanan kode hierarki SNI yang telah diverifikasi satu per satu.

| Kelas proyek | Padanan penutup lahan secara umum | Relevansi kebijakan |
|---|---|---|
| Sawah | Pertanian bervegetasi/sawah | Perlindungan LP2B (UU 41/2009) |
| Bangunan | Area terbangun | Kajian pemanfaatan ruang dan perubahan lahan |
| Mangrove | Vegetasi pesisir/lahan basah | Perlindungan ekosistem pesisir |
| Lahan hijau | Vegetasi alami atau semi-alami | Konservasi vegetasi dan fungsi resapan |
| Laut | Perairan laut | Pengelolaan pesisir dan ruang perairan |
| Danau | Badan air daratan | Perlindungan badan air dan sempadan |

**Catatan kelas danau:** label `danau` pada data sampel belum otomatis membuktikan bahwa seluruh lokasi termasuk danau alami/ranu; klasifikasi sumber poligon perlu diperiksa untuk memisahkan danau alami dari waduk, kolam, atau badan air buatan.

### 3.2 Batasan analisis kebijakan

Hasil prediksi LULC dapat membantu **mengidentifikasi area yang perlu ditinjau lebih lanjut**, namun tidak dapat langsung digunakan untuk menyatakan pelanggaran RTRW, perubahan historis, atau status hukum LP2B. Analisis tersebut memerlukan data tambahan seperti peta zonasi resmi, batas kawasan lindung, peta LP2B, serta data pembanding lintas waktu.

---

## 4. Pemodelan dan Evaluasi Machine Learning

### 4.1 Rancangan eksperimen

Enam algoritma dilatih dan dibandingkan menggunakan **180 baris statistik poligon** dengan **18 fitur**. Pembagian terstratifikasi menghasilkan 144 poligon pelatihan dan 36 poligon pengujian. Kinerja dinilai menggunakan *accuracy*, *macro F1-score*, dan *Cohen's kappa*.

### 4.2 Hasil perbandingan

| Algoritma | Accuracy (%) | Cohen's Kappa | Macro F1 (%) |
|---|---:|---:|---:|
| **Extra Trees (terpilih)** | **72.22** | **0.6667** | **68.33** |
| Random Forest | 72.22 | 0.6667 | 65.47 |
| K-Nearest Neighbors (KNN) | 69.44 | 0.6333 | 62.60 |
| Hist Gradient Boosting | 66.67 | 0.6000 | 62.51 |
| Decision Tree (CART) | 63.89 | 0.5667 | 59.86 |
| Support Vector Machine (RBF) | 55.56 | 0.4667 | 54.04 |

**Model terpilih: Extra Trees.** Random Forest memiliki akurasi yang sama (72,22%), tetapi *macro F1-score* Extra Trees lebih tinggi. Model terpilih disimpan sebagai `model_lulc_sentinel2_asli.joblib`. Hasil perbandingan tersedia pada `hasil_perbandingan_model_asli.csv`, dan detail evaluasi pada `evaluasi_model_asli.json`.

### 4.3 Confusion matrix dan pembahasan

Pada 36 poligon pengujian, jumlah prediksi benar menurut kelas adalah:

| Kelas | Benar dari 6 sampel uji | Recall |
|---|---:|---:|
| Bangunan | 6/6 | 100.00% |
| Danau | 3/6 | 50.00% |
| Lahan hijau | 6/6 | 100.00% |
| Laut | 5/6 | 83.33% |
| Mangrove | 1/6 | 16.67% |
| Sawah | 5/6 | 83.33% |

Model paling sulit mengenali kelas **mangrove**, dengan *recall* hanya **16,67%** pada data uji. Hasil ini menunjukkan potensi kebingungan spektral antarjenis vegetasi dan kelas lain serta perlunya peningkatan kualitas sampel, pemeriksaan musim/area, dan validasi independen. Grafik *feature importance* tersedia pada halaman Perbandingan Model aplikasi Streamlit; nilai per fitur tidak dicantumkan di sini karena angka lama berasal dari eksperimen sintetis dan bukan keluaran model terbaru yang telah diverifikasi.

### 4.4 Keterbatasan evaluasi

1. Evaluasi menggunakan pembagian acak terstratifikasi per poligon, **bukan** *spatial-block cross-validation*. Kedekatan lokasi sampel masih dapat memengaruhi perkiraan kemampuan generalisasi.
2. Sampel berjumlah 180 poligon, dengan beberapa label referensi belum diverifikasi secara independen.
3. Periode dan resolusi ekstraksi spektral belum seragam pada semua poligon.
4. Akurasi **72,22%** hanya berlaku untuk **36 poligon pengujian** pada eksperimen ini, **bukan** tingkat akurasi klasifikasi seluruh provinsi atau akurasi peta raster.

---

## 5. Implementasi GIS, Visualisasi Spasial, dan Deployment

### 5.1 Aplikasi interaktif

Aplikasi dibangun menggunakan **Streamlit** (`app.py`) dengan peta **Folium/Leaflet**. Saat laporan ini diperbarui, aplikasi **sudah berjalan secara lokal**, tetapi **belum ada URL deployment publik yang terverifikasi**. Karena itu, statusnya tidak dinyatakan sudah *deployed* secara online.

Jalankan secara lokal melalui terminal di folder proyek:

```bash
python -m streamlit run app.py
```

Aplikasi menyediakan:

- Peta interaktif **180 poligon sampel** dengan enam kelas, menggunakan basemap satelit serta pilihan untuk membandingkan label referensi dan prediksi model.
- **Klasifikasi Raster Per Piksel** pada **satu area contoh sekitar Bangkalan, Madura**, dari GeoTIFF Sentinel-2 L2A berukuran **256 × 256 piksel**. Sebanyak **65.535 piksel** memiliki mask valid, dan hasil prediksi divisualisasikan melalui **Folium `ImageOverlay`**.
- Halaman Data Understanding dengan karakteristik 13 band Sentinel-2.
- Penjelasan rumus delapan indeks spektral dan grafik eksplorasi data.
- Pembahasan acuan SNI dan relevansi kebijakan tata ruang.
- Tabel perbandingan enam model, *confusion matrix*, *classification report*, dan *feature importance*.
- Simulator prediksi berbasis sepuluh band reflektansi; delapan indeks dihitung sesuai masukan.
- Eksplorasi dataset **180 baris** dengan enam kelas serta fungsi filter.

**Jenis layanan peta:** basemap Esri World Imagery menggunakan tile peta (*XYZ tile service*), **bukan WMS**. Raster prediksi ditampilkan dengan **Folium `ImageOverlay`**, juga **bukan WMS**. Tidak ada layanan WMS mandiri yang diklaim dalam proyek ini.

### 5.2 Demonstrasi klasifikasi raster

Raster contoh diambil melalui **Copernicus Process API** dengan 10 band reflektansi Sentinel-2 L2A dan satu band mask. Model Extra Trees yang sebelumnya dilatih pada statistik rata-rata per poligon digunakan untuk menghasilkan raster klasifikasi dan citra overlay.

Keluaran demonstrasi:

- `sentinel2_raster_contoh.tif` — data masukan contoh (10 band dan mask).
- `hasil_klasifikasi_raster.tif` — kode prediksi kelas per piksel.
- `overlay_klasifikasi.png` — warna kelas transparan untuk ditampilkan di peta.
- `overlay_klasifikasi_bounds.json` — batas geografis overlay.

Hasil ini bersifat **prototipe eksploratif**, bukan peta LULC final tervalidasi. **Model dilatih pada nilai rata-rata per poligon, kemudian diterapkan ke nilai setiap piksel**, sehingga terdapat perbedaan distribusi masukan. Overlay memperlihatkan pola berbintik dan indikasi salah klasifikasi, termasuk banyak piksel daratan diprediksi sebagai danau. Kinerja 72,22% dari data uji poligon **tidak boleh diterapkan sebagai akurasi raster**. Evaluasi terhadap data referensi piksel independen dan/atau model khusus piksel diperlukan sebelum peta digunakan untuk pengambilan keputusan.

### 5.3 Publikasi website PSD

Dokumentasi UTS ini ditempatkan pada **Jupyter Book PSD yang sudah ada** (`materi/klasifikasi_lulc_jatim.md`) bersama materi PSD sebelumnya. **Tautan publik Streamlit baru boleh dicantumkan setelah aplikasinya benar-benar dideploy dan berhasil dibuka.** Tidak diperlukan pembuatan website PSD terpisah.


### 5.4 Peta Interaktif Hasil Klasifikasi Extra Trees Jawa Timur

Peta berikut menampilkan **prediksi model Extra Trees pada 180 poligon sampel** enam kelas
(sawah, bangunan, mangrove, lahan hijau, laut, dan danau). Warna menunjukkan **kelas
hasil prediksi**, bukan label asli. Pengguna dapat memilih basemap satelit, mengaktifkan
layer kelas, membaca legenda warna, serta mengeklik poligon untuk membandingkan
prediksi dengan label kandidat sampel.

<iframe src="_static/peta_hasil_prediksi_lulc.html"
  width="100%" height="650" loading="lazy"
  style="border:1px solid #ddd; border-radius:8px;"
  title="Peta hasil klasifikasi Extra Trees pada 180 poligon"></iframe>

**Catatan evaluasi:** Peta ini merupakan hasil prediksi pada **180 poligon yang juga
termasuk dalam dataset pelatihan/pengujian**, bukan klasifikasi raster seluruh
Jawa Timur. Akurasi **72,22%** hanya berasal dari **36 poligon data uji**;
bukan akurasi keseluruhan peta atau raster. Raster area contoh Bangkalan tetap
dibahas secara terpisah pada bagian 5.2 sebagai demonstrasi yang belum tervalidasi.

---

## 6. Kesimpulan dan Rekomendasi

1. Eksperimen berhasil membangun dataset **180 poligon enam kelas** dengan **10 band reflektansi Copernicus** dan **8 indeks spektral** (18 fitur).
2. Dari enam algoritma, **Extra Trees** dipilih berdasarkan akurasi pengujian **72,22%** dan *macro F1* **68,33%**; Random Forest menyamai akurasi tetapi memiliki *macro F1* lebih rendah.
3. Performa berbeda antar kelas, terutama **mangrove** dengan recall **16,67%**. Label serta sampel mangrove dan danau menjadi prioritas verifikasi.
4. Peta poligon sampel dapat menjadi media eksplorasi GIS; raster per piksel saat ini **baru demonstrasi wilayah terbatas** dan belum tervalidasi untuk interpretasi penutup lahan tingkat provinsi.
5. Sebelum menerapkan hasil pada kebijakan LP2B, konservasi, atau RTRW, diperlukan validasi kelas referensi, penyamaan periode/resolusi citra, evaluasi spasial independen, dan *overlay* dengan dataset zonasi resmi.

**Kesimpulan ruang lingkup:** sistem telah mengimplementasikan alur pengumpulan data, ekstraksi fitur, perbandingan model, dan visualisasi interaktif untuk studi contoh di Jawa Timur. Klaim pemetaan lengkap atau akurasi tinggi seluruh Jawa Timur **tidak** dibuat berdasarkan eksperimen ini.


---

## 7. Contoh Implementasi Kode dan Perhitungan Manual

### 7.1 Contoh perhitungan NDVI dari data Copernicus

Digunakan contoh poligon SAWAH_001 dengan nilai rata-rata reflektansi:

- B04 (Red) = 0.0463
- B08 (NIR) = 0.1865

Rumus:

$$
NDVI = \frac{B08-B04}{B08+B04}
$$

Substitusi nilai:

$$
NDVI = \frac{0.1865-0.0463}{0.1865+0.0463}
$$

$$
NDVI = \frac{0.1402}{0.2328} \approx 0.6022
$$

Hasil tersebut merupakan indeks yang dihitung dari
rata-rata reflektansi band dalam satu poligon.

### 7.2 Implementasi perhitungan indeks dengan Python

Berikut contoh potongan logika yang digunakan dalam
`hitung_indeks.py`:

```python
red = float(row["B04"])
nir = float(row["B08"])
green = float(row["B03"])
swir1 = float(row["B11"])

eps = 1e-10

ndvi = (nir - red) / (nir + red + eps)
ndwi = (green - nir) / (green + nir + eps)
mndwi = (green - swir1) / (green + swir1 + eps)
ndbi = (swir1 - nir) / (swir1 + nir + eps)
```

Keempat indeks di atas merupakan sebagian dari delapan
indeks yang digunakan dalam dataset model.

### 7.3 Implementasi pembagian data dan evaluasi

Berikut potongan kode dari alur eksperimen:

```python
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.20,
    stratify=y,
    random_state=42
)

model.fit(X_train, y_train)
prediksi = model.predict(X_test)
akurasi = accuracy_score(y_test, prediksi)
```

Sebanyak 180 data statistik poligon dibagi menjadi
144 data latih dan 36 data uji. Model terbaik pada
eksperimen awal adalah Extra Trees dengan akurasi 72,22%.

### 7.4 Implementasi peta raster interaktif

Visualisasi raster area contoh menggunakan Folium ImageOverlay:

```python
from folium.raster_layers import ImageOverlay

ImageOverlay(
    image="overlay_klasifikasi.png",
    bounds=batas_peta,
    opacity=0.65,
    name="Prediksi Extra Trees per piksel"
).add_to(peta)
```

Kode merupakan ilustrasi inti; pada aplikasi yang
dijalankan, data gambar dan koordinat dibaca dari
file keluaran proses klasifikasi raster.

Peta raster tersebut merupakan demonstrasi area contoh
dan belum memiliki evaluasi akurasi piksel independen.
