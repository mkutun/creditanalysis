# app.py - v8 (Tek Pencere Garantili Stabil Sürüm)

import streamlit as st
import os
import json
from io import BytesIO
import pandas as pd
import math
import numpy as np
import re

# Diğer modüllerden importlar
from pdf_okuyucu import pdf_verilerini_oku
from hesaplamalar import finansal_oranlari_hesapla, oran_basliklari_tr, oran_basliklari_en
from skorlama import kredi_skoru_hesapla
from cikti_islemleri import excel_cikti_al, word_cikti_al

# --- STATE (DURUM) YÖNETİMİ ---
if 'file_uploaded' not in st.session_state:
    st.session_state.file_uploaded = False

# --- SEKTÖREL VERİTABANI ---
SEKTOR_HEDEFLERI = {
    "Genel Değerler": {
        "Cari Oran": {"hedef": "> 1.5", "iyi": 1.5, "orta": 1.0, "tip": "buyuk_iyi"}, "Likidite Oranı": {"hedef": "> 1.0", "iyi": 1.0, "orta": 0.8, "tip": "buyuk_iyi"},
        "Finansal Kaldıraç": {"hedef": "< 2.5", "iyi": 2.5, "orta": 3.5, "tip": "kucuk_iyi"}, "Borç / Özkaynak Oranı": {"hedef": "< 1.5", "iyi": 1.5, "orta": 2.0, "tip": "kucuk_iyi"},
        "Brüt Kar Marjı": {"hedef": "> 25%", "iyi": 0.25, "orta": 0.15, "tip": "buyuk_iyi"}, "Faaliyet Kar Marjı": {"hedef": "> 15%", "iyi": 0.15, "orta": 0.10, "tip": "buyuk_iyi"},
        "EBITDA Marjı": {"hedef": "> 20%", "iyi": 0.20, "orta": 0.15, "tip": "buyuk_iyi"}, "Net Kar Marjı": {"hedef": "> 10%", "iyi": 0.10, "orta": 0.05, "tip": "buyuk_iyi"},
        "Aktif Karlılığı (ROA)": {"hedef": "> 10%", "iyi": 0.10, "orta": 0.05, "tip": "buyuk_iyi"}, "Özkaynak Karlılığı (ROE)": {"hedef": "> 15%", "iyi": 0.15, "orta": 0.10, "tip": "buyuk_iyi"},
    },
    "İnşaat": { "Cari Oran": {"hedef": "> 1.3", "iyi": 1.3, "orta": 1.0, "tip": "buyuk_iyi"}, "Borç / Özkaynak Oranı": {"hedef": "< 3.0", "iyi": 3.0, "orta": 4.0, "tip": "kucuk_iyi"}, "Net Kar Marjı": {"hedef": "> 4%", "iyi": 0.04, "orta": 0.02, "tip": "buyuk_iyi"}, "Özkaynak Karlılığı (ROE)": {"hedef": "> 12%", "iyi": 0.12, "orta": 0.08, "tip": "buyuk_iyi"}},
    "Tekstil": { "Cari Oran": {"hedef": "> 1.5", "iyi": 1.5, "orta": 1.2, "tip": "buyuk_iyi"}, "Borç / Özkaynak Oranı": {"hedef": "< 1.5", "iyi": 1.5, "orta": 2.0, "tip": "kucuk_iyi"}, "Brüt Kar Marjı": {"hedef": "> 25%", "iyi": 0.25, "orta": 0.18, "tip": "buyuk_iyi"}, "Net Kar Marjı": {"hedef": "> 7%", "iyi": 0.07, "orta": 0.04, "tip": "buyuk_iyi"}},
    "İlaç": { "Cari Oran": {"hedef": "> 2.0", "iyi": 2.0, "orta": 1.5, "tip": "buyuk_iyi"}, "Borç / Özkaynak Oranı": {"hedef": "< 1.0", "iyi": 1.0, "orta": 1.5, "tip": "kucuk_iyi"}, "Brüt Kar Marjı": {"hedef": "> 70%", "iyi": 0.70, "orta": 0.60, "tip": "buyuk_iyi"}, "Net Kar Marjı": {"hedef": "> 18%", "iyi": 0.18, "orta": 0.12, "tip": "buyuk_iyi"}},
    "Hastane": { "Cari Oran": {"hedef": "> 1.8", "iyi": 1.8, "orta": 1.5, "tip": "buyuk_iyi"}, "Borç / Özkaynak Oranı": {"hedef": "< 2.0", "iyi": 2.0, "orta": 2.5, "tip": "kucuk_iyi"}, "Faaliyet Kar Marjı": {"hedef": "> 8%", "iyi": 0.08, "orta": 0.05, "tip": "buyuk_iyi"}, "Net Kar Marjı": {"hedef": "> 4%", "iyi": 0.04, "orta": 0.02, "tip": "buyuk_iyi"}},
    "Yazılım": { "Borç / Özkaynak Oranı": {"hedef": "< 0.5", "iyi": 0.5, "orta": 0.8, "tip": "kucuk_iyi"}, "Brüt Kar Marjı": {"hedef": "> 80%", "iyi": 0.80, "orta": 0.70, "tip": "buyuk_iyi"}, "Net Kar Marjı": {"hedef": "> 20%", "iyi": 0.20, "orta": 0.10, "tip": "buyuk_iyi"}, "Özkaynak Karlılığı (ROE)": {"hedef": "> 25%", "iyi": 0.25, "orta": 0.15, "tip": "buyuk_iyi"}},
    "Film Prodüksiyon": { "Faaliyet Kar Marjı": {"hedef": "> 25%", "iyi": 0.25, "orta": 0.15, "tip": "buyuk_iyi"}, "Özkaynak Karlılığı (ROE)": {"hedef": "> 30%", "iyi": 0.30, "orta": 0.20, "tip": "buyuk_iyi"}},
    "Gıda": { "Cari Oran": {"hedef": "> 1.4", "iyi": 1.4, "orta": 1.1, "tip": "buyuk_iyi"}, "Borç / Özkaynak Oranı": {"hedef": "< 1.5", "iyi": 1.5, "orta": 2.0, "tip": "kucuk_iyi"}, "Net Kar Marjı": {"hedef": "> 5%", "iyi": 0.05, "orta": 0.03, "tip": "buyuk_iyi"}, "Aktif Karlılığı (ROA)": {"hedef": "> 8%", "iyi": 0.08, "orta": 0.05, "tip": "buyuk_iyi"}},
    "Tarım": { "Cari Oran": {"hedef": "> 1.5", "iyi": 1.5, "orta": 1.2, "tip": "buyuk_iyi"}, "Borç / Özkaynak Oranı": {"hedef": "< 2.0", "iyi": 2.0, "orta": 2.5, "tip": "kucuk_iyi"}, "Net Kar Marjı": {"hedef": "> 8%", "iyi": 0.08, "orta": 0.05, "tip": "buyuk_iyi"}},
    "Endüstriyel Ürünler / İmalat": { "Cari Oran": {"hedef": "> 1.8", "iyi": 1.8, "orta": 1.5, "tip": "buyuk_iyi"}, "Borç / Özkaynak Oranı": {"hedef": "< 2.0", "iyi": 2.0, "orta": 2.5, "tip": "kucuk_iyi"}, "Faaliyet Kar Marjı": {"hedef": "> 10%", "iyi": 0.10, "orta": 0.07, "tip": "buyuk_iyi"}, "Aktif Karlılığı (ROA)": {"hedef": "> 7%", "iyi": 0.07, "orta": 0.04, "tip": "buyuk_iyi"}}
}
SEKTOR_ACIKLAMALARI = { "Genel Değerler": [ {"oran": "Cari Oran", "hedef": "> 1.5", "aciklama": "Şirketin kısa vadeli (1 yıldan az) borçlarını rahatça ödeyip ödeyemeyeceğini gösterir. Değerin 1.5'in üzerinde olması, şirketin likidite açısından güvende olduğunu gösterir."}, {"oran": "Likidite Oranı", "hedef": "> 1.0", "aciklama": "Cari orana benzer ancak daha hassastır. Stoklar gibi hemen nakde çevrilemeyecek varlıkları çıkararak hesaplanır. 1'in üzeri, şirketin acil durumlar için bile yeterli likiditeye sahip olduğu anlamına gelir."}, {"oran": "Finansal Kaldıraç", "hedef": "< 2.5", "aciklama": "Şirketin varlıklarının ne kadarının borçla finanse edildiğini gösterir. Yüksek olması riskli kabul edilir. 2.5'in altı, şirketin varlıklarının büyük kısmının özkaynaklarla finanse edildiğini gösterir ve daha sağlıklıdır."}, {"oran": "Borç / Özkaynak Oranı", "hedef": "< 1.5", "aciklama": "Toplam borcun özkaynaklara oranını gösterir. 1.5'in altı, şirketin borçlarının özkaynaklarından az olduğu ve borç yükünün yönetilebilir seviyede olduğu anlamına gelir."}, {"oran": "Brüt Kar Marjı", "hedef": "> 25%", "aciklama": "Şirketin sattığı malın maliyetini düştükten sonra elde ettiği karın yüzdesidir. Bu oranın yüksekliği, şirketin temel faaliyetlerinde ne kadar karlı olduğunu gösterir."}, {"oran": "Faaliyet Kar Marjı", "hedef": "> 15%", "aciklama": "Satışların maliyeti ve diğer tüm operasyonel giderler (pazarlama, yönetim vb.) düşüldükten sonra kalan karı gösterir. Şirketin ana işinden ne kadar verimli kar ürettiğinin en önemli göstergelerindendir."}, {"oran": "EBITDA Marjı", "hedef": "> 20%", "aciklama": "Faiz, vergi ve amortisman öncesi karın satışlara oranıdır. Şirketin operasyonel performansını ve nakit yaratma potansiyelini ölçmek için kullanılır."}, {"oran": "Net Kâr Marjı", "hedef": "> 10%", "aciklama": "Tüm giderler (vergiler dahil) düşüldükten sonra net karın satışlara oranını gösterir. Şirketin genel karlılığını ifade eden nihai orandır."}, {"oran": "Aktif Karlılığı (ROA)", "hedef": "> 10%", "aciklama": "Şirketin sahip olduğu toplam varlıkları ne kadar verimli kullanarak net kar ürettiğini gösterir. Yüksek olması, varlıkların etkin kullanıldığı anlamına gelir."}, {"oran": "Özkaynak Karlılığı (ROE)", "hedef": "> 15%", "aciklama": "Şirket sahiplerinin yatırdığı sermayenin ne kadar verimli kullanılarak kar elde edildiğini gösterir. Yatırımcılar için en önemli karlılık göstergelerinden biridir."} ]}

def get_ratio_evaluation(ratio_name_key, value, dil):
    secilen_sektor = st.session_state.get('secilen_sektor', 'Genel Değerler')
    sektor_kurallari = SEKTOR_HEDEFLERI.get(secilen_sektor, SEKTOR_HEDEFLERI["Genel Değerler"])
    kural = sektor_kurallari.get(ratio_name_key) or SEKTOR_HEDEFLERI["Genel Değerler"].get(ratio_name_key)
    durum_iyi, durum_orta, durum_kotu, durum_yok = ("İyi", "Good"), ("Orta", "Average"), ("Zayıf", "Weak"), ("", "")
    if not kural or value is None or np.isnan(value): return kural.get("hedef", "-") if kural else "-", durum_yok[1 if dil == "EN" else 0]
    status, hedef_str = durum_yok, kural["hedef"]
    if kural["tip"] == "buyuk_iyi":
        if value >= kural["iyi"]: status = durum_iyi
        elif value >= kural["orta"]: status = durum_orta
        else: status = durum_kotu
    elif kural["tip"] == "kucuk_iyi":
        if value <= kural["iyi"]: status = durum_iyi
        elif value <= kural["orta"]: status = durum_orta
        else: status = durum_kotu
    return hedef_str, status[1 if dil == "EN" else 0]

def parse_tr_number(s: str) -> float:
    if s is None: return 0.0
    s = str(s).strip();
    if not s: return 0.0
    is_negative = s.startswith('(') and s.endswith(')')
    s = re.sub(r'[^\d,.]', '', s)
    try:
        if '.' in s and ',' in s:
            if s.rfind('.') > s.rfind(','): s = s.replace(',', '')
            else: s = s.replace('.', '').replace(',', '.')
        else: s = s.replace(',', '.')
        number = float(s)
        return -number if is_negative else number
    except (ValueError, TypeError): return 0.0

def format_tr_number(x, decimals=2):
    if x is None or np.isnan(x) or np.isinf(x): return ""
    try: return f"{x:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except: return ""

rows_tr = ["Dönen Varlıklar", "Duran Varlıklar", "Kısa Vadeli Yükümlülükler", "Uzun Vadeli Yükümlülükler", "Özkaynaklar", "Net Satışlar", "Satışların Maliyeti", "Faaliyet Giderleri", "Finansman Giderleri"]
rows_en = ["Current Assets", "Fixed Assets", "Short-Term Liabilities", "Long-Term Liabilities", "Equity", "Net Sales", "Cost of Goods Sold", "Operating Expenses", "Financial Expenses"]

def build_grid_df(finansal_veriler, dil):
    internal_keys = rows_tr
    display_rows = rows_en if dil == "EN" else rows_tr
    years = finansal_veriler.get("yillar", [])
    data = {}
    for yil in years:
        col_data = []
        year_index = years.index(yil)
        for key in internal_keys:
            if key in finansal_veriler and finansal_veriler[key] and len(finansal_veriler[key]) > year_index:
                col_data.append(finansal_veriler[key][year_index])
            else: col_data.append(0.0)
        data[yil] = col_data
    formatted_data = {yil: [format_tr_number(val) for val in values] for yil, values in data.items()}
    return pd.DataFrame(formatted_data, index=display_rows)

def grid_to_numeric_state(df_grid, hedef_state):
    internal_keys = rows_tr
    years = list(df_grid.columns)
    hedef_state["yillar"] = years
    for i, r_key in enumerate(internal_keys):
        hedef_state[r_key] = [parse_tr_number(df_grid.iloc[i][y]) for y in years]

def is_percentage_key(k): return any(kw in k for kw in ["Marjı", "Margin", "ROA", "ROE", "%"])

KALEM_ESLESTIRME_SÖZLÜGÜ = {"Dönen Varlıklar": [r"dönen varlıklar"], "Duran Varlıklar": [r"duran varlıklar"],"Kısa Vadeli Yükümlülükler": [r"k[ıi]sa vadeli yabanc[ıi] kaynaklar", r"k[ıi]sa vadeli yükümlülükler"],"Uzun Vadeli Yükümlülükler": [r"uzun vadeli yabanc[ıi] kaynaklar", r"uzun vadeli yükümlülükler"],"Özkaynaklar": [r"öz kaynaklar", r"özkaynaklar"], "Net Satışlar": [r"net sat[ıi]şlar"],"Satışların Maliyeti": [r"sat[ıi]şlar[ıi]n maliyeti"], "Faaliyet Giderleri": [r"faaliyet giderleri"],"Finansman Giderleri": [r"finansman giderleri"],}

def handle_file_upload():
    if st.session_state.get('uploader_key') is not None:
        st.session_state.file_uploaded = True

def merge_data(existing_data, new_data, new_years):
    existing_years = existing_data.get('yillar', [])
    all_years = sorted(list(set(existing_years + new_years)))
    merged_data = {'yillar': all_years}
    for internal_key, search_terms in KALEM_ESLESTIRME_SÖZLÜGÜ.items():
        merged_values = [0.0] * len(all_years)
        if internal_key in existing_data and existing_data.get(internal_key):
            for i, year in enumerate(existing_years):
                if year in all_years: merged_values[all_years.index(year)] = existing_data[internal_key][i]
        for row in new_data:
            description = row.get('Açıklama', '').lower()
            if any(re.search(term, description) for term in search_terms):
                for year in new_years:
                    if year in all_years: merged_values[all_years.index(year)] = row.get(year, 0.0)
                break
        merged_data[internal_key] = merged_values
    return merged_data

def process_uploaded_data():
    st.session_state.file_uploaded = False 
    uploaded_file = st.session_state.get('uploader_key')
    if uploaded_file is None: return
    try:
        file_name = uploaded_file.name.lower()
        dil = st.session_state.secilen_dil
        if file_name.endswith('.pdf'):
            pdf_data = pdf_verilerini_oku(uploaded_file)
            if pdf_data and pdf_data.get('yillar') and pdf_data.get('tablo_verileri'):
                st.session_state.finansal_veriler = merge_data(st.session_state.finansal_veriler, pdf_data['tablo_verileri'], pdf_data['yillar'])
                message = f"PDF verileri eklendi. Yıllar: {', '.join(st.session_state.finansal_veriler['yillar'])}" if dil == "TR" else f"PDF data added. Years: {', '.join(st.session_state.finansal_veriler['yillar'])}"
                st.session_state.upload_status = ("success", message)
            else:
                st.session_state.upload_status = ("error", "PDF'ten finansal tablo okunamadı." if dil == "TR" else "Could not read financial table from PDF.")
        elif file_name.endswith(('.xlsx', '.xls', '.csv')):
            df_uploaded = pd.read_excel(uploaded_file, index_col=0) if file_name.endswith(('.xlsx', '.xls')) else pd.read_csv(uploaded_file, index_col=0, sep=';', encoding='utf-8')
            df_uploaded.columns = [str(col).strip() for col in df_uploaded.columns]
            df_uploaded.index = [str(idx).strip() for idx in df_uploaded.index]
            excel_years = [col for col in df_uploaded.columns if col.isdigit()]
            excel_table_data = []
            for index, row in df_uploaded.iterrows():
                row_data = {"Açıklama": index}
                for year in excel_years: row_data[year] = parse_tr_number(row.get(year))
                excel_table_data.append(row_data)
            st.session_state.finansal_veriler = merge_data(st.session_state.finansal_veriler, excel_table_data, excel_years)
            message = f"Excel/CSV verileri eklendi. Yıllar: {', '.join(st.session_state.finansal_veriler['yillar'])}" if dil == "TR" else f"Excel/CSV data added. Years: {', '.join(st.session_state.finansal_veriler['yillar'])}"
            st.session_state.upload_status = ("success", message)
        else:
             st.session_state.upload_status = ("error", "Bu dosya formatı desteklenmiyor." if dil == "TR" else "This file format is not supported.")
    except Exception as e:
        message = f"Dosya işlenirken hata oluştu: {e}" if dil == "TR" else f"An error occurred while processing the file: {e}"
        st.session_state.upload_status = ("error", message)
    finally:
        if 'data_editor' in st.session_state:
            del st.session_state['data_editor']

def generate_detailed_analysis(dil):
    if not st.session_state.get('hesaplanan_oranlar'): return {}
    detayli_veri = {}
    oran_basliklari = oran_basliklari_en if dil == "EN" else oran_basliklari_tr
    yillar = st.session_state.finansal_veriler.get('yillar', [])
    for i, yil in enumerate(yillar):
        yil_verisi = []
        for key, values in st.session_state.hesaplanan_oranlar.items():
            if i < len(values):
                val = values[i]
                target, status = get_ratio_evaluation(key, val, dil)
                if key == "EBITDA": formatted_val = format_tr_number(val, 2)
                elif is_percentage_key(key): formatted_val = f"{val * 100:.2f}%" if val is not None and not np.isnan(val) else "N/A"
                else: formatted_val = f"{val:,.2f}" if val is not None and not np.isnan(val) else "N/A"
                degisim_str = "-"
                if i > 0:
                    onceki_val = values[i-1]
                    if onceki_val is not None and onceki_val != 0 and val is not None and not np.isnan(onceki_val) and not np.isnan(val):
                        yuzde_degisim = ((val - onceki_val) / abs(onceki_val)) * 100
                        if yuzde_degisim > 0.01: degisim_str = f"▲ +{yuzde_degisim:.1f}%"
                        elif yuzde_degisim < -0.01: degisim_str = f"▼ {yuzde_degisim:.1f}%"
                        else: degisim_str = "— 0.0%"
                    else: degisim_str = "N/A"
                yil_verisi.append({("Oran" if dil == "TR" else "Ratio"): oran_basliklari.get(key, key), ("Değer" if dil == "TR" else "Value"): formatted_val, ("Yıllık Değişim" if dil == "TR" else "YoY Change"): degisim_str,("Hedef" if dil == "TR" else "Target"): target, ("Durum" if dil == "TR" else "Status"): status})
        detayli_veri[yil] = yil_verisi
    return detayli_veri

# --- TEMEL DEĞİŞKENLER VE OTURUM YÖNETİMİ ---
if 'finansal_veriler' not in st.session_state:
    st.session_state.finansal_veriler = {'yillar': []}
    for key in KALEM_ESLESTIRME_SÖZLÜGÜ.keys(): st.session_state.finansal_veriler[key] = []
if 'hesaplanan_oranlar' not in st.session_state: st.session_state.hesaplanan_oranlar = {}
if 'kredi_skoru_sonucu' not in st.session_state: st.session_state.kredi_skoru_sonucu = {}
if 'secilen_dil' not in st.session_state: st.session_state.secilen_dil = "TR"
if 'secilen_sektor' not in st.session_state: st.session_state.secilen_sektor = "Genel Değerler"

# --- ARAYÜZ ---
st.set_page_config(layout="wide")
st.sidebar.header("Language / Dil")
dil_secenekleri = {"TR": "Türkçe", "EN": "English"}
secilen_dil_kodu = st.sidebar.radio("Dil Seçimi", list(dil_secenekleri.keys()), format_func=lambda x: dil_secenekleri[x], index=list(dil_secenekleri.keys()).index(st.session_state.secilen_dil), key="dil_secimi")
if st.session_state.secilen_dil != secilen_dil_kodu:
    st.session_state.secilen_dil = secilen_dil_kodu
    if 'data_editor' in st.session_state: del st.session_state['data_editor']
    st.rerun()

dil = st.session_state.secilen_dil
st.title("Finansal Analiz ve Kredi Danışmanı" if dil == "TR" else "Financial Analysis and Credit Advisor")
menu_tr = ["Veri Girişi", "Hesaplanan Oranlar ve Yorumlama", "Kredi Skoru ve Analizi", "Referans Değerler", "Çıktı Al", "Verileri Kaydet / Yükle"]
menu_en = ["Data Entry", "Calculated Ratios & Interpretation", "Credit Score & Analysis", "Reference Values", "Get Output", "Save / Load Data"]
menu_options = menu_en if dil == "EN" else menu_tr
uyari_veri_girisi = "Lütfen önce 'Veri Girişi' sayfasından analiz yapın." if dil == "TR" else "Please perform an analysis from the 'Data Entry' page first."
st.sidebar.title("Menü" if dil == "TR" else "Menu")
choice = st.sidebar.radio("Git" if dil == "TR" else "Go", menu_options)

if st.session_state.file_uploaded:
    process_uploaded_data()

if choice == menu_options[0]:
    st.header("1. " + ("Finansal Veri Girişi" if dil == "TR" else "Enter Financial Data"))
    tab1, tab2 = st.tabs(["Dosya Yükleyerek Giriş" if dil=="TR" else "Upload a File", "Manuel Giriş" if dil=="TR" else "Manual Entry"])
    with tab1:
        st.subheader("Seçenek 1: Rapor Yükle (PDF, Excel, CSV)" if dil == "TR" else "Option 1: Upload Report (PDF, Excel, CSV)")
        st.info("💡 " + ("Analize başlamak için bir veya daha fazla finansal rapor yükleyin." if dil == "TR" else "💡 Upload one or more financial reports to begin the analysis."))
        st.file_uploader("Finansal Rapor Yükle" if dil == "TR" else "Upload Financial Report", type=['pdf', 'xlsx', 'xls', 'csv'], key='uploader_key', on_change=handle_file_upload)
    with tab2:
        st.subheader("Seçenek 2: Verileri Manuel Girin" if dil == "TR" else "Option 2: Enter Data Manually")
        years_input = st.text_input(label="Analiz edilecek yılları girin (virgülle ayırarak, örn: 2022, 2023, 2024)" if dil == "TR" else "Enter years to analyze (comma-separated, e.g., 2022, 2023, 2024)", placeholder="2022, 2023, 2024")
        if st.button("Manuel Giriş Tablosu Oluştur" if dil == "TR" else "Create Manual Entry Table"):
            if years_input:
                try:
                    parsed_years = sorted([y.strip() for y in years_input.split(',') if y.strip().isdigit()])
                    if parsed_years:
                        st.session_state.finansal_veriler = {'yillar': parsed_years}
                        for key in KALEM_ESLESTIRME_SÖZLÜGÜ.keys(): st.session_state.finansal_veriler[key] = [0.0] * len(parsed_years)
                        st.session_state.hesaplanan_oranlar = {}; st.session_state.kredi_skoru_sonucu = {}
                        if 'data_editor' in st.session_state: del st.session_state['data_editor']
                        st.rerun()
                    else: st.warning("Lütfen geçerli yıl(lar) girin." if dil == "TR" else "Please enter valid year(s).")
                except Exception: st.error("Yılları ayrıştırırken bir hata oluştu." if dil == "TR" else "Error parsing years.")
    st.divider()
    if st.button("🔄 " + ("Tüm Verileri Temizle" if dil == "TR" else "Clear All Data")):
        st.session_state.finansal_veriler = {'yillar': []}
        for key in KALEM_ESLESTIRME_SÖZLÜGÜ.keys(): st.session_state.finansal_veriler[key] = []
        st.session_state.hesaplanan_oranlar = {}; st.session_state.kredi_skoru_sonucu = {}
        if 'data_editor' in st.session_state: del st.session_state['data_editor']
        st.rerun()
    if 'upload_status' in st.session_state:
        status, message = st.session_state.upload_status
        if status == "success": st.success(message)
        else: st.error(message)
        del st.session_state.upload_status
    if st.session_state.finansal_veriler.get('yillar'):
        st.subheader("Veri Giriş Tablosu" if dil == "TR" else "Data Entry Table")
        edited_df = st.data_editor(build_grid_df(st.session_state.finansal_veriler, dil), use_container_width=True, num_rows="fixed", key="data_editor")
        if st.button("Hesapla ve Analiz Et" if dil == "TR" else "Calculate and Analyze", type="primary"):
            try:
                grid_to_numeric_state(edited_df, st.session_state.finansal_veriler)
                st.session_state.hesaplanan_oranlar = finansal_oranlari_hesapla(st.session_state.finansal_veriler)
                st.session_state.kredi_skoru_sonucu = kredi_skoru_hesapla(st.session_state.hesaplanan_oranlar, st.session_state.finansal_veriler.get('yillar', []))
                st.success("Hesaplama tamamlandı! Analiz sonuçlarını diğer sekmelerden görebilirsiniz." if dil == "TR" else "Calculation complete! You can view the analysis results in the other tabs.")
                if 'data_editor' in st.session_state: del st.session_state['data_editor']
                ### <-- DÜZELTME: Bu satırı kaldırarak mesajın görünmesini sağlıyoruz.
                # st.rerun() 
            except Exception as e:
                st.error(f"{'Hesaplama hatası' if dil == 'TR' else 'Calculation error'}: {e}")
    else:
        st.info("Görüntülenecek veri yok. Lütfen bir dosya yükleyin veya manuel olarak tablo oluşturun." if dil == "TR" else "No data to display. Please upload a file or create a table manually.")

elif choice == menu_options[1]:
    st.header("2. " + ("Hesaplanan Oranlar ve Yorumlama" if dil == "TR" else "Calculated Ratios & Interpretation"))
    if not st.session_state.get('hesaplanan_oranlar'):
        st.warning(uyari_veri_girisi)
    else:
        detayli_analiz = generate_detailed_analysis(dil)
        for yil, yil_verisi in detayli_analiz.items():
            expander_title = f"**{yil} Yılı Analizi**" if dil == "TR" else f"**Analysis for Year {yil}**"
            with st.expander(expander_title, expanded=(yil == list(detayli_analiz.keys())[-1])):
                if yil_verisi:
                    df_year = pd.DataFrame(yil_verisi).set_index("Oran" if dil == "TR" else "Ratio")
                    def color_status(val):
                        color = 'red' if val in ["Zayıf", "Weak"] else 'orange' if val in ["Orta", "Average"] else 'green' if val in ["İyi", "Good"] else 'black'
                        return f'color: {color}'
                    def color_degisim(val):
                        if isinstance(val, str):
                            if '▲' in val: return 'color: green'
                            if '▼' in val: return 'color: red'
                        return 'color: black'
                    st.dataframe(df_year.style.map(color_status, subset=['Durum' if dil == 'TR' else 'Status']).map(color_degisim, subset=['Yıllık Değişim' if dil == 'TR' else 'YoY Change']), use_container_width=True)

# ... (Diğer menü seçenekleri - değişiklik yok) ...

elif choice == menu_options[2]:
    st.header("3. " + ("Kredi Skoru ve Analizi" if dil == "TR" else "Credit Score & Analysis"))
    if not st.session_state.get('kredi_skoru_sonucu'): st.warning(uyari_veri_girisi)
    else:
        for yil, skor in st.session_state.kredi_skoru_sonucu.items():
            st.subheader(f"{'Yıl' if dil == 'TR' else 'Year'}: {yil}")
            c1, c2 = st.columns([1, 2])
            with c1:
                st.metric("Toplam Kredi Skoru" if dil == "TR" else "Total Credit Score", f"{skor.get('toplam_skor', 0):.0f}")
                degerlendirme = skor.get('degerlendirme') if dil == "TR" else skor.get('degerlendirme_en')
                st.markdown(f"**{'Değerlendirme' if dil == 'TR' else 'Evaluation'}:** {degerlendirme}")
            with c2:
                st.markdown(f"**{'Olumlu Yönler' if dil == 'TR' else 'Strengths'}**")
                for p in skor.get('olumlu_yonler' if dil == "TR" else 'olumlu_yonler_en', []): st.markdown(f"- {p}")
                st.markdown(f"**{'Olumsuz Yönler' if dil == 'TR' else 'Weaknesses'}**")
                for n in skor.get('olumsuz_yonler' if dil == "TR" else 'olumsuz_yonler_en', []): st.markdown(f"- {n}")
            st.divider()

elif choice == menu_options[3]:
    st.header(menu_options[3])
    sektor_listesi = list(SEKTOR_HEDEFLERI.keys())
    index = sektor_listesi.index(st.session_state.secilen_sektor) if st.session_state.secilen_sektor in sektor_listesi else 0
    secilen = st.selectbox("Değerlendirme yapmak için bir sektör seçin." if dil == "TR" else "Select a sector for evaluation.", sektor_listesi, index=index)
    if secilen != st.session_state.secilen_sektor:
        st.session_state.secilen_sektor = secilen
        st.rerun()
    st.markdown("---")
    st.subheader(f"'{st.session_state.secilen_sektor}' " + ("Sektörü İçin Hedef Değerler" if dil == "TR" else "Sector Target Values"))
    hedef_verisi = SEKTOR_HEDEFLERI.get(st.session_state.secilen_sektor, SEKTOR_HEDEFLERI["Genel Değerler"])
    aciklama_verisi = SEKTOR_ACIKLAMALARI.get("Genel Değerler", [])
    for oran_aciklamasi in aciklama_verisi:
        oran_key = oran_aciklamasi["oran"]
        if oran_key in hedef_verisi:
            guncel_hedef = hedef_verisi[oran_key]["hedef"]
            expander_title = f"**{oran_key}** (" + (f"Sektör Hedefi: {guncel_hedef})" if dil == "TR" else f"Sector Target: {guncel_hedef})")
            with st.expander(expander_title):
                st.write(oran_aciklamasi['aciklama'])

elif choice == menu_options[4]:
    st.header("5. " + menu_options[4])
    if not st.session_state.get('hesaplanan_oranlar'): st.warning(uyari_veri_girisi)
    else:
        dosya_adi = st.text_input("Dosya adı" if dil == "TR" else "File name", value="financial_report")
        detayli_analiz_for_output = generate_detailed_analysis(dil)
        excel_buffer = BytesIO()
        if excel_cikti_al(st.session_state.finansal_veriler, st.session_state.hesaplanan_oranlar, st.session_state.kredi_skoru_sonucu, detayli_analiz_for_output, dil, excel_buffer):
            st.download_button("Excel İndir" if dil == "TR" else "Download Excel", excel_buffer.getvalue(), f"{dosya_adi}.xlsx")
        word_buffer = BytesIO()
        if word_cikti_al(st.session_state.finansal_veriler, st.session_state.hesaplanan_oranlar, st.session_state.kredi_skoru_sonucu, detayli_analiz_for_output, dil, word_buffer):
            st.download_button("Word İndir" if dil == "TR" else "Download Word", word_buffer.getvalue(), f"{dosya_adi}.docx")

elif choice == menu_options[5]:
    st.header("6. " + menu_options[5])
    save_dir = "saved_data"
    os.makedirs(save_dir, exist_ok=True)
    files = [f for f in os.listdir(save_dir) if f.endswith(".json")]
    c1, c2 = st.columns(2)
    with c1:
        filename = st.text_input("Kaydedilecek dosya adı" if dil == "TR" else "File name to save", "dataset1")
        if st.button("Verileri Kaydet" if dil == "TR" else "Save Data"):
            path = os.path.join(save_dir, f"{filename}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(st.session_state.finansal_veriler, f, ensure_ascii=False, indent=4)
            st.success("Veri kaydedildi!" if dil == "TR" else "Data saved!")
    with c2:
        if files:
            selected = st.selectbox("Yüklenecek dosyayı seçin" if dil == "TR" else "Select file to load", files)
            if st.button("Veriyi Yükle" if dil == "TR" else "Load Data"):
                with open(os.path.join(save_dir, selected), "r", encoding="utf-8") as f:
                    st.session_state.finansal_veriler = json.load(f)
                st.session_state.hesaplanan_oranlar = {}; st.session_state.kredi_skoru_sonucu = {}
                if 'data_editor' in st.session_state: del st.session_state['data_editor']
                st.success("Veri yüklendi!" if dil == "TR" else "Data loaded!")
                st.rerun()