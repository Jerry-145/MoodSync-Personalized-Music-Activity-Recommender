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
    dataset_tracks = recommend_from_dataset(emotion)
    final_tracks = []

    for t in dataset_tracks:
        api_data = search_track(t["track_name"], t["artist"])

        final_tracks.append({
            "name": t["track_name"],
            "artist": t["artist"],
            "preview_url": api_data["preview_url"] if api_data else None
        })

    return jsonify({
        "emotion": emotion,
        "tracks": final_tracks
    })

@app.route("/history_page")
def history_page():
    if "user" not in session:
        return redirect("/login")
    return send_from_directory(FRONTEND_DIR, "history.html")

@app.route("/popular")
def popular():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

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
            "preview_url": api_data["preview_url"] if api_data else None
        })

    return jsonify(final_tracks)

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

@app.route("/analytics_page")
def analytics_page():
    if "user" not in session:
        return redirect("/login")
    return send_from_directory(FRONTEND_DIR, "analytics.html")

@app.route("/search", methods=["GET"])
def search():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    query = request.args.get("q")
    if not query:
        return jsonify([])

    from spotify_api import search_track  # already exists

    # Search directly using Spotify API
    token = search_track(query, "")  # quick search using name only

    if not token:
        return jsonify([])

    return jsonify([{
        "name": token["name"],
        "artist": token["artist"],
        "preview_url": token["preview_url"]
    }])

# ---------- History Saved ----------
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
    conn.close()

    return jsonify({"status": "saved"})


# ---------- STATIC FILES ----------
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(STATIC_DIR, filename)

# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    app.run(debug=True)
