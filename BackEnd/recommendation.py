import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "dataset.csv")

def recommend_from_dataset(emotion, top_n=5):
    df = pd.read_csv(DATA_PATH)

    if "artist" in df.columns:
        artist_col = "artist"
    elif "artists" in df.columns:
        artist_col = "artists"
    elif "artist_name" in df.columns:
        artist_col = "artist_name"
    else:
        raise KeyError("No artist column found in dataset")

    if emotion == "Happy":
        df = df[(df.valence > 0.6) & (df.energy > 0.6)]
    elif emotion == "Sad":
        df = df[(df.valence < 0.4) & (df.energy < 0.4)]
    elif emotion == "Angry":
        df = df[(df.valence < 0.5) & (df.energy > 0.6)]
    elif emotion == "Surprise":
        df = df[df.energy > 0.6]
    else:
        df = df[(df.valence.between(0.4, 0.6)) & (df.energy.between(0.4, 0.6))]

    return df.head(top_n)[["track_name", artist_col]] \
        .rename(columns={artist_col: "artist"}) \
        .to_dict(orient="records")
