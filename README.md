# MoodSync-Personalized-Music-Activity-Recommender
MoodSync is a web-based application that recommends personalized music and activities based on the user’s mood. Using Spotify audio features like energy and valence, it suggests suitable songs and activities to improve emotional well-being and user experience.

# 🎧 Emotion-Based Music Recommendation System

An AI-powered web application that detects a user’s emotion using facial expressions or emoji selection and recommends music based on the detected mood.

---

## 🚀 Features

- Real-time face detection using OpenCV
- Emotion recognition using a deep learning model
- Emoji-based emotion selection with interactive UI
- Spotify-inspired music recommendation interface
- Clean and user-friendly frontend
- Modular backend and frontend structure

---

## 🧠 How It Works

1. User selects an emoji or clicks the camera button
2. Camera captures facial expression (IP Webcam or local webcam)
3. Emotion is detected using a trained CNN model
4. Detected emotion is stored
5. Music recommendations are shown based on emotion

---

## 🛠️ Technologies Used

### Backend
- Python
- OpenCV
- TensorFlow / Keras
- NumPy

### Frontend
- HTML
- Static 
- -CSS
- -JavaScript

---

## 📂 Project Structure

Backend/
├── face_emotion.py
├── emotion.txt
├── haarcascade_frontalface_default.xml
└── models/
└── emotion_model.hdf5

Frontend/
├── index.html
└── static/
├── style.css
└── script.js
