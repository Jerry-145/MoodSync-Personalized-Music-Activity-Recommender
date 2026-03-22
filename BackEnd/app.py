from flask import Flask, request, redirect, jsonify, send_from_directory, session
import os
import sqlite3
import subprocess
import urllib.parse

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
# DATABASE
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

    conn.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            emotion TEXT NOT NULL,
            song_name TEXT NOT NULL,
            artist TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
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

# ---------- ANALYTICS ----------
@app.route("/analytics_page")
def analytics_page():
    if "user" not in session:
        return redirect("/login")
    return send_from_directory(FRONTEND_DIR, "analytics.html")

# ---------- HISTORY ----------
@app.route("/history_page")
def history_page():
    if "user" not in session:
        return redirect("/login")
    return send_from_directory(FRONTEND_DIR, "history.html")
# ---------- EMOJI ----------
@app.route("/emoji", methods=["POST"])
def emoji_detect():
    emoji = request.json.get("emoji")

    emoji_map = {
        "😊": "Happy",
        "😢": "Sad",
        "😡": "Angry",
        "❤️": "Happy"
    }

    emotion = emoji_map.get(emoji, "Happy")

    with open(EMOTION_FILE, "w", encoding="utf-8") as f:
        f.write(emotion)

    return recommend(emotion)

# ---------- CAMERA ----------
@app.route("/detect", methods=["POST"])
def camera_detect():

    subprocess.run(["python", "face_emotion.py"], cwd=BASE_DIR)

    emotion = "Happy"

    if os.path.exists(EMOTION_FILE):
        with open(EMOTION_FILE, "r", encoding="utf-8") as f:
            file_emotion = f.read().strip()
            if file_emotion:
                emotion = file_emotion

    print("🚀 Final Emotion:", emotion)

    return recommend(emotion)

# ---------- RECOMMEND ----------
def recommend(emotion):

    dataset_tracks = recommend_from_dataset(emotion)
    final_tracks = []

    for t in dataset_tracks:

        api_data = search_track(t["track_name"], t["artist"])

        final_tracks.append({
            "name": t["track_name"],
            "artist": t["artist"],
            "preview_url": api_data["preview_url"] if api_data else None,
            "spotify_url": api_data["spotify_url"] if api_data else
                f"https://open.spotify.com/search/{urllib.parse.quote(t['track_name'] + ' ' + t['artist'])}"
        })

    return jsonify({
        "emotion": emotion,
        "tracks": final_tracks
    })

# ---------- SEARCH ----------
@app.route("/search")
def search():

    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])

    result = search_track(query, "")

    if result:
        return jsonify([result])

    # fallback
    return jsonify([{
        "name": query,
        "artist": "",
        "preview_url": None,
        "spotify_url": f"https://open.spotify.com/search/{urllib.parse.quote(query)}"
    }])

# ---------- POPULAR ----------
@app.route("/popular")
def popular():

    popular_tracks = [
        {"name": "Blinding Lights", "artist": "The Weeknd"},
        {"name": "Shape of You", "artist": "Ed Sheeran"},
        {"name": "Levitating", "artist": "Dua Lipa"},
        {"name": "Stay", "artist": "The Kid LAROI"},
        {"name": "Perfect", "artist": "Ed Sheeran"}
    ]

    final_tracks = []

    for track in popular_tracks:

        api_data = search_track(track["name"], track["artist"])

        final_tracks.append({
            "name": track["name"],
            "artist": track["artist"],
            "preview_url": api_data["preview_url"] if api_data else None,
            "spotify_url": api_data["spotify_url"] if api_data else
                f"https://open.spotify.com/search/{urllib.parse.quote(track['name'] + ' ' + track['artist'])}"
        })

    return jsonify(final_tracks)

# ---------- SAVE HISTORY ----------
@app.route("/save_history", methods=["POST"])
def save_history():

    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json

    song_name = data.get("song_name")
    artist = data.get("artist")
    emotion = data.get("emotion")

    conn = get_db()

    conn.execute("""
        INSERT INTO history (username, emotion, song_name, artist)
        VALUES (?, ?, ?, ?)
    """, (session["user"], emotion, song_name, artist))

    conn.commit()

    count = conn.execute("SELECT COUNT(*) FROM history").fetchone()[0]
    print("📊 Total history rows:", count)

    conn.close()

    return jsonify({"status": "saved"})

# ---------- STATIC ----------
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(STATIC_DIR, filename)

# ---------- ANALYTICS ----------
@app.route("/analytics")
def analytics():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    conn = get_db()

    total_plays = conn.execute("""
        SELECT COUNT(*) as count
        FROM history
        WHERE username = ?
    """, (session["user"],)).fetchone()["count"]

    most_emotion = conn.execute("""
        SELECT emotion, COUNT(*) as count
        FROM history
        WHERE username = ?
        GROUP BY emotion
        ORDER BY count DESC
        LIMIT 1
    """, (session["user"],)).fetchone()

    most_song = conn.execute("""
        SELECT song_name, artist, COUNT(*) as count
        FROM history
        WHERE username = ?
        GROUP BY song_name, artist
        ORDER BY count DESC
        LIMIT 1
    """, (session["user"],)).fetchone()

    conn.close()

    return jsonify({
        "total_plays": total_plays,
        "most_emotion": dict(most_emotion) if most_emotion else None,
        "most_song": dict(most_song) if most_song else None
    })

# ---------- HISTORY ----------
@app.route("/history")
def history():
    if "user" not in session:
        return jsonify([])

    conn = get_db()

    rows = conn.execute("""
        SELECT song_name, artist, emotion, timestamp
        FROM history
        WHERE username = ?
        ORDER BY timestamp DESC
    """, (session["user"],)).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])
# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)