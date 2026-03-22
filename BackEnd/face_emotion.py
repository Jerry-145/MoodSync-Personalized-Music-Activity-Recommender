import cv2
import numpy as np
from keras.models import load_model
import time
import os

# =========================
# PATH SETUP
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMOTION_FILE = os.path.join(BASE_DIR, "emotion.txt")

# =========================
# LOAD MODELS
# =========================
face_cascade = cv2.CascadeClassifier(
    os.path.join(BASE_DIR, "models", "haarcascade_frontalface_default.xml")
)

emotion_model = load_model(
    os.path.join(BASE_DIR, "models", "emotion_model.hdf5"),
    compile=False
)

# =========================
# USE LAPTOP WEBCAM
# =========================
cap = cv2.VideoCapture(0)

print("📷 Looking for face...")

detected_emotion = "Happy"  # fallback
result_frame = None

start_time = time.time()

# =========================
# MAIN LOOP
# =========================
while True:

    ret, frame = cap.read()
    if not ret:
        print("❌ Could not read frame")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) > 0:

        (x, y, w, h) = faces[0]

        face = gray[y:y+h, x:x+w]

        if face.size == 0:
            continue

        # Preprocess
        face = cv2.resize(face, (64, 64))
        face = face / 255.0
        face = face.reshape(1, 64, 64, 1)

        # Predict
        prediction = emotion_model.predict(face, verbose=0)[0]

        print("Prediction:", prediction)

        # Extract important probabilities
        angry = prediction[0]
        happy = prediction[3]
        sad = prediction[4]
        surprise = prediction[5]

        # =========================
        # SMART EMOTION LOGIC
        # =========================
        if sad > 0.20:
            detected_emotion = "Sad"

        elif angry > 0.20:
            detected_emotion = "Angry"

        elif surprise > 0.25:
            detected_emotion = "Love"

        elif happy > 0.20:
            detected_emotion = "Happy"

        else:
            detected_emotion = "Happy"

        print("🎯 Detected Emotion:", detected_emotion)

        # Draw box
        cv2.rectangle(frame, (x,y), (x+w,y+h), (0,255,0), 2)

        cv2.putText(
            frame,
            f"Emotion: {detected_emotion}",
            (x, y-10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0,255,0),
            2
        )

        result_frame = frame.copy()
        break

    cv2.imshow("Detecting Emotion...", frame)

    # Timeout protection
    if time.time() - start_time > 10:
        print("⚠ Timeout: No face detected")
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# =========================
# CLEANUP
# =========================
cap.release()
cv2.destroyAllWindows()

# =========================
# WRITE EMOTION SAFELY (AFTER LOOP)
# =========================
try:
    if os.path.exists(EMOTION_FILE):
        os.remove(EMOTION_FILE)

    f = open(EMOTION_FILE, "w", encoding="utf-8")
    f.write(detected_emotion)
    f.flush()
    os.fsync(f.fileno())
    f.close()

    print("✅ Emotion written to file:", detected_emotion)
    print("📁 File path:", EMOTION_FILE)

except Exception as e:
    print("❌ File write error:", e)

# =========================
# FINAL RESULT DISPLAY
# =========================
if result_frame is not None:

    print(f"✅ Final Emotion: {detected_emotion}")

    cv2.imshow("Final Emotion Result", result_frame)
    cv2.waitKey(3000)
    cv2.destroyAllWindows()

else:
    print("⚠ No face detected")