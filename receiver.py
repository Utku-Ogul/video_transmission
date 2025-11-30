# DOSYA ADI: receiver.py
import cv2
import socket
import numpy as np

# --- AYARLAR ---
LISTEN_IP = "0.0.0.0" # Tüm ağları dinle
PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((LISTEN_IP, PORT))

print(f"Yer İstasyonu Hazır. Port {PORT} dinleniyor...")
print("Pencere açılması için Drone'dan veri bekleniyor...")

while True:
    try:
        # 1. Veriyi Yakala (Max 65536 byte)
        data, addr = sock.recvfrom(65536)
        
        # 2. Byte verisini resme çevir
        nparr = np.frombuffer(data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # 3. Ekrana Bas
        if frame is not None:
            cv2.imshow("CANLI YAYIN - YER ISTASYONU", frame)
            
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except Exception as e:
        print(f"Hata: {e}")
        pass

sock.close()
cv2.destroyAllWindows()