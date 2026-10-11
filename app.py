"""Aplikasi GIS UTS: statistik polygon + demonstrasi raster klasifikasi area contoh."""

from pathlib import Path

import json

import html

import altair as alt

import folium

import joblib

import numpy as np

import pandas as pd

import streamlit as st

from streamlit_folium import st_folium

BASE = Path(__file__).resolve().parent

DATA_FILE = BASE / 'dataset_sentinel2_fitur_asli.csv'

MODEL_FILE = BASE / 'model_lulc_sentinel2_asli.joblib'

RESULT_FILE = BASE / 'hasil_perbandingan_model_asli.csv'

EVAL_FILE = BASE / 'evaluasi_model_asli.json'

GEO_FILE = BASE / 'PSD_180_polygon_gabungan.geojson'

BANDS = ['B02','B03','B04','B05','B06','B07','B08','B8A','B11','B12']

INDICES = ['NDVI','NDWI','MNDWI','NDBI','BSI','EVI','SAVI','NDMI']

FEATURES = BANDS + INDICES

DISPLAY = {'sawah':'Sawah','bangunan':'Bangunan','mangrove':'Mangrove',

           'lahan_hijau':'Lahan Hijau','laut':'Laut','danau':'Danau'}

COLORS = {'sawah':'#EAB308','bangunan':'#EF4444','mangrove':'#0D9488',

          'lahan_hijau':'#16A34A','laut':'#0284C7','danau':'#6366F1'}

st.set_page_config(page_title='SIG LULC Jawa Timur | Copernicus Sentinel-2',

                   page_icon='🛰️', layout='wide')

@st.cache_data

def read_data():

    df = pd.read_csv(DATA_FILE)

    required = set(['id','kelas'] + FEATURES)

    missing = sorted(required - set(df.columns))

    if missing:

        raise ValueError(f'Kolom dataset belum lengkap: {missing}')

    if df['id'].duplicated().any():

        raise ValueError('Ada ID polygon duplikat')

    numeric = df[FEATURES].apply(pd.to_numeric, errors='coerce')

    if not np.isfinite(numeric.to_numpy()).all():

        raise ValueError('Masih ada nilai band/indeks NaN atau tak terhingga')

    df[FEATURES] = numeric

    return df

@st.cache_resource

def read_model():

    obj = joblib.load(MODEL_FILE)

    if not isinstance(obj, dict) or 'model' not in obj:

        raise ValueError('Format model tidak sesuai hasil training_model_asli.py')

    return obj

@st.cache_data

def read_results():

    results = pd.read_csv(RESULT_FILE)

    evaluation = json.loads(EVAL_FILE.read_text(encoding='utf-8'))

    geo = json.loads(GEO_FILE.read_text(encoding='utf-8'))

    return results, evaluation, geo

files = [DATA_FILE, MODEL_FILE, RESULT_FILE, EVAL_FILE, GEO_FILE]

missing_files = [p.name for p in files if not p.exists()]

if missing_files:

    st.error('File hasil pengolahan belum ditemukan di folder yang sama dengan app.py: '

             + ', '.join(missing_files))

    st.stop()

try:

    df = read_data()

    model_obj = read_model()

    results, evaluation, geo = read_results()

    model = model_obj['model']

    features = model_obj.get('fitur', FEATURES)

    if not set(features).issubset(df.columns):

        raise ValueError('Fitur model tidak sesuai dataset')

    pred = model.predict(df[features])

    df = df.copy()

    df['prediksi_model'] = pred

except Exception as e:

    st.error(f'Data/model belum bisa dimuat: {e}')

    st.stop()

best_name = evaluation.get('model_terbaik', 'Extra Trees')

best_result = results.loc[results['model'] == best_name]

if best_result.empty:

    st.error('Nama model terpilih tidak ditemukan dalam tabel evaluasi.')

    st.stop()

best_result = best_result.iloc[0]

accuracy = float(best_result['accuracy'])

macro_f1 = float(best_result['f1_macro'])

kappa = float(best_result['kappa'])

with st.sidebar:

    st.title('🛰️ Panel GIS Jawa Timur')

    st.caption('UTS PSD • Sentinel-2 L2A Copernicus')

    menu = st.radio('Pilih halaman:', [

        '🗺️ Peta Interaktif LULC',

        '🌈 Klasifikasi Raster Per Piksel',

        '📊 Data Understanding & Sentinel-2',

        '📐 Ekstraksi Fitur & Indeks',

        '📜 SNI & Kebijakan Tata Ruang',

        '🤖 Perbandingan Model',

        '🧪 Simulator Prediksi',

        '📁 Eksplorasi Data',

    ])

    active_classes = st.multiselect('Tampilkan kelas:', list(DISPLAY),

                                    default=list(DISPLAY), format_func=lambda k: DISPLAY[k])

    st.caption('Peta polygon sampel dan menu raster area contoh tersedia; belum menjadi peta seluruh Jawa Timur.')

st.title('🛰️ Klasifikasi Tutupan Lahan Jawa Timur')

st.caption('Analisis spasial penggunaan lahan dan kebijakan • Statistik Sentinel-2 L2A berbasis polygon')

m1,m2,m3,m4,m5 = st.columns(5)

m1.metric('Polygon sampel',len(df))

m2.metric('Kelas',df['kelas'].nunique())

m3.metric('Fitur',len(features))

m4.metric('Akurasi uji',f'{accuracy*100:.2f}%')

m5.metric('Kappa',f'{kappa:.4f}')

st.info(f'Model terpilih: **{best_name}**, akurasi pengujian **{accuracy*100:.2f}%**, '

        f'F1-macro **{macro_f1:.4f}**. Data uji **{evaluation.get("jumlah_test",36)} polygon**. '

        'Ini evaluasi awal pada polygon sampel, bukan akurasi peta seluruh provinsi.')

if menu == '🗺️ Peta Interaktif LULC':

    st.subheader('Peta interaktif sampel tutupan lahan')

    st.caption('Warna dapat menunjukkan label referensi atau hasil prediksi model pada 180 polygon. '

               'Layer satelit adalah basemap XYZ, **bukan WMS**, dan bukan raster hasil klasifikasi.')

    a,b,c = st.columns([2,2,2])

    with a:
        basemap = st.selectbox(
            'Basemap',
            ['Google Satellite Hybrid', 'Esri World Imagery (satelit)',
             'OpenStreetMap', 'CartoDB Positron'],
        )
    with b:
        map_mode = st.selectbox(
            'Warna polygon', ['Label referensi', 'Prediksi model'], index=1
        )
    with c:

        show_points = st.checkbox('Tampilkan titik pusat polygon', value=False)

    m = folium.Map(location=[-7.75,112.75], zoom_start=8, tiles=None, control_scale=True)

    if basemap == 'Google Satellite Hybrid':
        # Google Hybrid via XYZ tile, not a WMS endpoint. Verify permitted use.
        folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
            attr='Google Maps', name='Google Satellite Hybrid',
            overlay=False, control=True,
        ).add_to(m)
    elif basemap.startswith('Esri'):
        folium.TileLayer(
            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            attr='Tiles © Esri and its data providers', name='Esri World Imagery',
            overlay=False, control=True,
        ).add_to(m)
    elif basemap == 'OpenStreetMap':
        folium.TileLayer('OpenStreetMap', name='OpenStreetMap').add_to(m)
    else:
        folium.TileLayer('CartoDB positron', name='CartoDB Positron').add_to(m)

    by_id = df.set_index('id')

    shown = 0

    for ft in geo.get('features', []):

        props = ft.get('properties') or {}

        fid = props.get('id')

        label = props.get('kelas')

        if fid not in by_id.index or label not in active_classes:

            continue

        r = by_id.loc[fid]

        predicted = str(r['prediksi_model'])

        thematic = predicted if map_mode == 'Prediksi model' else label

        color = COLORS.get(thematic,'#64748b')

        popup = (f'<b>{html.escape(str(fid))}</b><br>Referensi: {html.escape(DISPLAY.get(label,label))}'

                 f'<br>Prediksi model: {html.escape(DISPLAY.get(predicted,predicted))}'

                 f'<br>NDVI: {r["NDVI"]:.3f} • MNDWI: {r["MNDWI"]:.3f}')

        folium.GeoJson(

            ft, name=DISPLAY.get(label,label),

            style_function=lambda _f, c=color: {'color':c,'fillColor':c,'weight':2,'fillOpacity':0.45},

            tooltip=f'{fid} | {DISPLAY.get(thematic,thematic)}',

            popup=folium.Popup(popup,max_width=300)

        ).add_to(m)

        if show_points:

            # GeoJSON geometries can be Polygon or MultiPolygon: representative centroids are not used

            # unless a point is safely derived from the geometry bounds.

            geometry = ft.get('geometry') or {}

            def pairs(coords):

                if isinstance(coords, list) and len(coords)>=2 and all(isinstance(v,(int,float)) for v in coords[:2]):

                    yield coords[:2]

                elif isinstance(coords, list):

                    for item in coords:

                        yield from pairs(item)

            points = list(pairs(geometry.get('coordinates',[])))

            if points:

                # Bounding box center is approximate and may lie outside irregular polygons.

                lon = (min(p[0] for p in points)+max(p[0] for p in points))/2

                lat = (min(p[1] for p in points)+max(p[1] for p in points))/2

                folium.CircleMarker([lat,lon], radius=2, color=color,fill=True).add_to(m)

        shown += 1

    # Legenda mengikuti COLORS asli aplikasi dan pilihan kelas aktif.

    legend_rows = ''.join(

        '<div style="display:flex;align-items:center;gap:7px;margin-top:5px;">'

        f'<span style="display:inline-block;width:13px;height:13px;'

        f'background:{COLORS[k]};border:1px solid #555;border-radius:3px;"></span>'

        f'<span>{html.escape(DISPLAY[k])}</span></div>'

        for k in active_classes

    )

    legend_html = (

        '<div style="position:fixed;bottom:25px;left:12px;z-index:9999;'

        'background:rgba(255,255,255,.96);color:#222;'

        'border:1px solid #aaa;border-radius:7px;padding:10px 12px;'

        'font:13px Arial,sans-serif;box-shadow:0 2px 8px #0003;">'

        '<b>Legenda Kelas LULC</b>' + legend_rows + '</div>'

    )

    m.get_root().html.add_child(folium.Element(legend_html))

    folium.LayerControl(collapsed=True).add_to(m)

    st_folium(m,height=580,use_container_width=True,returned_objects=[])

    st.caption(f'Menampilkan {shown} polygon dari dataset sampel. Label yang digunakan perlu verifikasi lapangan/citra.')

elif menu == '🌈 Klasifikasi Raster Per Piksel':

    from folium.raster_layers import ImageOverlay

    st.subheader('Klasifikasi raster per piksel — area contoh')

    st.caption('Raster 256 × 256 dari Copernicus Sentinel-2 L2A, diprediksi dengan model '

               'Extra Trees memakai 10 band + 8 indeks. Hanya wilayah contoh sekitar 5 km; '

               'bukan klasifikasi seluruh Jawa Timur dan bukan WMS.')

    overlay_png = BASE / 'overlay_klasifikasi.png'

    overlay_meta = BASE / 'overlay_klasifikasi_bounds.json'

    if not overlay_png.exists() or not overlay_meta.exists():

        st.warning('Overlay belum dibuat. Jalankan *\\`*python klasifikasi_raster.py*\\`* di terminal VS Code.')

    else:

        meta = json.loads(overlay_meta.read_text(encoding='utf-8'))

        bounds = meta['bounds']

        center = [(bounds[0][0] + bounds[1][0])/2,

                  (bounds[0][1] + bounds[1][1])/2]

        st.write(f"**Piksel valid:** {meta['valid_pixels']:,} dari {meta['total_pixels']:,}")

        opacity = st.slider('Opasitas hasil klasifikasi', 0.1, 1.0, 0.75, 0.05)

        m_raster = folium.Map(location=center, zoom_start=12, tiles=None, control_scale=True)

        folium.TileLayer(

            tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',

            attr='Tiles © Esri and its data providers', name='Esri World Imagery',

            overlay=False, control=True

        ).add_to(m_raster)

        folium.TileLayer('OpenStreetMap', name='OpenStreetMap', show=False).add_to(m_raster)

        ImageOverlay(

            image=str(overlay_png), bounds=bounds, opacity=opacity,

            name='Prediksi Extra Trees per piksel', interactive=False,

            zindex=5

        ).add_to(m_raster)

        m_raster.fit_bounds(bounds)

        folium.LayerControl(collapsed=False).add_to(m_raster)

        st_folium(m_raster, height=540, use_container_width=True, returned_objects=[])

        st.markdown('**Legenda kelas:** ' + ' · '.join(

            f'<span style="color:{COLORS[k]}">■</span> {DISPLAY[k]}'

            for k in COLORS

        ), unsafe_allow_html=True)

        st.warning('Eksperimen visual area kecil. Label training belum diverifikasi independen; '

                   'model hanya diuji pada 36 polygon (akurasi awal 72,22%). '

                   'Perbedaan waktu akuisisi dan resolusi raster perlu diaudit sebelum hasil '

                   'digunakan untuk analisis kebijakan atau peta regional.')

elif menu == '📊 Data Understanding & Sentinel-2':

    st.subheader('Data Understanding')

    st.markdown('**Tujuan:** mengkaji sawah produktif (LP2B), kawasan terbangun, mangrove pesisir, '

                'lahan hijau, laut, dan danau/ranu untuk mendukung analisis tata ruang Jawa Timur termasuk Madura.')

    st.markdown('**Sumber data:** Copernicus Data Space, koleksi Sentinel-2 L2A (surface reflectance), '

                '10 band sebagai fitur input. Sentinel-2 MSI memiliki 13 band secara keseluruhan.')

    band_table = [

        ('B01','Coastal aerosol',443,60,False),('B02','Blue',490,10,True),

        ('B03','Green',560,10,True),('B04','Red',665,10,True),

        ('B05','Red edge 1',705,20,True),('B06','Red edge 2',740,20,True),

        ('B07','Red edge 3',783,20,True),('B08','NIR',842,10,True),

        ('B8A','Narrow NIR',865,20,True),('B09','Water vapour',945,60,False),

        ('B10','Cirrus (tidak tersedia pada produk L2A)',1375,60,False),

        ('B11','SWIR 1',1610,20,True),('B12','SWIR 2',2190,20,True),

    ]

    st.dataframe(pd.DataFrame(band_table,columns=['Band','Spektral','Panjang gelombang (nm)','Resolusi asli (m)','Digunakan sebagai fitur']),

                 use_container_width=True,hide_index=True)

    st.markdown(f'**Sampel:** {len(df)} statistik rata-rata polygon; '

                f'{evaluation.get("jumlah_train",144)} latih dan {evaluation.get("jumlah_test",36)} uji '

                '(split stratifikasi satu baris per polygon).')

    stats = df['kelas'].value_counts().rename_axis('Kelas').reset_index(name='Jumlah polygon')

    stats['Kelas'] = stats['Kelas'].map(DISPLAY)

    st.dataframe(stats,hide_index=True,use_container_width=True)

    st.warning('Batasan: periode citra Juli–September dan April–September 2026 serta resolusi sampling '

               'berbeda pada sebagian polygon; sumber akuisisi dan keseragaman data perlu diaudit. '

               'Identitas platform Sentinel-2A spesifik tidak ditelusuri untuk tiap akuisisi; '

               'produk yang digunakan ialah Sentinel-2 L2A.')

elif menu == '📐 Ekstraksi Fitur & Indeks':

    st.subheader('Delapan indeks spektral')

    st.markdown('Indeks dihitung dari **rata-rata reflektansi tiap band per polygon**, '

                'bukan rata-rata indeks piksel per polygon.')

    formulas = {
        'NDVI': r'\frac{B08-B04}{B08+B04}',
        'NDWI': r'\frac{B03-B08}{B03+B08}',
        'MNDWI': r'\frac{B03-B11}{B03+B11}',
        'NDBI': r'\frac{B11-B08}{B11+B08}',
        'BSI': r'\frac{(B11+B04)-(B08+B02)}{(B11+B04)+(B08+B02)}',
        'EVI': r'2.5\,\frac{B08-B04}{B08+6B04-7.5B02+1}',
        'SAVI': r'1.5\,\frac{B08-B04}{B08+B04+0.5}',
        'NDMI': r'\frac{B08-B11}{B08+B11}',
    }

    for key, expression in formulas.items():

        with st.expander(key):

            st.latex(key+'='+expression)

    long_df = df.groupby('kelas')[INDICES].mean().reset_index().melt('kelas',var_name='Indeks',value_name='Rata-rata')

    long_df['Kelas'] = long_df['kelas'].map(DISPLAY)

    chart = alt.Chart(long_df).mark_bar().encode(

        x='Indeks:N',y='Rata-rata:Q',color='Kelas:N',xOffset='Kelas:N',

        tooltip=['Kelas','Indeks',alt.Tooltip('Rata-rata:Q',format='.3f')]).properties(height=350)

    st.altair_chart(chart,use_container_width=True)

elif menu == '📜 SNI & Kebijakan Tata Ruang':

    st.subheader('Acuan klasifikasi dan relevansi kebijakan')

    st.markdown('Enam kelas berikut adalah **penyederhanaan operasional proyek**, '

                'bukan keseluruhan kelas dalam SNI 7645.')

    mappings = [

        ('Sawah','Pertanian bervegetasi / sawah','Perlindungan lahan pertanian pangan berkelanjutan (UU 41/2009)'),

        ('Bangunan','Lahan terbangun','Evaluasi pemanfaatan ruang dan konversi lahan'),

        ('Mangrove','Vegetasi pesisir / lahan basah','Perlindungan ekosistem pesisir'),

        ('Lahan Hijau','Vegetasi alami atau semi-alami','Konservasi vegetasi dan fungsi resapan'),

        ('Laut','Perairan laut','Perencanaan ruang pesisir dan perairan'),

        ('Danau','Perairan darat','Perlindungan danau dan sempadan badan air'),

    ]

    st.dataframe(pd.DataFrame(mappings,columns=['Kelas proyek','Padanan umum penutup lahan','Relevansi kebijakan']),

                 hide_index=True,use_container_width=True)

    st.markdown('**Rujukan awal:** SNI 7645 tentang klasifikasi penutup lahan; '

                'UU No. 41 Tahun 2009 (LP2B); UU No. 26 Tahun 2007 (penataan ruang); '

                'Perpres No. 60 Tahun 2021 (penyelamatan danau prioritas).')

    st.warning('Penetapan kelas danau **alami** memerlukan verifikasi polygon, karena badan air '

               'buatan/waduk tidak boleh otomatis diklaim sebagai danau alami. '

               'Penerapan kebijakan dan kesesuaian RTRW memerlukan layer zonasi resmi, '

               'bukan hanya prediksi LULC.')

elif menu == '🤖 Perbandingan Model':

    st.subheader('Eksperimen enam algoritma machine learning')

    st.markdown(f'Pembagian train/test: **{evaluation.get("jumlah_train",144)}/{evaluation.get("jumlah_test",36)}** '

                '(80% / 20%, stratifikasi kelas, random_state=42).')

    view = results.copy().sort_values(['accuracy','f1_macro'],ascending=False)

    view['accuracy'] *= 100

    view['f1_macro'] *= 100

    view = view.rename(columns={'model':'Model','accuracy':'Accuracy (%)','f1_macro':'F1-Macro (%)','kappa':'Kappa'})

    st.dataframe(view.style.format({'Accuracy (%)':'{:.2f}','F1-Macro (%)':'{:.2f}','Kappa':'{:.4f}'}),

                 use_container_width=True,hide_index=True)

    chart = alt.Chart(view).mark_bar().encode(

        x=alt.X('Accuracy (%):Q',scale=alt.Scale(domain=[0,100])),

        y=alt.Y('Model:N',sort='-x'),tooltip=['Model','Accuracy (%)','F1-Macro (%)','Kappa']).properties(height=260)

    st.altair_chart(chart,use_container_width=True)

    st.markdown(f'**Model terbaik: {best_name}**. Saat akurasi seri, dipilih F1-macro lebih tinggi.')

    classes = evaluation.get('kelas',sorted(df['kelas'].unique()))

    matrix = evaluation.get('confusion_matrix',[])

    if matrix:

        cm = pd.DataFrame(matrix,index=[DISPLAY.get(s,s) for s in classes],

                          columns=[DISPLAY.get(s,s) for s in classes])

        st.markdown('**Confusion matrix** (baris = referensi, kolom = prediksi)')

        st.dataframe(cm,use_container_width=True)

    report = evaluation.get('classification_report',{})

    if report:

        rep = pd.DataFrame(report).T

        st.markdown('**Classification report model terpilih**')

        st.dataframe(rep,use_container_width=True)

    if hasattr(model,'feature_importances_'):

        fi = pd.DataFrame({'Fitur':features,'Importance':model.feature_importances_}).sort_values('Importance',ascending=False)

        st.markdown('**Feature importance (Extra Trees)**')

        st.bar_chart(fi.set_index('Fitur').head(10))

    st.caption('Evaluasi awal pada 36 polygon sampel, belum spatial-block cross-validation dan '

               'belum validasi label independen; hasil tidak boleh digeneralisasikan ke seluruh Jawa Timur.')

elif menu == '🧪 Simulator Prediksi':

    st.subheader('Simulator klasifikasi dari band spektral')

    st.caption('Nilai awal diambil dari salah satu pengukuran Copernicus di dataset, '

               'bukan profil reflektansi sintetis. Slider mengubahnya menjadi eksperimen hipotetis.')

    options = df[['id','kelas']].copy()

    sample_id = st.selectbox('Polygon contoh dari dataset asli:',options['id'].tolist())

    row = df.set_index('id').loc[sample_id]

    st.caption(f'Label referensi: {DISPLAY.get(row["kelas"],row["kelas"])}')

    inputs = {}

    with st.form('simulator'):

        cols = st.columns(5)

        for i,band in enumerate(BANDS):

            val = float(row[band])

            # Use numeric inputs because actual reflectances may include values beyond slider preset ranges.

            with cols[i%5]:

                inputs[band] = st.number_input(band,value=val,format='%.6f',key=f'sim_{band}_{sample_id}')

        submitted = st.form_submit_button('Prediksi tutupan lahan')

    if submitted:

        blue,green,red = inputs['B02'],inputs['B03'],inputs['B04']

        nir,swir1 = inputs['B08'],inputs['B11']

        def ratio(a,b): return (a-b)/(a+b+1e-10)

        indices = {

            'NDVI':ratio(nir,red), 'NDWI':ratio(green,nir),

            'MNDWI':ratio(green,swir1), 'NDBI':ratio(swir1,nir),

            'BSI':((swir1+red)-(nir+blue))/(swir1+red+nir+blue+1e-10),

            'EVI':2.5*(nir-red)/(nir+6*red-7.5*blue+1+1e-10),

            'SAVI':1.5*(nir-red)/(nir+red+0.5+1e-10),

            'NDMI':ratio(nir,swir1),

        }

        input_df = pd.DataFrame([{**inputs,**indices}])[features]

        predicted = str(model.predict(input_df)[0])

        st.success('Prediksi model: '+DISPLAY.get(predicted,predicted))

        if hasattr(model,'predict_proba'):

            probs = model.predict_proba(input_df)[0]

            proba_df = pd.DataFrame({'Kelas':[DISPLAY.get(s,s) for s in model.classes_],

                                    'Probabilitas':probs})

            st.bar_chart(proba_df.set_index('Kelas'))

            st.caption('Probabilitas model bukan tingkat kepastian hasil di lapangan.')

elif menu == '📁 Eksplorasi Data':

    st.subheader('Dataset Copernicus Sentinel-2 L2A — 180 polygon')

    selection = st.multiselect('Kelas',list(DISPLAY),default=list(DISPLAY),format_func=lambda k:DISPLAY[k])

    filtered = df.loc[df['kelas'].isin(selection)]

    st.dataframe(filtered,use_container_width=True,hide_index=True)

    st.download_button('📥 Unduh dataset fitur (CSV)',data=df.to_csv(index=False).encode('utf-8'),

                       file_name='dataset_sentinel2_fitur_asli.csv',mime='text/csv')

    st.caption('Satu baris adalah rata-rata band pada satu polygon, bukan satu piksel individual.')

st.divider()

st.caption('UTS PSD • Klasifikasi tutupan lahan Jawa Timur • Copernicus Sentinel-2 L2A • 2026')
