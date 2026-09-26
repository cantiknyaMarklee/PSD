# Ekstraksi Fitur TSFEL

Bab ini membahas konsep ekstraksi fitur TSFEL pada domain statistik, temporal, dan spektral, pembuktian perhitungan manual pada fitur yang menjadi bagian analisis, serta hasil ekstraksi fitur multi-polutan.

Ekstraksi fitur merupakan proses mengubah data time series menjadi sekumpulan nilai numerik yang dapat merepresentasikan karakteristik penting dari suatu sinyal. Pada penelitian ini, ekstraksi fitur dilakukan terhadap data time series tiga polutan, yaitu Karbon Monoksida (CO), Nitrogen Dioksida (NO₂), dan Sulfur Dioksida (SO₂).

Ekstraksi fitur dilakukan menggunakan **Time Series Feature Extraction Library (TSFEL)**. Fitur yang digunakan berasal dari tiga domain utama, yaitu **statistical domain**, **temporal domain**, dan **spectral domain**.

## 1. Konsep Dasar Ekstraksi Fitur Time Series

### 1.1 Domain Statistik

Domain statistik menggambarkan karakteristik distribusi nilai pada suatu time series. Fitur pada domain ini digunakan untuk mengetahui sifat data berdasarkan ukuran statistik seperti rata-rata, median, variansi, standar deviasi, minimum, maksimum, kurtosis, dan karakteristik distribusi lainnya.

Sebagai contoh, nilai rata-rata dari suatu time series dihitung menggunakan:

$$
\bar{x} = \frac{1}{n}\sum_{i=1}^{n}x_i
$$

dengan:

- $x_i$ = nilai data ke-$i$,
- $n$ = jumlah data,
- $\bar{x}$ = nilai rata-rata.

### 1.2 Domain Temporal

Domain temporal menggambarkan karakteristik sinyal berdasarkan perubahan nilai terhadap waktu. Fitur temporal dapat digunakan untuk mengukur pola perubahan, jarak, autokorelasi, zero crossing, serta karakteristik lain yang berkaitan dengan urutan waktu pada data.

Salah satu contoh fitur temporal adalah **autocorrelation**, yaitu ukuran hubungan antara suatu time series dengan versi time series tersebut yang mengalami pergeseran waktu (*lag*).

### 1.3 Domain Spektral

Domain spektral menggambarkan karakteristik sinyal berdasarkan komponen frekuensinya. Analisis pada domain ini umumnya menggunakan transformasi dari domain waktu ke domain frekuensi sehingga pola frekuensi yang terdapat pada data dapat dianalisis.

Beberapa fitur yang termasuk dalam analisis spektral antara lain **fundamental frequency**, **spectral centroid**, **spectral entropy**, **spectral roll-off**, dan fitur lain yang menggambarkan distribusi energi pada frekuensi.

Pada proses ekstraksi yang digunakan dalam penelitian ini, setiap polutan menghasilkan **68 fitur TSFEL**. Karena terdapat tiga polutan, yaitu CO, NO₂, dan SO₂, maka keseluruhan fitur yang digunakan pada analisis gabungan adalah:

$$
68 \times 3 = 204 \text{ fitur}
$$

## 2. Fitur yang Dianalisis

Berdasarkan pembagian fitur ekstraksi, fitur yang dianalisis pada bagian ini adalah:

1. `slope(signal)`
2. `spectral_centroid(signal, fs)`

Kedua fitur tersebut mewakili karakteristik time series yang berbeda. `slope` digunakan untuk menggambarkan kecenderungan perubahan nilai sinyal, sedangkan `spectral_centroid` digunakan untuk menggambarkan pusat distribusi spektrum frekuensi suatu sinyal.

### 2.1 Slope

#### 2.1.1 Deskripsi Slope

`Slope` merupakan fitur yang digunakan untuk mengukur kecenderungan perubahan nilai suatu sinyal terhadap waktu. Nilai slope menunjukkan arah dan besar perubahan data secara linear.

Interpretasi nilai slope adalah:

- slope positif menunjukkan kecenderungan nilai sinyal meningkat,
- slope negatif menunjukkan kecenderungan nilai sinyal menurun,
- slope mendekati nol menunjukkan bahwa secara linear nilai sinyal relatif tidak mengalami kecenderungan naik atau turun yang kuat.

Secara matematis, slope regresi linear dapat dihitung menggunakan:

$$
m =
\frac{
n\sum x_i y_i - (\sum x_i)(\sum y_i)
}{
n\sum x_i^2 - (\sum x_i)^2
}
$$

dengan:

- $m$ = nilai slope,
- $x_i$ = indeks atau urutan waktu,
- $y_i$ = nilai sinyal pada indeks ke-$i$,
- $n$ = jumlah data.

#### 2.1.2 Contoh Perhitungan Manual

Sebagai contoh sederhana, digunakan lima nilai sinyal:

$$
y = [2,4,6,8,10]
$$

dengan indeks:

$$
x = [0,1,2,3,4]
$$

Jumlah data:

$$
n = 5
$$

Jumlah seluruh nilai $x$:

$$
\sum x_i = 0+1+2+3+4 = 10
$$

Jumlah seluruh nilai $y$:

$$
\sum y_i = 2+4+6+8+10 = 30
$$

Jumlah hasil perkalian $x_i$ dan $y_i$:

$$
\sum x_i y_i
=
(0)(2)+(1)(4)+(2)(6)+(3)(8)+(4)(10)
=80
$$

Jumlah kuadrat nilai $x$:

$$
\sum x_i^2
=
0^2+1^2+2^2+3^2+4^2
=30
$$

Selanjutnya nilai tersebut dimasukkan ke dalam persamaan slope:

$$
m =
\frac{
(5)(80)-(10)(30)
}{
(5)(30)-(10)^2
}
$$

$$
m =
\frac{400-300}{150-100}
=
\frac{100}{50}
=2
$$

Dengan demikian, nilai slope yang diperoleh adalah **2**. Nilai positif menunjukkan bahwa sinyal pada contoh tersebut memiliki kecenderungan meningkat.

#### 2.1.3 Pembuktian Menggunakan TSFEL

Setelah nilai slope dihitung secara manual, hasil tersebut dapat dibandingkan dengan fungsi `slope(signal)` pada TSFEL.

Kode yang digunakan:

```python
import numpy as np
from tsfel.feature_extraction.features import slope

signal = np.array([2, 4, 6, 8, 10])

hasil_slope = slope(signal)

print("Hasil slope TSFEL:", hasil_slope)
```

Untuk sinyal:

$$
[2,4,6,8,10]
$$

perhitungan manual menghasilkan:

$$
\text{Slope Manual} = 2
$$

Hasil fungsi `slope(signal)` pada TSFEL kemudian dapat dibandingkan dengan hasil perhitungan manual tersebut.

### 2.2 Spectral Centroid

#### 2.2.1 Deskripsi Spectral Centroid

`Spectral centroid` merupakan fitur pada domain spektral yang digunakan untuk menunjukkan pusat distribusi spektrum suatu sinyal. Fitur ini menghitung rata-rata tertimbang frekuensi berdasarkan besar spektrum pada masing-masing frekuensi.

Secara matematis, spectral centroid dapat dinyatakan sebagai:

$$
C =
\frac{
\sum_{k=0}^{N-1} f_k A_k
}{
\sum_{k=0}^{N-1} A_k
}
$$

dengan:

- $C$ = spectral centroid,
- $f_k$ = frekuensi pada bin ke-$k$,
- $A_k$ = besar atau magnitudo spektrum pada frekuensi ke-$k$,
- $N$ = jumlah komponen frekuensi.

Semakin besar nilai spectral centroid, semakin besar kontribusi komponen frekuensi tinggi terhadap spektrum sinyal. Sebaliknya, nilai spectral centroid yang lebih rendah menunjukkan bahwa distribusi spektrum lebih banyak terkonsentrasi pada frekuensi yang lebih rendah.

#### 2.2.2 Contoh Perhitungan Manual

Sebagai contoh sederhana, diasumsikan hasil analisis spektrum memiliki frekuensi dan magnitudo sebagai berikut:

| Frekuensi ($f_k$) | Magnitudo ($A_k$) |
|---:|---:|
| 0 | 1 |
| 1 | 2 |
| 2 | 3 |
| 3 | 4 |

Spectral centroid dihitung menggunakan:

$$
C =
\frac{
(0)(1)+(1)(2)+(2)(3)+(3)(4)
}{
1+2+3+4
}
$$

$$
C =
\frac{0+2+6+12}{10}
=
\frac{20}{10}
=2
$$

Berdasarkan contoh tersebut, diperoleh nilai spectral centroid sebesar **2** dalam satuan frekuensi yang digunakan pada contoh.

#### 2.2.3 Pembuktian Menggunakan TSFEL

Setelah konsep dan perhitungan manual spectral centroid dijelaskan, fitur ini dapat dihitung menggunakan fungsi `spectral_centroid(signal, fs)` pada TSFEL.

Pada proses ekstraksi fitur digunakan parameter `fs=1`.

Kode pembuktian menggunakan TSFEL adalah sebagai berikut:

```python
import numpy as np
from tsfel.feature_extraction.features import spectral_centroid

signal = np.array([2, 4, 6, 8, 10])
fs = 1

hasil_spectral_centroid = spectral_centroid(signal, fs)

print("Hasil spectral centroid TSFEL:", hasil_spectral_centroid)
```

Fungsi `spectral_centroid(signal, fs)` menghitung spectral centroid berdasarkan spektrum frekuensi dari sinyal masukan. Parameter `signal` berisi nilai time series, sedangkan `fs` merupakan frekuensi sampling yang digunakan dalam proses perhitungan.

Hasil yang diperoleh dari TSFEL dapat digunakan sebagai pembuktian implementasi perhitungan spectral centroid pada data time series.

## 3. Hasil Ekstraksi Fitur TSFEL

Ekstraksi fitur dilakukan terhadap tiga data time series polutan, yaitu CO, NO₂, dan SO₂. Masing-masing polutan menghasilkan **68 fitur TSFEL**.

Hasil ekstraksi fitur disimpan dalam file:

- `CO_Kota_Sumenep_TSFEL_68.csv`
- `NO2_Kota_Sumenep-TSFEL-68-Fitur.csv`
- `SO2_Kota_Sumenep_TSFEL_68.csv`

Karena masing-masing polutan menghasilkan 68 fitur, jumlah fitur yang digunakan pada analisis gabungan adalah:

$$
68 + 68 + 68 = 204 \text{ fitur}
$$

Hasil ekstraksi tersebut selanjutnya digunakan sebagai data masukan pada tahap reduksi dimensi dan clustering.