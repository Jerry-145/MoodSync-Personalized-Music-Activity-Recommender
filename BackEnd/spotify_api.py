import requests
import base64
import os

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

def get_access_token():
    if not CLIENT_ID or not CLIENT_SECRET:
        return None

    auth = f"{CLIENT_ID}:{CLIENT_SECRET}"
    encoded = base64.b64encode(auth.encode()).decode()

    res = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={
            "Authorization": f"Basic {encoded}",
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={"grant_type": "client_credentials"}
    )

    data = res.json()
    return data.get("access_token")

def search_track(track_name, artist=""):
    token = get_access_token()
    if not token:
        return None

    query = track_name if not artist else f"{track_name} {artist}"

    res = requests.get(
        "https://api.spotify.com/v1/search",
        headers={"Authorization": f"Bearer {token}"},
        params={
            "q": query,
            "type": "track",
            "limit": 10   # 🔥 increase results
        }
    )

    data = res.json()
    items = data.get("tracks", {}).get("items", [])

    if not items:
        return None

    # 🔥 IMPORTANT: find track WITH preview
    for track in items:
        if track["preview_url"]:
            return {
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "preview_url": track["preview_url"],
                "spotify_url": track["external_urls"]["spotify"]
            }

    # fallback (no preview)
    track = items[0]
    return {
        "name": track["name"],
        "artist": track["artists"][0]["name"],
        "preview_url": track["preview_url"],
        "spotify_url": track["external_urls"]["spotify"]  # ⭐ IMPORTANT
    }