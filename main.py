import requests
import re
from bs4 import BeautifulSoup
import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth


SPOTIFY_CLIENT_ID = os.environ["ENV_SPOTIFY_CLIENT_ID"]
SPOTIFY_CLIENT_SECRET = os.environ["ENV_SPOTIFY_CLIENT_SECRET"]

date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD:")
billboard_url = f"https://www.billboard.com/charts/hot-100/{date}"

response = requests.get(billboard_url)
html_doc = response.text

soap = BeautifulSoup(html_doc, "html.parser")

# titles = [title.getText().replace("\n", "").replace("\t", "") for title in soap.select("li #title-of-a-story")]
song_names = [re.sub(r'[\t|\n]+', "", title.getText()) for title in soap.select("li #title-of-a-story")]
song_uris = []
year = date.split("-")[0]
spotify_credentials = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    scope="playlist-modify-private",
    redirect_uri="http://example.com",
    show_dialog=True,
    cache_path="token.txt"
)
sp = spotipy.Spotify(auth_manager=spotify_credentials)
user_id = sp.current_user()["id"]

for song in song_names:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

playlist = sp.user_playlist_create(user=user_id, name=f"{date} Billboard 100", public=False)
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
