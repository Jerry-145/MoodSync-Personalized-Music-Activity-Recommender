import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "dataset.csv")

# Load dataset ONCE (faster)
df = pd.read_csv(DATA_PATH)


def recommend_from_dataset(emotion, top_n=5):
    global df

    # Detect correct artist column
    if "artist" in df.columns:
        artist_col = "artist"
    elif "artists" in df.columns:
        artist_col = "artists"
    elif "artist_name" in df.columns:
        artist_col = "artist_name"
    else:
        raise KeyError("No artist column found in dataset")

    # =========================
    # STRONG EMOTION FILTERING
    # =========================
    if emotion == "Happy":
        filtered = df[(df.valence > 0.7) & (df.energy > 0.6)]

    elif emotion == "Sad":
        filtered = df[(df.valence < 0.3) & (df.energy < 0.4)]

    elif emotion == "Angry":
        filtered = df[(df.valence < 0.4) & (df.energy > 0.7)]

    elif emotion == "Love":
        filtered = df[(df.valence > 0.8) & (df.energy.between(0.4, 0.7))]

    else:
        filtered = df

    # =========================
    # RANDOM SELECTION (IMPORTANT)
    # =========================
    if len(filtered) >= top_n:
        result = filtered.sample(n=top_n)
    else:
        result = filtered

    return result[["track_name", artist_col]] \
        .rename(columns={artist_col: "artist"}) \
        .to_dict(orient="records")