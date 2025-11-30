# DOSYA ADI: detection_module.py
import cv2
import os

def model_hazirla():
    """Haar Cascade modelini bulur ve yükler."""
    # Senin kodundaki Ubuntu dosya yolu mantığı
    if hasattr(cv2, "data"):
        haar_dir = cv2.data.haarcascades
    else:
        haar_dir = "/usr/share/opencv4/haarcascades/"

    cascade_path = os.path.join(haar_dir, "haarcascade_frontalface_default.xml")
    print("Model Yolu:", cascade_path)

    face_cascade = cv2.CascadeClassifier(cascade_path)
    
    if face_cascade.empty():
        print("HATA: Model yüklenemedi! Dosya yolunu kontrol et.")
        return None
        
    return face_cascade

def isleme_yap(frame, face_cascade):
    """Görüntüyü alır, insan varsa çizer ve geri döndürür."""
    
    # Gri tonlamaya çevir
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Senin belirlediğin parametrelerle tespit
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60)
    )

    human_detected = len(faces) > 0

    # Kareleri çiz
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Yazı ve Renk Ayarı
    if human_detected:
        status_text = "INSAN VAR"
        color = (0, 255, 0) # Yeşil
    else:
        status_text = "INSAN YOK"
        color = (0, 0, 255) # Kırmızı

    # Ekrana Yazı Yaz
    cv2.putText(
        frame,
        status_text,
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        color,
        2,
        cv2.LINE_AA
    )
    
    return frame