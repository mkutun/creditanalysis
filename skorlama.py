# skorlama.py - GÜNCEL VE SAĞLAM VERSİYON

def kredi_skoru_hesapla(oranlar: dict, yillar: list) -> dict:
    skor_sonuclari = {}

    # Her bir oranı daha güvenli bir şekilde almak için bir yardımcı fonksiyon
    def get_ratio_value(ratio_name, index):
        ratio_list = oranlar.get(ratio_name, [])
        return ratio_list[index] if index < len(ratio_list) else None

    for i, yil in enumerate(yillar):
        toplam_skor = 0
        olumlu_yonler, olumsuz_yonler = [], []
        olumlu_yonler_en, olumsuz_yonler_en = [], []

        # Cari Oran > 1.5 iyi
        cari_oran = get_ratio_value("Cari Oran", i)
        if cari_oran is not None:
            if cari_oran >= 1.5:
                toplam_skor += 20
                olumlu_yonler.append("Cari oran (likidite seviyesi) güçlü.")
                olumlu_yonler_en.append("Current ratio (liquidity level) is strong.")
            elif cari_oran < 1.0:
                toplam_skor -= 15
                olumsuz_yonler.append("Cari oran çok düşük, acil likidite riski var.")
                olumsuz_yonler_en.append("Current ratio is very low, immediate liquidity risk.")
            else:
                toplam_skor -= 5
                olumsuz_yonler.append("Cari oran düşük, likiditeye dikkat edilmeli.")
                olumsuz_yonler_en.append("Current ratio is low, liquidity should be monitored.")

        # Borç / Özkaynak < 1.5 iyi
        debt_eq = get_ratio_value("Borç / Özkaynak Oranı", i)
        if debt_eq is not None:
            if debt_eq < 1.5:
                toplam_skor += 20
                olumlu_yonler.append("Borç/Özkaynak oranı makul ve sağlıklı seviyede.")
                olumlu_yonler_en.append("Debt to Equity ratio is at a reasonable and healthy level.")
            else:
                toplam_skor -= 15
                olumsuz_yonler.append("Borç/Özkaynak oranı yüksek, şirket borca bağımlı.")
                olumsuz_yonler_en.append("High Debt to Equity ratio, the company is reliant on debt.")

        # Net Kar Marjı > %8 iyi
        net_margin = get_ratio_value("Net Kar Marjı", i)
        if net_margin is not None:
            if net_margin > 0.08:
                toplam_skor += 20
                olumlu_yonler.append("Net kar marjı güçlü, kârlılık yüksek.")
                olumlu_yonler_en.append("Net profit margin is strong, indicating high profitability.")
            else:
                toplam_skor -= 10
                olumsuz_yonler.append("Net kar marjı zayıf, kârlılık düşük.")
                olumsuz_yonler_en.append("Net profit margin is weak, indicating low profitability.")
        
        # EBITDA Marjı > %15 iyi
        ebitda_margin = get_ratio_value("EBITDA Marjı", i)
        if ebitda_margin is not None:
            if ebitda_margin > 0.15:
                toplam_skor += 20
                olumlu_yonler.append("EBITDA marjı çok iyi, operasyonel verimlilik yüksek.")
                olumlu_yonler_en.append("EBITDA margin is very good, high operational efficiency.")
            elif ebitda_margin < 0.05:
                 toplam_skor -= 15
                 olumsuz_yonler.append("EBITDA marjı çok düşük, operasyonel kârlılık zayıf.")
                 olumsuz_yonler_en.append("EBITDA margin is very low, poor operational profitability.")

        # ROE > %15 iyi
        roe = get_ratio_value("Özkaynak Karlılığı (ROE)", i)
        if roe is not None:
            if roe > 0.15:
                toplam_skor += 20
                olumlu_yonler.append("Özkaynak kârlılığı yüksek, ortak sermayesi verimli kullanılıyor.")
                olumlu_yonler_en.append("Return on Equity is high, shareholder equity is used efficiently.")
            else:
                toplam_skor -= 10
                olumsuz_yonler.append("Özkaynak kârlılığı düşük, sermaye verimsiz kullanılıyor.")
                olumsuz_yonler_en.append("Return on Equity is low, capital is used inefficiently.")

        # Genel değerlendirme
        if toplam_skor >= 80:
            degerlendirme, degerlendirme_en = "Çok İyi", "Excellent"
        elif toplam_skor >= 60:
            degerlendirme, degerlendirme_en = "İyi", "Good"
        elif toplam_skor >= 40:
            degerlendirme, degerlendirme_en = "Orta", "Average"
        else:
            degerlendirme, degerlendirme_en = "Zayıf", "Weak"

        skor_sonuclari[yil] = {
            "toplam_skor": toplam_skor,
            "degerlendirme": degerlendirme, "degerlendirme_en": degerlendirme_en,
            "olumlu_yonler": olumlu_yonler, "olumlu_yonler_en": olumlu_yonler_en,
            "olumsuz_yonler": olumsuz_yonler, "olumsuz_yonler_en": olumsuz_yonler_en,
        }

    return skor_sonuclari