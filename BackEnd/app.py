from flask import Flask, request, redirect, jsonify, send_from_directory, session
import os
import sqlite3
import subprocess
from werkzeug.security import generate_password_hash, check_password_hash

from recommendation import recommend_from_dataset
from spotify_api import search_track

APP_NAME = "MoodSync"
APPDATA_DIR = os.path.join(os.environ.get("LOCALAPPDATA"), APP_NAME)
os.makedirs(APPDATA_DIR, exist_ok=True)

DB_PATH = os.path.join(APPDATA_DIR, "users.db")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")
EMOTION_FILE = os.path.join(BASE_DIR, "emotion.txt")

app = Flask(__name__, static_folder=STATIC_DIR)
app.secret_key = "moodsync_secret_key"


def get_db():
    return sqlite3.connect(DB_PATH)


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


@app.route("/")
def home():
    if "user" not in session:
        return redirect("/login")
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return send_from_directory(FRONTEND_DIR, "login.html")

    username = request.form["username"]
    password = request.form["password"]

    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username=?",
        (username,)
    ).fetchone()
    conn.close()

    if user and check_password_hash(user[2], password):
        session["user"] = username
        return redirect("/")

    return redirect("/login")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return send_from_directory(FRONTEND_DIR, "signup.html")

    username = request.form["username"]
    password = generate_password_hash(request.form["password"])

    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?,?)",
            (username, password)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return redirect("/signup")

    conn.close()
    return redirect("/login")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


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

    with open(EMOTION_FILE, "w", encoding="utf-8") as f:
        f.write(emotion)

    return recommend(emotion)


@app.route("/detect", methods=["POST"])
def camera_detect():
    try:
        subprocess.run(
            ["python", "face_emotion.py"],
            cwd=BASE_DIR,
            check=True
        )
    except Exception as e:
        print("Camera process error:", e)

    emotion = "Neutral"
    try:
        if os.path.exists(EMOTION_FILE):
            with open(EMOTION_FILE, "r", encoding="utf-8") as f:
                emotion = f.read().strip()
    except Exception as e:
        print("Emotion file read error:", e)

    return recommend(emotion)


def recommend(emotion):
    dataset_tracks = recommend_from_dataset(emotion)
    final_tracks = []

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


@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(STATIC_DIR, filename)


if __name__ == "__main__":
    app.run(debug=True)
