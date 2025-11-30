import cv2
import socket
import numpy as np
import time

LISTEN_IP = "0.0.0.0"
PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((LISTEN_IP, PORT))
sock.setblocking(False) 

print(f"--- RECEIVER BAŞLADI (Port: {PORT}) ---")
print("Veri bekleniyor... (Eğer bu mesajda kalıyorsa Firewall'u kontrol et!)")

last_log_time = time.time()
veri_geldi_mi = False

while True:
    try:
        data = None
        # Tamponu temizle
        while True:
            try:
                packet, addr = sock.recvfrom(65536)
                data = packet
                # İlk veri geldiğinde haber ver
                if not veri_geldi_mi:
                    print(f"BAĞLANTI BAŞARILI! {addr} adresinden veri akıyor...")
                    veri_geldi_mi = True
            except BlockingIOError:
                break
        
        if data is not None:
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is not None:
                # Küçük gelen görüntüyü büyüt
                ekran_goruntusu = cv2.resize(frame, (1280, 720))
                cv2.imshow("YER ISTASYONU (Receiver)", ekran_goruntusu)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except Exception as e:
        print(f"Hata: {e}")

sock.close()
cv2.destroyAllWindows()