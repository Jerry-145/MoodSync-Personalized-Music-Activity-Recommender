🎧 MoodSync – Emotion-Based Music Recommendation System

MoodSync is an AI-powered web application that detects a user's emotion and recommends music accordingly. It uses facial emotion recognition, emoji input, and Spotify API integration to deliver personalized song suggestions.

🚀 Features
😊 Emotion Detection via Emoji
📷 Real-time Facial Emotion Detection using AI
🎵 Music Recommendation based on Mood
🔍 Song Search Functionality
🔥 Popular Songs Section
📜 Listening History Tracking
📊 User Analytics Dashboard
🔐 User Authentication (Login/Signup)
🧠 How It Works
User selects mood via emoji OR uses camera
Emotion is detected using ML model
Songs are filtered from dataset based on emotion
Spotify API fetches playable links
Results are shown in UI
History and analytics stored using SQLite
🛠 Tech Stack
🔹 Backend
Python
Flask
SQLite (Database)
🔹 Frontend
HTML, CSS, JavaScript
Responsive UI
🔹 Machine Learning
OpenCV
Keras (Emotion Model)
Haar Cascade (Face Detection)
🔹 APIs
Spotify Web API
📁 Project Structure
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
⚙️ Installation & Setup
1️⃣ Clone the Repository
git clone https://github.com/your-username/moodsync.git
cd moodsync
2️⃣ Install Dependencies
pip install flask pandas opencv-python keras requests
3️⃣ Set Environment Variables (IMPORTANT)
export SPOTIFY_CLIENT_ID=your_client_id
export SPOTIFY_CLIENT_SECRET=your_client_secret

(Windows users use set instead of export)

4️⃣ Run the Application
python app.py
5️⃣ Open in Browser
http://127.0.0.1:5000
📸 Screens (Your UI)
Home Page (Mood Selection + Search)
Login / Signup
History Page
Analytics Dashboard
📊 Database Schema
Users Table
id
username
password
History Table
username
emotion
song_name
artist
timestamp
🎯 Emotion Logic
Emotion	Filter Logic
Happy	High valence & energy
Sad	Low valence & energy
Angry	Low valence & high energy
Love	High valence & medium energy
⚠️ Important Notes
Requires webcam for emotion detection
Spotify API may not return preview for all songs
Emotion model file must be present in /models
🔮 Future Improvements
🎨 Better UI/UX (animations, dark mode)
📱 Mobile responsiveness
🤖 Better ML model accuracy
💾 Cloud database (Firebase / MongoDB)
🎧 Full Spotify playback integration
📈 Advanced analytics (charts)
👨‍💻 Author

Abhee B Vasava

⭐ If You Like This Project

Give it a ⭐ on GitHub and share it!
