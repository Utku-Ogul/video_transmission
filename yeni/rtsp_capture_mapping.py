import cv2
import os
import time
import argparse
import threading
from datetime import datetime

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

class LatestFrameGrabber:
    def __init__(self, url):
        self.url = url
        self.cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        # Bazı sistemlerde işe yarar:
        try:
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        except Exception:
            pass

        self.lock = threading.Lock()
        self.frame = None
        self.ok = False
        self.ts = 0.0
        self.stop_flag = False

    def start(self):
        self.t = threading.Thread(target=self._loop, daemon=True)
        self.t.start()

    def _loop(self):
        while not self.stop_flag:
            ok, fr = self.cap.read()
            now = time.time()
            with self.lock:
                self.ok = ok
                if ok and fr is not None:
                    self.frame = fr
                    self.ts = now
            if not ok:
                time.sleep(0.05)

    def get_latest(self):
        with self.lock:
            return self.ok, (None if self.frame is None else self.frame.copy()), self.ts

    def stop(self):
        self.stop_flag = True
        try:
            self.t.join(timeout=1.0)
        except Exception:
            pass
        self.cap.release()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True, help="RTSP URL (e.g. rtsp://192.168.144.25:8554/main.264)")
    ap.add_argument("--fps", type=float, default=2.0, help="Kaydedilecek foto/saniye (örn 1,2,5)")
    ap.add_argument("--out", default="mapping_frames", help="Çıktı klasörü")

    ap.add_argument("--format", choices=["png", "jpg"], default="png", help="Kayıt formatı")
    ap.add_argument("--png_compression", type=int, default=3, help="PNG sıkıştırma 0-9 (0 hızlı/büyük, 9 yavaş/küçük)")
    ap.add_argument("--jpeg_quality", type=int, default=90, help="JPG kalite 0-100")

    ap.add_argument("--resize", default="", help="Örn: 1280x720 (boş = orijinal)")
    ap.add_argument("--max", type=int, default=0, help="0=sonsuz, yoksa max foto sayısı")
    args = ap.parse_args()

    if not (0 <= args.png_compression <= 9):
        raise SystemExit("--png_compression 0-9 arası olmalı")
    if not (0 <= args.jpeg_quality <= 100):
        raise SystemExit("--jpeg_quality 0-100 arası olmalı")

    ensure_dir(args.out)
    meta_path = os.path.join(args.out, "frames.csv")

    resize_w = resize_h = None
    if args.resize:
        try:
            resize_w, resize_h = map(int, args.resize.lower().split("x"))
        except Exception:
            raise SystemExit("--resize formatı 1280x720 gibi olmalı")

    grabber = LatestFrameGrabber(args.url)
    grabber.start()

    period = 1.0 / max(args.fps, 0.001)
    next_t = time.monotonic()
    count = 0

    with open(meta_path, "w", encoding="utf-8") as f:
        f.write("index,filename,unix_ts,iso_ts\n")

        print(f"[INFO] Saving at {args.fps} fps -> every {period:.3f}s")
        print(f"[INFO] Format: {args.format}")
        print(f"[INFO] Output: {os.path.abspath(args.out)}")

        try:
            while True:
                now = time.monotonic()
                if now < next_t:
                    time.sleep(min(0.01, next_t - now))
                    continue
                next_t += period

                ok, frame, ts = grabber.get_latest()
                if not ok or frame is None:
                    continue

                if resize_w and resize_h:
                    frame = cv2.resize(frame, (resize_w, resize_h), interpolation=cv2.INTER_AREA)

                iso = datetime.fromtimestamp(ts).strftime("%Y%m%d_%H%M%S_%f")
                ext = args.format
                filename = f"frame_{count:06d}_{iso}.{ext}"
                path = os.path.join(args.out, filename)

                if args.format == "png":
                    cv2.imwrite(path, frame, [int(cv2.IMWRITE_PNG_COMPRESSION), int(args.png_compression)])
                else:
                    cv2.imwrite(path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), int(args.jpeg_quality)])

                f.write(f"{count},{filename},{ts:.6f},{iso}\n")
                f.flush()

                count += 1
                if args.max > 0 and count >= args.max:
                    break

        except KeyboardInterrupt:
            pass
        finally:
            grabber.stop()

    print(f"[DONE] Saved {count} images. Metadata: {meta_path}")

if __name__ == "__main__":
    main()