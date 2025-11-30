import cv2
import socket
import numpy as np

# --- AYARLAR ---
LISTEN_IP = "0.0.0.0" # Her yerden dinle
PORT = 9999

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((LISTEN_IP, PORT))
# Donmayı engellemek için soketi bloklanmayan moda alıyoruz
sock.setblocking(False)

print(f"--- RECEIVER BAŞLADI (Port: {PORT}) ---")
print("Görüntü bekleniyor...")

while True:
    try:
        data = None
        
        # --- BUFFER TEMİZLEME (Gecikme Önleyici) ---
        # Ağdaki tüm paketleri çek, sadece EN SONUNCUYU al.
        while True:
            try:
                packet, addr = sock.recvfrom(65536)
                data = packet
            except BlockingIOError:
                break
        
        # Eğer yeni veri varsa işle
        if data is not None:
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is not None:
                cv2.imshow("Receiver (Canli Izleme)", frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except Exception as e:
        pass

sock.close()
cv2.destroyAllWindows()