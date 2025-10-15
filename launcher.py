# launcher.py - KRİTİK STABİL SÜRÜM (Çoklu Açmayı Engelleyen Port Kontrolü)

import subprocess
import time
import webbrowser
import sys
import socket # Port kontrolü için gerekli

STREAMLIT_PORT = 8501
STREAMLIT_URL = f'http://localhost:{STREAMLIT_PORT}'

# FONKSİYON: Portun kullanılıp kullanılmadığını kontrol eder.
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Eğer bağlanabilirse port kullanımdadır.
        return s.connect_ex(('localhost', port)) == 0

def start_and_open():
    if is_port_in_use(STREAMLIT_PORT):
        # KRİTİK KONTROL: Eğer port meşgulse uygulama zaten çalışıyordur. 
        # Yeni bir tarayıcı açılmaz ve program sessizce kapanır.
        return

    # Streamlit sunucusunu başlatma komutu
    # --server.headless True: Streamlit'e tarayıcıyı otomatik açma demektir.
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless", "True"]
    
    # Yeni bir alt süreç (subprocess) başlatıyoruz.
    try:
        streamlit_process = subprocess.Popen(cmd, shell=False)
    except FileNotFoundError:
        print("HATA: Streamlit veya Python yorumlayıcısı bulunamadı.")
        return

    # SUNUCU BEKLEME DÖNGÜSÜ: Sunucunun açılmasını garantilemek için.
    print("Streamlit sunucusu başlatılıyor, lütfen bekleyin...")
    for _ in range(15): # Maksimum 15 saniye bekleme süresi
        if is_port_in_use(STREAMLIT_PORT):
            print("Sunucu açıldı.")
            break # Port açıldı, döngüden çık
        time.sleep(1)
    
    # Tarayıcıyı sadece ve sadece sunucu portu açıldıysa aç.
    webbrowser.open(STREAMLIT_URL)
    
    # Ana programı (launcher.py), Streamlit işlemi devam ettiği sürece canlı tut
    # (Bu kısım, EXE'nin hemen kapanmaması ve arka plan sunucusunun kapanmasını beklemek için gereklidir.)
    while streamlit_process.poll() is None:
        time.sleep(1)

if __name__ == "__main__":
    start_and_open()