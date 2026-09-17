# Analisis Time Series

Bab ini membahas pengunduhan deret waktu multi-polutan ($NO_2$, $SO_2$, dan $CO$) melalui **openEO Copernicus Dataspace**, analisis tren harian, serta dekomposisi karakteristik sinyal temporal di wilayah **Kecamatan Kota Sumenep**.

---

## 1. Pipeline Ekstraksi Multi-Polutan via openEO

Untuk menambahkan parameter polutan $SO_2$ dan $CO$ berdampingan dengan $NO_2$, array `bands` pada pemanggilan `load_collection` diperluas:

```python
import json
import openeo

# 1. Hubungkan ke openEO Copernicus
connection = openeo.connect("[https://openeo.dataspace.copernicus.eu](https://openeo.dataspace.copernicus.eu)")
connection.authenticate_oidc_device()

# 2. Muat batas wilayah GeoJSON Kota Sumenep
with open("KotaSumenep.geojson", "r") as f:
    aoi = json.load(f)

# 3. Muat Data Cube Sentinel-5P dengan band NO2, SO2, dan CO
datacube = connection.load_collection(
    "SENTINEL_5P_L2",
    spatial_extent=aoi,
    temporal_extent=["2025-08-31", "2026-08-31"],
    bands=["NO2", "SO2", "CO"]
)

# 4. Agregasi Temporal Harian (Mean)
datacube_daily = datacube.aggregate_temporal_period(
    period="day",
    reducer="mean"
)

# 5. Agregasi Spasial per Wilayah AOI
datacube_daily_spatial = datacube_daily.aggregate_spatial(
    geometries=aoi,
    reducer="mean"
)

# 6. Eksekusi Batch Job dan Simpan ke CSV
job = datacube_daily_spatial.save_result(format="CSV").execute_batch(
    outputfile="Multi_Polutan_Kota_Sumenep_2025-2026.csv",
    title="Time Series NO2, SO2, CO Kota Sumenep",
    description="Sentinel-5P daily mean aggregated over Kota Sumenep"
)
print("Batch Job ID:", job.job_id)
