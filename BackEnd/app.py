from flask import Flask, request, redirect, jsonify, send_from_directory, session
import os
import sqlite3
import subprocess
from werkzeug.security import generate_password_hash, check_password_hash

from recommendation import recommend_from_dataset
from spotify_api import search_track

# =========================
# PATH CONFIGURATION
# =========================
APP_NAME = "MoodSync"
APPDATA_DIR = os.path.join(os.environ.get("LOCALAPPDATA"), APP_NAME)
os.makedirs(APPDATA_DIR, exist_ok=True)

DB_PATH = os.path.join(APPDATA_DIR, "users.db")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")
EMOTION_FILE = os.path.join(BASE_DIR, "emotion.txt")

# =========================
# FLASK APP
# =========================
app = Flask(__name__, static_folder=STATIC_DIR)
app.secret_key = "moodsync_secret_key"

# =========================
# DATABASE FUNCTIONS
# =========================
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return send_from_directory(FRONTEND_DIR, "index.html")

# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return send_from_directory(FRONTEND_DIR, "login.html")

    username = request.form["username"]
    password = request.form["password"]

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    conn.close()

    if user and check_password_hash(user["password"], password):
        session["user"] = user["username"]
        return redirect("/")

    return redirect("/login")

# ---------- SIGNUP ----------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return send_from_directory(FRONTEND_DIR, "signup.html")

    username = request.form["username"]
    password = generate_password_hash(request.form["password"])

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return redirect("/signup")

    conn.close()
    return redirect("/login")

# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------- EMOJI DETECTION ----------
@app.route("/emoji", methods=["POST"])
def emoji_detect():
    emoji = request.json.get("emoji")

    emoji_map = {
        "😊": "Happy",
        "😢": "Sad",
        "😡": "Angry",
        "❤️": "Love"
    }

    emotion = emoji_map.get(emoji, "Neutral")

    try:
        with open(EMOTION_FILE, "w", encoding="utf-8") as f:
            f.write(emotion)
    except Exception as e:
        print("Emotion file write error:", e)

    return recommend(emotion)

# ---------- CAMERA DETECTION ----------
@app.route("/detect", methods=["POST"])
def camera_detect():
    emotion = "Neutral"

    try:
        subprocess.run(
            ["python", "face_emotion.py"],
            cwd=BASE_DIR,
            timeout=20
        )
    except Exception as e:
        print("Camera process error:", e)

    try:
        if os.path.exists(EMOTION_FILE):
            with open(EMOTION_FILE, "r", encoding="utf-8") as f:
                emotion = f.read().strip()
    except Exception as e:
        print("Emotion file read error:", e)

    return recommend(emotion)

# ---------- RECOMMENDATION ----------
def recommend(emotion):
    final_tracks = []

    try:
        dataset_tracks = recommend_from_dataset(emotion)
    except Exception as e:
        print("Dataset error:", e)
        dataset_tracks = []

    for t in dataset_tracks:
        api_data = search_track(t["track_name"], t["artist"])

        if api_data:
            final_tracks.append(api_data)
        else:
            final_tracks.append({
                "name": t["track_name"],
                "artist": t["artist"],
                "preview_url": None,
                "spotify_url": None
            })

    return jsonify({
        "emotion": emotion,
        "tracks": final_tracks
    })

# ---------- STATIC FILES ----------
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(STATIC_DIR, filename)

# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    app.run(debug=True)
