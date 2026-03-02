import os
import cv2
import json
import time
import threading
import numpy as np
from dotenv import load_dotenv
from deepface import DeepFace
from mysql_db import get_db, attendance_log

load_dotenv()

rtsp_in_url=os.getenv("RTSP_IN")
rtsp_out_url=os.getenv("RTSP_OUT")

# ---------------- CONFIG ----------------
DETECTOR = "opencv"
MODEL = "ArcFace"
THRESHOLD = 0.5
ABSENCE_TIMEOUT = 60
present = {}  # KEY: LAST_SEEN_TIME

print("Script started", flush=True)

# ---------------- LOAD EMPLOYEES ----------------
conn = get_db()
cursor = conn.cursor()
cursor.execute("SELECT id, name, embedding FROM employees")
rows = cursor.fetchall()
cursor.close()
conn.close()

known_embeddings = []
known_ids = []
known_names = []

# CONVERT EMBEDDINGS TO NUMPY + NORMALIZE
for emp_id, name, emb_json in rows:
    emb = np.array(json.loads(emb_json), dtype=np.float32)
    emb = emb / np.linalg.norm(emb)
    known_embeddings.append(emb)
    known_ids.append(emp_id)
    known_names.append(name)

known_embeddings = np.array(known_embeddings)

# ---------------- CAMERA CLASS ----------------
class RTSPStream:
    def __init__(self, url, camera_name, direction):
        self.url = url
        self.camera_name = camera_name
        self.direction = direction
        self.cap = cv2.VideoCapture(url)
        self.frame = None
        self.stopped = False

    def start(self):
        threading.Thread(target=self.update, daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True
        self.cap.release()

# CONVERT WEBCAM INDEX FROM STRING TO INT
if rtsp_in_url and rtsp_in_url.isdigit():
    rtsp_in_url = int(rtsp_in_url)

# ---------------- START CAMERAS ----------------
rtsp_in = RTSPStream(rtsp_in_url, camera_name="In Camera", direction="IN").start()
rtsp_out = RTSPStream(rtsp_out_url, camera_name="Out Camera", direction="OUT").start()

print("Starting cameras...", flush=True)
time.sleep(2)

if rtsp_in.read() is None:
    print("IN camera not working", flush=True)

if rtsp_out.read() is None:
    print("OUT camera not working", flush=True)


# ---------------- MAIN LOOP ----------------
while True:
    for rtsp_obj in [rtsp_in, rtsp_out]:
        frame = rtsp_obj.read()
        if frame is None:
            continue

        display_frame = frame.copy()

        try:
            results = DeepFace.represent(
                img_path=frame,
                model_name=MODEL,
                detector_backend=DETECTOR,
                enforce_detection=False
            )

            for res in results:
                x = res["facial_area"]["x"]
                y = res["facial_area"]["y"]
                w = res["facial_area"]["w"]
                h = res["facial_area"]["h"]

                curr_emb = np.array(res["embedding"], dtype=np.float32)
                curr_emb = curr_emb / np.linalg.norm(curr_emb)

                if len(known_embeddings) > 0:
                    similarities = np.dot(known_embeddings, curr_emb)
                    best_idx = int(np.argmax(similarities))
                    max_sim = float(similarities[best_idx])

                    if max_sim > THRESHOLD:
                        emp_id = known_ids[best_idx]
                        name = known_names[best_idx]

                        key = (emp_id, rtsp_obj.direction)
                        now = time.time()

                        # LOG ONCE WHEN THEY APPEAR
                        if key not in present:
                            attendance_log(emp_id, rtsp_obj.camera_name, rtsp_obj.direction)

                        # UPDATE LAST SEEN
                        present[key] = now

                        color = (0, 255, 0)
                        label = f"{name} {max_sim:.2f}"
                    else:
                        color = (0, 0, 255)
                        label = "Unknown"
                else:
                    color = (255, 255, 255)
                    label = "No DB Records"

                cv2.rectangle(display_frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(display_frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        except Exception as e:
            print("Error:", e, flush=True)

        cv2.imshow(rtsp_obj.camera_name, display_frame)

    # CLEANUP: REMOVE PEOPLE WHO HAVEN'T BEEN SEEN RECENTLY
    now = time.time()
    to_remove = [k for k, last_seen in present.items() if now - last_seen > ABSENCE_TIMEOUT]
    for k in to_remove:
        del present[k]

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

rtsp_in.stop()
rtsp_out.stop()
cv2.destroyAllWindows()