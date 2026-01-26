from flask import Flask, send_from_directory, request, jsonify
import subprocess
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
STATIC_DIR = os.path.join(FRONTEND_DIR, "static")

app = Flask(__name__, static_folder=STATIC_DIR)

@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory(STATIC_DIR, filename)

def get_recommendations(emotion):
    data = {
        "Happy": [
            {"name": "Happy Vibes", "audio": "audio/happy1.mp3"},
            {"name": "Feel Good Beats", "audio": "audio/happy2.mp3"}
        ],
        "Sad": [
            {"name": "Soft Piano", "audio": "audio/sad1.mp3"}
        ],
        "Angry": [
            {"name": "Power Energy", "audio": "audio/happy1.mp3"}
        ],
        "Love": [
            {"name": "Romantic Mood", "audio": "audio/happy2.mp3"}
        ],
        "Neutral": [
            {"name": "Lo-fi Chill", "audio": "audio/happy1.mp3"}
        ]
    }
    return data.get(emotion, [])

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

    with open(os.path.join(BASE_DIR, "emotion.txt"), "w") as f:
        f.write(emotion)

    return jsonify({
        "emotion": emotion,
        "tracks": get_recommendations(emotion)
    })

@app.route("/detect", methods=["POST"])
def camera_detect():
    subprocess.run(["python", "face_emotion.py"], cwd=BASE_DIR)

    emotion = "Neutral"
    file_path = os.path.join(BASE_DIR, "emotion.txt")

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            emotion = f.read().strip()

    return jsonify({
        "emotion": emotion,
        "tracks": get_recommendations(emotion)
    })

if __name__ == "__main__":
    app.run(debug=True)
