import cv2
import socket
import time
import detection_module as dm 

# --- AĞ AYARLARI (BURAYI KONTROL ET!) ---
# Alıcı bilgisayarın IP adresini buraya yazmalısın.
HEDEF_IP = "127.0.0.1"  
PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

face_cascade = dm.model_hazirla()
if face_cascade is None: exit()

# Kamerayı HD açıyoruz
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

print(f"--- SENDER BAŞLADI ---")
print(f"Hedef IP: {HEDEF_IP}:{PORT}")
print("Ctrl+C ile durdurabilirsin.")

frame_sayac = 0

while True:
    ret, frame = cap.read()
    if not ret: break

    # 1. Küçült (Akıcılık için 640x360)
    frame_to_send = cv2.resize(frame, (640, 360))

    # 2. İşle
    islenmis_frame = dm.isleme_yap(frame_to_send, face_cascade)

    # 3. Sıkıştır (Kalite 35)
    ret, buffer = cv2.imencode('.jpg', islenmis_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 35])
    
    if ret:
        data = buffer.tobytes()
        paket_boyutu = len(data)

        if paket_boyutu < 65500:
            sock.sendto(data, (HEDEF_IP, PORT))
            
            # --- DEBUG: Her 30 karede bir terminale bilgi yaz ---
            frame_sayac += 1
            if frame_sayac % 30 == 0:
                print(f"Yayın Aktif -> Paket Boyutu: {paket_boyutu} byte gönderildi.")
        else:
            print(f"UYARI: Paket Sınırı Aşıldı! ({paket_boyutu} byte). Gönderilemedi.")

    cv2.imshow("Drone Gorusu (Sender)", islenmis_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
sock.close()
cv2.destroyAllWindows()