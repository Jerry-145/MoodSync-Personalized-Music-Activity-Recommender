import cv2
import numpy as np
from keras.models import load_model
import time

face_cascade = cv2.CascadeClassifier(
    "models/haarcascade_frontalface_default.xml"
)

emotion_model = load_model(
    "models/emotion_model.hdf5",
    compile=False
)

emotion_labels = [
    'Angry', 'Disgust', 'Fear',
    'Happy', 'Sad', 'Surprise', 'Neutral'
]

ip_webcam_url = "http://10.80.133.9:8080/video"
cap = cv2.VideoCapture(ip_webcam_url)

print("📷 Looking for face...")

detected_emotion = None
result_frame = None

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Could not read frame")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) > 0:
        (x, y, w, h) = faces[0]

        face = gray[y:y + h, x:x + w]
        if face.size == 0:
            continue

        face = cv2.resize(face, (64, 64))
        face = face / 255.0
        face = face.reshape(1, 64, 64, 1)

        prediction = emotion_model.predict(face, verbose=0)
        detected_emotion = emotion_labels[np.argmax(prediction)]

        try:
            with open("emotion.txt", "w", encoding="utf-8") as f:
                f.write(detected_emotion)
        except OSError as e:
            print("❌ File write error:", e)

        # Prepare final display frame
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(
            frame,
            f"Detected Emotion: {detected_emotion}",
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0),
            2
        )

        result_frame = frame.copy()
        break

    cv2.imshow("Detecting Emotion...", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

if detected_emotion and result_frame is not None:
    print(f"✅ Emotion Detected: {detected_emotion}")
    cv2.imshow("Final Emotion Result", result_frame)
    cv2.waitKey(3000)
    cv2.destroyAllWindows()
else:
    print("⚠ No face detected")