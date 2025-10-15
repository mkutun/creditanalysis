# hesaplamalar.py - GÜNCEL VERSİYON

import numpy as np

# ---------------- Başlıklar (TR/EN) ----------------
oran_basliklari_tr = {
    "Cari Oran": "Cari Oran",
    "Likidite Oranı": "Likidite Oranı",
    "Finansal Kaldıraç": "Finansal Kaldıraç",
    "Borç / Özkaynak Oranı": "Borç / Özkaynak Oranı",
    "Net Kar Marjı": "Net Kar Marjı",
    "Brüt Kar Marjı": "Brüt Kar Marjı",
    "Faaliyet Kar Marjı": "Faaliyet Kar Marjı",
    "Aktif Karlılığı (ROA)": "Aktif Karlılığı (ROA)",
    "Özkaynak Karlılığı (ROE)": "Özkaynak Karlılığı (ROE)",
    "EBITDA": "EBITDA",
    "EBITDA Marjı": "EBITDA Marjı"  # YENİ EKLENDİ
}

oran_basliklari_en = {
    "Cari Oran": "Current Ratio",
    "Likidite Oranı": "Quick Ratio",
    "Finansal Kaldıraç": "Financial Leverage",
    "Borç / Özkaynak Oranı": "Debt to Equity Ratio",
    "Net Kar Marjı": "Net Profit Margin",
    "Brüt Kar Marjı": "Gross Profit Margin",
    "Faaliyet Kar Marjı": "Operating Profit Margin",
    "Aktif Karlılığı (ROA)": "Return on Assets (ROA)",
    "Özkaynak Karlılığı (ROE)": "Return on Equity (ROE)",
    "EBITDA": "EBITDA",
    "EBITDA Marjı": "EBITDA Margin"  # YENİ EKLENDİ
}


# ---------------- Finansal Oran Hesaplama ----------------
def finansal_oranlari_hesapla(veriler: dict) -> dict:
    try:
        yillar = veriler['yillar']
        n = len(yillar)
        oranlar = {}

        gerekli_anahtarlar = [
            "Dönen Varlıklar", "Kısa Vadeli Yükümlülükler", "Duran Varlıklar",
            "Özkaynaklar", "Uzun Vadeli Yükümlülükler", "Net Satışlar",
            "Satışların Maliyeti", "Faaliyet Giderleri", "Finansman Giderleri"
        ]
        for anahtar in gerekli_anahtarlar:
            veriler.setdefault(anahtar, [0.0] * n)

        # Cari Oran
        oranlar["Cari Oran"] = [
            veriler["Dönen Varlıklar"][i] / veriler["Kısa Vadeli Yükümlülükler"][i]
            if veriler["Kısa Vadeli Yükümlülükler"][i] != 0 else np.nan
            for i in range(n)
        ]

        # Likidite Oranı (Stoklar hariç dönen varlıklar / KVYK)
        # Stoklar olmadığı için Dönen Varlıkların belirli bir yüzdesini alarak yaklaştırabiliriz.
        # Genelde stoklar %20-30 civarıdır. Burada %30 düşerek hesaplayalım.
        oranlar["Likidite Oranı"] = [
            (veriler["Dönen Varlıklar"][i] * 0.7) / veriler["Kısa Vadeli Yükümlülükler"][i]
            if veriler["Kısa Vadeli Yükümlülükler"][i] != 0 else np.nan
            for i in range(n)
        ]

        # Finansal Kaldıraç (Toplam Varlıklar / Özkaynaklar)
        toplam_varliklar = [veriler["Dönen Varlıklar"][i] + veriler["Duran Varlıklar"][i] for i in range(n)]
        oranlar["Finansal Kaldıraç"] = [
            toplam_varliklar[i] / veriler["Özkaynaklar"][i]
            if veriler["Özkaynaklar"][i] != 0 else np.nan
            for i in range(n)
        ]
        
        # Borç/Özkaynak Oranı
        toplam_borc = [veriler["Kısa Vadeli Yükümlülükler"][i] + veriler["Uzun Vadeli Yükümlülükler"][i] for i in range(n)]
        oranlar["Borç / Özkaynak Oranı"] = [
            toplam_borc[i] / veriler["Özkaynaklar"][i]
            if veriler["Özkaynaklar"][i] != 0 else np.nan
            for i in range(n)
        ]

        # Karlılık Hesaplamaları
        brut_kar = [veriler["Net Satışlar"][i] - veriler["Satışların Maliyeti"][i] for i in range(n)]
        faaliyet_kari = [brut_kar[i] - veriler["Faaliyet Giderleri"][i] for i in range(n)]
        net_kar = [faaliyet_kari[i] - veriler["Finansman Giderleri"][i] for i in range(n)]

        # EBITDA (FAVÖK) - RAKAMSAL DEĞER
        # Not: Gerçek EBITDA için amortisman eklenmelidir. Bu basitleştirilmiş bir yaklaşımdır.
        oranlar["EBITDA"] = faaliyet_kari

        # Marjlar
        oranlar["Brüt Kar Marjı"] = [brut_kar[i] / veriler["Net Satışlar"][i] if veriler["Net Satışlar"][i] != 0 else np.nan for i in range(n)]
        oranlar["Faaliyet Kar Marjı"] = [faaliyet_kari[i] / veriler["Net Satışlar"][i] if veriler["Net Satışlar"][i] != 0 else np.nan for i in range(n)]
        oranlar["Net Kar Marjı"] = [net_kar[i] / veriler["Net Satışlar"][i] if veriler["Net Satışlar"][i] != 0 else np.nan for i in range(n)]
        
        # YENİ: EBITDA Marjı - YÜZDESEL DEĞER
        oranlar["EBITDA Marjı"] = [
            faaliyet_kari[i] / veriler["Net Satışlar"][i]
            if veriler["Net Satışlar"][i] != 0 else np.nan
            for i in range(n)
        ]

        # Varlık ve Özkaynak Karlılığı
        oranlar["Aktif Karlılığı (ROA)"] = [net_kar[i] / toplam_varliklar[i] if toplam_varliklar[i] != 0 else np.nan for i in range(n)]
        oranlar["Özkaynak Karlılığı (ROE)"] = [net_kar[i] / veriler["Özkaynaklar"][i] if veriler["Özkaynaklar"][i] != 0 else np.nan for i in range(n)]

        return oranlar

    except Exception as e:
        print(f"Hesaplama hatası: {e}")
        return {}