# 🎧 MoodSync – Emotion-Based Music Recommendation System

> *Your mood, your music — powered by AI* 🎶

---

## 🚀 Overview

**MoodSync** is an AI-powered web application that detects a user's emotion and recommends music accordingly. It combines **facial emotion recognition**, **emoji-based input**, and **Spotify API integration** to deliver a personalized music experience.

---

## ✨ Features

- 😊 **Emotion Detection via Emoji**
- 📷 **Real-time Facial Emotion Detection (AI)**
- 🎵 **Mood-Based Music Recommendation**
- 🔍 **Search Songs & Artists**
- 🔥 **Popular Songs Section**
- 📜 **Listening History Tracking**
- 📊 **User Analytics Dashboard**
- 🔐 **User Authentication (Login & Signup)**

---

## 🧠 How It Works

```
1. User selects mood (emoji) OR uses camera
2. Emotion is detected using ML model
3. Dataset filters songs based on emotion
4. Spotify API fetches preview + links
5. Songs are displayed in UI
6. User activity is stored for history & analytics
```

---

## 🛠 Tech Stack

### 🔹 Backend
- Python 🐍
- Flask 🌐
- SQLite 🗄️

### 🔹 Frontend
- HTML, CSS, JavaScript 🎨

### 🔹 Machine Learning
- OpenCV 📷
- Keras 🤖
- Haar Cascade (Face Detection)

### 🔹 APIs
- Spotify Web API 🎧

---

## 📁 Project Structure

```
MoodSync/
│
├── backend/
│   ├── app.py
│   ├── face_emotion.py
│   ├── recommendation.py
│   ├── spotify_api.py
│   ├── emotion.txt
│   └── data/
│       └── dataset.csv
│
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── history.html
│   ├── analytics.html
│   └── static/
│       ├── style.css
│       ├── auth.css
│       └── script.js
│
└── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/moodsync.git
cd moodsync
```

---

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3️⃣ Set Environment Variables

```bash
export SPOTIFY_CLIENT_ID=your_client_id
export SPOTIFY_CLIENT_SECRET=your_client_secret
```

👉 For Windows:
```bash
set SPOTIFY_CLIENT_ID=your_client_id
set SPOTIFY_CLIENT_SECRET=your_client_secret
```

---

### 4️⃣ Run the Application

```bash
python app.py
```

---

### 5️⃣ Open in Browser

```
http://127.0.0.1:5000
```

---

## 📊 Database Schema

### 👤 Users Table
- `id`
- `username`
- `password`

### 🎵 History Table
- `username`
- `emotion`
- `song_name`
- `artist`
- `timestamp`

---

## 🎯 Emotion Logic

| Emotion | Filter Logic |
|--------|-------------|
| 😊 Happy | High valence & energy |
| 😢 Sad | Low valence & energy |
| 😡 Angry | Low valence & high energy |
| ❤️ Love | High valence & medium energy |

---

## ⚠️ Important Notes

- 📷 Webcam required for emotion detection  
- 🎧 Spotify may not provide preview for all songs  
- 🤖 ML model must be placed inside `/models` folder  

---

## 🔮 Future Improvements

- 🎨 Modern UI with animations  
- 📱 Mobile responsiveness  
- 🤖 Improved ML model accuracy  
- ☁️ Cloud database (Firebase / MongoDB)  
- 🎧 Full Spotify playback integration  
- 📈 Advanced analytics  

---

## 👨‍💻 Author

**Abhee B Vasava**

---

## ⭐ Support

If you like this project:

- ⭐ Star the repo  
- 🔁 Share it  
- 💡 Contribute ideas  
