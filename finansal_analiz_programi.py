# finansal_analiz_programi.py

# Gerekli kütüphaneleri ve kendi modüllerimizi içe aktarıyoruz (import ediyoruz)
import os
from hesaplamalar import finansal_oranlari_hesapla, oran_basliklari_tr, oran_basliklari_en
from skorlama import kredi_skoru_hesapla
from cikti_islemleri import excel_cikti_al, word_cikti_al

# Bu sözlük (dictionary), girilen verileri hafızada tutacak.
# Programı kapatıp açana kadar veriler burada kalır.
finansal_veriler = {}
hesaplanan_oranlar = {}
kredi_skoru_sonucu = {}
secilen_dil = "TR" # Varsayılan dil Türkçe


def clear_screen():
    # Ekranı temizleme komutu. Windows'ta 'cls', diğer sistemlerde 'clear' kullanır.
    os.system('cls' if os.name == 'nt' else 'clear')


def veri_girisi():
    """Kullanıcıdan şirket finansal verilerini alır."""
    global finansal_veriler # Bu değişkeni fonksiyon dışından değiştireceğimizi belirtiyoruz
    global hesaplanan_oranlar
    global kredi_skoru_sonucu

    print("\n--- Finansal Veri Girişi ---")
    print("Lütfen şirketin son 3 yıllık finansal verilerini girin.")
    print("Verileri girdikten sonra 'Enter' tuşuna basarak devam edin.")
    
    # Yıl bilgilerini manuel olarak alalım
    while True:
        try:
            yil_1 = input("İlk yıl (örn: 2022): ")
            yil_2 = input("İkinci yıl (örn: 2023): ")
            yil_3 = input("Üçüncü yıl (örn: 2024): ")
            finansal_veriler['yillar'] = [yil_1, yil_2, yil_3]
            break
        except ValueError:
            print("Geçersiz yıl formatı. Lütfen sayı girin.")

    # Finansal kalemlerin başlıkları ve her bir yıl için veri girişi
    # Bu kısmı daha düzenli hale getirelim
    kalemler = {
        "Dönen Varlıklar": "Bilanço",
        "Duran Varlıklar": "Bilanço",
        "Kısa Vadeli Yükümlülükler": "Bilanço",
        "Uzun Vadeli Yükümlülükler": "Bilanço",
        "Özkaynaklar": "Bilanço",
        "Net Satışlar": "Gelir Tablosu",
        "Satışların Maliyeti": "Gelir Tablosu",
        "Faaliyet Giderleri": "Gelir Tablosu",
        "Finansman Giderleri": "Gelir Tablosu",
    }

    # Her bir kalem için kullanıcıdan yıllara göre veri alıyoruz
    for kalem_adi, tablo_turu in kalemler.items():
        finansal_veriler[kalem_adi] = []
        for yil in finansal_veriler['yillar']:
            while True:
                try:
                    deger = float(input(f"{kalem_adi} ({yil} - {tablo_turu}, Bin TL): "))
                    finansal_veriler[kalem_adi].append(deger)
                    break
                except ValueError:
                    print("Geçersiz giriş. Lütfen sayısal bir değer girin.")
    
    # Veriler girildikten sonra hesaplamaları otomatik yapalım
    print("\nVeriler başarıyla alındı. Şimdi finansal oranlar hesaplanıyor...")
    hesaplanan_oranlar = finansal_oranlari_hesapla(finansal_veriler)
    kredi_skoru_sonucu = kredi_skoru_hesapla(hesaplanan_oranlar, finansal_veriler['yillar'])

    input("\nVeri girişi ve hesaplamalar tamamlandı. Devam etmek için Enter'a basın.")
    clear_screen()


def oranlari_goster():
    """Hesaplanan finansal oranları ekrana yazdırır."""
    if not hesaplanan_oranlar:
        print("Önce 'Veri Girşi' yapmalısınız.")
        return

    print("\n--- Finansal Oranlar Raporu ---")
    yillar = finansal_veriler['yillar']

    # Başlıkları dile göre seçelim
    oran_basliklari = oran_basliklari_tr if secilen_dil == "TR" else oran_basliklari_en

    # Oranları tablo formatında yazdıralım
    print(f"{'Oran Adı':<40} | {yillar[0]:<10} | {yillar[1]:<10} | {yillar[2]:<10}")
    print("-" * 80)

    for oran_adi, degerler in hesaplanan_oranlar.items():
        # Oran adını dile göre çevirelim
        gorunen_oran_adi = oran_basliklari.get(oran_adi, oran_adi)
        
        # Yüzdelik olanları % olarak gösterelim
        if "Marjı" in oran_adi: # Kar marjları için yüzde formatı
             print(f"{gorunen_oran_adi:<40} | {degerler[0]*100:<9.2f}% | {degerler[1]*100:<9.2f}% | {degerler[2]*100:<9.2f}%")
        else:
             print(f"{gorunen_oran_adi:<40} | {degerler[0]:<10.2f} | {degerler[1]:<10.2f} | {degerler[2]:<10.2f}")
    
    input("\nDevam etmek için Enter'a basın.")
    clear_screen()


def skorlama_goster():
    """Kredi skorlama sonuçlarını ve açıklamayı ekrana yazdırır."""
    if not kredi_skoru_sonucu:
        print("Önce 'Veri Girişi' yapmalısınız.")
        return

    print("\n--- Kredi Skorlama Raporu ---")
    
    # Skoru en güncel yıla göre alalım (son yılın skoru)
    son_yil_skor_bilgisi = kredi_skoru_sonucu[finansal_veriler['yillar'][-1]]

    # Dile göre çıktı verelim
    if secilen_dil == "TR":
        print(f"\nŞirketin {finansal_veriler['yillar'][-1]} Yılı Kredi Skoru: {son_yil_skor_bilgisi['toplam_skor']:.2f}")
        print("Değerlendirme:", son_yil_skor_bilgisi['degerlendirme'])
        print("\n--- Olumlu Yönler ---")
        for i, yon in enumerate(son_yil_skor_bilgisi['olumlu_yonler']):
            print(f"{i+1}. {yon}")
        print("\n--- Olumsuz Yönler ---")
        for i, yon in enumerate(son_yil_skor_bilgisi['olumsuz_yonler']):
            print(f"{i+1}. {yon}")
    else: # English
        print(f"\nCompany's Credit Score for {finansal_veriler['yillar'][-1]}: {son_yil_skor_bilgisi['toplam_skor']:.2f}")
        print("Evaluation:", son_yil_skor_bilgisi['degerlendirme_en'])
        print("\n--- Strengths ---")
        for i, yon in enumerate(son_yil_skor_bilgisi['olumlu_yonler_en']):
            print(f"{i+1}. {yon}")
        print("\n--- Weaknesses ---")
        for i, yon in enumerate(son_yil_skor_bilgisi['olumsuz_yonler_en']):
            print(f"{i+1}. {yon}")

    input("\nDevam etmek için Enter'a basın.")
    clear_screen()


def dil_secimi():
    """Kullanıcının dil seçimi yapmasını sağlar."""
    global secilen_dil
    print("\n--- Dil Seçimi ---")
    print("1. Türkçe (TR)")
    print("2. English (EN)")
    
    while True:
        secim = input("Lütfen bir dil seçin (1 veya 2): ")
        if secim == "1":
            secilen_dil = "TR"
            print("Dil Türkçe olarak ayarlandı.")
            break
        elif secim == "2":
            secilen_dil = "EN"
            print("Language set to English.")
            break
        else:
            print("Geçersiz seçim. Lütfen 1 veya 2 girin.")
    input("\nDevam etmek için Enter'a basın.")
    clear_screen()


def ana_menu():
    """Ana menüyü gösterir ve kullanıcıdan işlem seçimi alır."""
    while True:
        print("\n--- Finansal Analiz Programı Ana Menü ---")
        if secilen_dil == "TR":
            print("1. Finansal Veri Girişi")
            print("2. Hesaplanan Oranları Görüntüle")
            print("3. Kredi Skorunu ve Analizi Görüntüle")
            print("4. Çıktı Al (Excel / Word)")
            print("5. Dil Seçimi")
            print("6. Programı Kapat")
        else: # English
            print("1. Enter Financial Data")
            print("2. View Calculated Ratios")
            print("3. View Credit Score and Analysis")
            print("4. Get Output (Excel / Word)")
            print("5. Language Selection")
            print("6. Exit Program")

        secim = input("Lütfen bir işlem seçin: ")

        if secim == "1":
            veri_girisi()
        elif secim == "2":
            oranlari_goster()
        elif secim == "3":
            skorlama_goster()
        elif secim == "4":
            if not hesaplanan_oranlar:
                print("Önce 'Veri Girişi' yapmalısınız.")
                input("Devam etmek için Enter'a basın.")
                clear_screen()
                continue
            
            print("\n--- Çıktı Alma Seçenekleri ---")
            if secilen_dil == "TR":
                print("1. Excel Çıktısı")
                print("2. Word Çıktısı")
                print("3. Geri Dön")
            else:
                print("1. Excel Output")
                print("2. Word Output")
                print("3. Go Back")

            cikti_secim = input("Lütfen bir çıktı formatı seçin: ")
            
            if cikti_secim == "1":
                dosya_adi_excel = input("Excel dosya adı (örn: rapor): ")
                excel_cikti_al(finansal_veriler, hesaplanan_oranlar, kredi_skoru_sonucu, secilen_dil, dosya_adi_excel)
                if secilen_dil == "TR": print(f"'{dosya_adi_excel}.xlsx' başarıyla oluşturuldu.")
                else: print(f"'{dosya_adi_excel}.xlsx' successfully created.")
            elif cikti_secim == "2":
                dosya_adi_word = input("Word dosya adı (örn: rapor): ")
                word_cikti_al(finansal_veriler, hesaplanan_oranlar, kredi_skoru_sonucu, secilen_dil, dosya_adi_word)
                if secilen_dil == "TR": print(f"'{dosya_adi_word}.docx' başarıyla oluşturuldu.")
                else: print(f"'{dosya_adi_word}.docx' successfully created.")
            elif cikti_secim == "3":
                pass # Geri dön
            else:
                if secilen_dil == "TR": print("Geçersiz seçim.")
                else: print("Invalid selection.")
            input("\nDevam etmek için Enter'a basın.")
            clear_screen()
        elif secim == "5":
            dil_secimi()
        elif secim == "6":
            if secilen_dil == "TR": print("Program kapatılıyor. Güle güle Murat!")
            else: print("Program closing. Goodbye Murat!")
            break
        else:
            if secilen_dil == "TR": print("Geçersiz seçim. Lütfen geçerli bir sayı girin.")
            else: print("Invalid selection. Please enter a valid number.")
        
# Program başladığında ana menüyü çalıştır
if __name__ == "__main__":
    ana_menu()