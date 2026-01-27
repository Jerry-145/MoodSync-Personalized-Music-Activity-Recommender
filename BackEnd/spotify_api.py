import requests
import base64
import os

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

def get_access_token():
    if not CLIENT_ID or not CLIENT_SECRET:
        print("❌ Spotify credentials not set")
        return None

    auth = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded = base64.b64encode(auth.encode()).decode()

    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={"grant_type": "client_credentials"}
    )

    data = response.json()

    if "access_token" not in data:
        print("❌ Spotify token error:", data)
        return None

    return data["access_token"]

def search_track(track_name, artist):
    token = get_access_token()
    if not token:
        return None

    response = requests.get(
        "https://api.spotify.com/v1/search",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "q": f"{track_name} {artist}",
            "type": "track",
            "limit": 1
        }
    )

    result = response.json()

    if "tracks" not in result or not result["tracks"]["items"]:
        return None

    track = result["tracks"]["items"][0]

    return {
        "name": track["name"],
        "artist": track["artists"][0]["name"],
        "preview_url": track["preview_url"],
        "spotify_url": track["external_urls"]["spotify"]
    }
