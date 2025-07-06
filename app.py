from flask import Flask, render_template, request
import pandas as pd
import os
import requests

app = Flask(__name__)

# Load and clean the dataset
df = pd.read_csv("songs.csv")
df['title'] = df['title'].astype(str).str.strip().str.lower()
df['artist'] = df['artist'].astype(str).str.title()
df['top genre'] = df['top genre'].astype(str).str.strip().str.lower()

# Get song cover using iTunes API
def get_song_cover(song, artist):
    try:
        query = f"{song} {artist}".strip().replace(" ", "+")
        url = f"https://itunes.apple.com/search?term={query}&limit=1"
        response = requests.get(url)
        data = response.json()
        if data['resultCount'] > 0:
            return data['results'][0]['artworkUrl100'].replace('100x100bb', '600x600bb')
    except:
        pass
    # Fallback image
    return "https://source.unsplash.com/800x400/?music"

# Recommend songs based on input
def recommend_songs(song_title):
    song_title_cleaned = song_title.strip().lower()

    matches = df[df['title'].str.contains(song_title_cleaned, na=False)]

    if matches.empty:
        return [], "❌ Song not found in database.", "Unknown Artist"

    matched_song = matches.iloc[0]
    genre = matched_song['top genre']
    actual_title = matched_song['title']
    artist = matched_song['artist']

    recommendations = df[(df['top genre'] == genre) & (df['title'] != actual_title)]

    if recommendations.empty:
        return [], "❌ No similar songs found in the same genre.", artist

    sample = recommendations.sample(n=min(5, len(recommendations)))
    return sample.to_dict(orient='records'), None, artist

@app.route('/')
def index():
    return render_template("index.html", recommendations=None, error=None)

@app.route('/recommend', methods=['POST'])
def recommend():
    song_input = request.form['song']
    recommendations, error, artist = recommend_songs(song_input)
    image = get_song_cover(song_input, artist)
    return render_template('index.html', recommendations=recommendations, error=error, image=image, input_song=song_input)

# Run the app
app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
