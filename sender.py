# DOSYA ADI: sender.py
import cv2
import socket
import detection_module as dm  # Yazdığımız modülü buraya çağırıyoruz

# --- AYARLAR ---
# Test için "127.0.0.1" (Kendi PC'n)
# Sahada Yer İstasyonu IP'si olacak (Örn: 192.168.1.20)
HEDEF_IP = "127.0.0.1" 
PORT = 9999

# Soket Kurulumu
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 1. Modülü ve Modeli Yükle
face_cascade = dm.model_hazirla()
if face_cascade is None:
    print("Program durduruluyor...")
    exit()

# 2. Kamerayı Aç
# NOT: SIYI Kamera gelince buraya 'rtsp://...' yazacaksın.
cap = cv2.VideoCapture(0) 

print(f"Drone Yayını Başladı -> Hedef: {HEDEF_IP}:{PORT}")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Kamera okunamadı!")
        break

    # --- MODÜLER KISIM ---
    # Görüntüyü modüle veriyoruz, o bize çizip geri veriyor
    islenmis_frame = dm.isleme_yap(frame, face_cascade)

    # --- GÖNDERME KISMI ---
    # JPEG Sıkıştırma (%50 Kalite)
    ret, buffer = cv2.imencode('.jpg', islenmis_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 50])

    if ret:
        data = buffer.tobytes()
        
        # Paket boyutu kontrolü (UDP için max 65500)
        if len(data) < 65500:
            sock.sendto(data, (HEDEF_IP, PORT))
        else:
            print(f"Uyarı: Kare boyutu çok büyük ({len(data)} byte), atlandı.")

    # Gönderici ekranda da görmek istersen (Test amaçlı)
    cv2.imshow("Drone - Gonderici Ekrani", islenmis_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
sock.close()
cv2.destroyAllWindows()