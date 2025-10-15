# pdf_okuyucu.py - SANAYİ SINIFI VERSİYON (NİHAİ ÇÖZÜM)

import fitz  # PyMuPDF
import re
import io
from collections import defaultdict
import pandas as pd

def parse_tr_number(s: str) -> float:
    """Sayısal metinleri temizleyip ondalık sayıya çevirir."""
    if s is None: return 0.0
    if isinstance(s, (int, float)): return float(s)
    s = str(s).strip()
    if not s or s.lower() in ['nan', 'none', '', '-']: return 0.0
    if s.startswith('(') and s.endswith(')'): s = '-' + s[1:-1]
    s = re.sub(r'[^\d,.-]', '', s)
    try:
        # Önce binlik ayırıcı olan noktaları kaldır, sonra ondalık ayırıcı olan virgülü noktaya çevir
        if ',' in s and '.' in s:
             # Eğer son ayırıcı noktaysa, virgülleri kaldır (1,234.56 formatı)
            if s.rfind('.') > s.rfind(','):
                s = s.replace(',', '')
            # Eğer son ayırıcı virgülse, noktaları kaldır (1.234,56 formatı)
            else:
                s = s.replace('.', '').replace(',', '.')
        else:
            s = s.replace(',', '.')
        return float(s)
    except (ValueError, TypeError):
        return 0.0

def pdf_verilerini_oku(uploaded_file):
    """
    Sanayi Sınıfı Analiz Motoru: PDF sayfasını koordinat tabanlı bir grid'e dönüştürerek
    tabloyu yeniden inşa eder. Tahmin yok, sadece geometrik kesinlik.
    """
    try:
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=io.BytesIO(pdf_bytes))
        
        all_pages_data = []
        all_years_found = set()

        for page_num, page in enumerate(doc):
            # Sayfadaki tüm kelimeleri koordinatlarıyla birlikte al
            words = page.get_text("words")
            if not words:
                continue

            # Kelimeleri satırlara grupla
            y_tolerance = 2
            lines = defaultdict(list)
            for w in words:
                # w -> [x0, y0, x1, y1, "word", block_no, line_no, word_no]
                y1 = round(w[3] / y_tolerance) * y_tolerance
                lines[y1].append(w)

            # Sütunları bul
            columns = []
            page_height = page.rect.height
            # Sadece sayfanın üst yarısındaki yıl başlıklarını ara
            for y1 in sorted(lines.keys()):
                if y1 > page_height / 1.5 and columns:
                    break
                line_text = " ".join(w[4] for w in sorted(lines[y1], key=lambda w: w[0]))
                
                year_matches = re.findall(r'\((\d{4})\)', line_text)
                if year_matches:
                    for year in year_matches:
                        for word_info in lines[y1]:
                            if year in word_info[4]:
                                x_center = (word_info[0] + word_info[2]) / 2
                                columns.append({'year': year, 'x_center': x_center})
            
            if not columns:
                continue

            # Sütunları x-koordinatına göre sırala ve tekilleştir
            columns = sorted(columns, key=lambda c: c['x_center'])
            unique_columns = []
            seen_x = -100
            for col in columns:
                if col['x_center'] > seen_x + 50: # Genişlik toleransı
                    unique_columns.append(col)
                    seen_x = col['x_center']
            columns = unique_columns
            page_years = [c['year'] for c in columns]
            all_years_found.update(page_years)

            if not columns:
                continue

            # Tabloyu satır satır yeniden oluştur
            page_data = []
            first_col_x = columns[0]['x_center'] - 50 # Tolerans

            for y1 in sorted(lines.keys()):
                line_words = sorted(lines[y1], key=lambda w: w[0])
                
                description_parts = []
                number_items = []

                for word_info in line_words:
                    word_text = word_info[4]
                    x_center = (word_info[0] + word_info[2]) / 2
                    
                    if x_center < first_col_x:
                        description_parts.append(word_text)
                    else:
                        if re.search(r'\d', word_text):
                            number_items.append({'text': word_text, 'x_center': x_center})
                
                description = " ".join(description_parts)
                if not description or len(description) < 3:
                    continue

                row_data = {'Açıklama': description}
                
                for col in columns:
                    best_match_val = 0.0
                    min_dist = float('inf')
                    for num_item in number_items:
                        dist = abs(num_item['x_center'] - col['x_center'])
                        if dist < min_dist:
                            min_dist = dist
                            best_match_val = parse_tr_number(num_item['text'])
                    row_data[col['year']] = best_match_val

                if any(val != 0.0 for key, val in row_data.items() if key != 'Açıklama'):
                    all_pages_data.append(row_data)

        if not all_pages_data:
            print("Uyarı: PDF içinde okunabilir bir finansal tablo yapısı bulunamadı.")
            return None

        return {
            'yillar': sorted(list(all_years_found)),
            'tablo_verileri': all_pages_data
        }

    except Exception as e:
        print(f"PDF okuma sırasında Sanayi Sınıfı Modül'de hata: {e}")
        return None

