import cv2
import socket
import time
import os

# --- AYARLAR ---
# Aynı bilgisayarda test için 127.0.0.1
# Farklı PC'ye atıyorsan onun IP'sini yaz (örn: 192.168.1.35)
HEDEF_IP = "127.0.0.1" 
PORT = 9999
VIDEO_DOSYASI = "test.mp4"

# --- 720p AYARLARI ---
HEDEF_GENISLIK = 1280
HEDEF_YUKSEKLIK = 720
KALITE = 25 

# Dosya kontrolü
if not os.path.exists(VIDEO_DOSYASI):
    print(f"HATA: '{VIDEO_DOSYASI}' bulunamadı! Videoyu klasöre koydun mu?")
    exit()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cap = cv2.VideoCapture(VIDEO_DOSYASI)

# FPS öğrenme
video_fps = cap.get(cv2.CAP_PROP_FPS)
if video_fps == 0: video_fps = 30
frame_suresi = 1.0 / video_fps

print(f"--- CANLI YAYIN SİMÜLASYONU (Penceresiz Mod) ---")
print(f"Dosya: {VIDEO_DOSYASI} | Hız: {int(video_fps)} FPS")
print(f"Hedef: {HEDEF_IP}:{PORT}")
print("Durdurmak için terminalde 'Ctrl + C' yapabilirsin.")

try:
    while True:
        baslangic = time.time()
        
        ret, frame = cap.read()
        
        # Video bittiyse başa sar
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # 1. BOYUTLANDIRMA
        frame_resized = cv2.resize(frame, (HEDEF_GENISLIK, HEDEF_YUKSEKLIK))

        # 2. SIKIŞTIRMA VE GÖNDERME
        ret, buffer = cv2.imencode('.jpg', frame_resized, [int(cv2.IMWRITE_JPEG_QUALITY), KALITE])
        
        if ret:
            data = buffer.tobytes()
            if len(data) < 65500:
                sock.sendto(data, (HEDEF_IP, PORT))
            # Hata vermesin diye uyarıyı da kapattım, sadece gönderiyor.

        # --- DEĞİŞİKLİK BURADA ---
        # cv2.imshow ve cv2.waitKey kodlarını sildik.
        # Bu sayede Linux/Snap hatası vermeyecek.
        
        # 3. SENKRONİZASYON (Video hızı ayarı)
        gecen_sure = time.time() - baslangic
        bekleme = frame_suresi - gecen_sure
        
        if bekleme > 0:
            time.sleep(bekleme)

except KeyboardInterrupt:
    print("\nYayın durduruldu.")

cap.release()
sock.close()
# cv2.destroyAllWindows() gerek kalmadı çünkü pencere açmadık.