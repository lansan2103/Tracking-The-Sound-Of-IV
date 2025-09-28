from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import os

# Change this to the folder where your CSV file is located
os.chdir("/Users/lancesanchez/Documents/IV Music Band Article")

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {"grant_type": "client_credentials"}
    results = post(url, headers=headers, data=data)
    json_result = json.loads(results.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]

    if len(json_result) == 0:
        print("No artist found")
        return None
    
    return json_result[0]

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result

token = get_token()
result = search_for_artist(token, "itzy")
print(result)

artist_id = result["id"]
songs = get_songs_by_artist(token, artist_id)

for id, song in enumerate(songs):
    print(f"{id + 1}. {song['name']}")

#print("Artist Info:")

name = result['name']
popularity = result['popularity']
followers = result['followers']['total']
genre = result['genres'][0]

print("Name:", name)
print("Popularity:", popularity)
print("Followers:", followers)
print("Genre:", genre)

import pandas as pd
import json
from requests import get

# --- Your existing functions (must already be defined) ---
# def get_token()
# def get_auth_header(token)
# def search_for_artist(token, artist_name)

# Genre cache to avoid repeated API calls
genre_cache = {}

def get_primary_genre_cached(token, artist_name):
    # Return cached result if available
    if artist_name in genre_cache:
        return genre_cache[artist_name]

    # Otherwise, fetch from API
    artist = search_for_artist(token, artist_name)
    if artist is None:
        genre_cache[artist_name] = ""
        return ""

    genres = artist.get("genres", [])
    primary_genre = genres[0] if genres else ""
    genre_cache[artist_name] = primary_genre
    print(artist_name, ':', primary_genre)
    return primary_genre

# Load the CSV
df = pd.read_csv("spotify_tracks.csv")

# Get token once
token = get_token()

# Apply genre lookup with caching
df["genres"] = df["artist_name"].apply(lambda name: get_primary_genre_cached(token, name))

# Save updated CSV
df.to_csv("spotify_tracks.csv", index=False)

print("Genres added and 'spotify_tracks.csv' updated successfully.")


'''
import csv
import time

# Step 4: Main loop
band_names = [
    "The Bad Neighbors", "Big Hungry", "Blue Lemonade", "CLIVE", "Cordoba", "Dawn Patrol",
    "Duende", "Eternal Wave", "Field Daze", "Lemon Generation", "Lizardsmouth", "Loc Dawgs",
    "Loot", "Magnetize", "Manners", "Mantis Finger", "Neil Erickson", "Orangepit!",
    "Pretty Cheeky", "Ray and Paul Holmberg", "The Framers", "The Radar"
]

token = get_token()
output = []

for band in band_names:
    print(f"Searching for: {band}")
    artist = search_for_artist(token, band)
    if artist:
        name = artist['name']
        popularity = artist['popularity']
        followers = artist['followers']['total']
        print(f"Found: {name} | Popularity: {popularity} | Followers: {followers}")
        output.append({"Name": name, "Popularity": popularity, "Followers": followers})
    else:
        print(f"Artist not found: {band}")
        output.append({"Name": band, "Popularity": "N/A", "Followers": "N/A"})
    
    time.sleep(0.3)  # Optional: avoid rate limits

# Step 5: Save to CSV
with open("spotify_band_data.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["Name", "Popularity", "Followers"])
    writer.writeheader()
    writer.writerows(output)

print("Data saved to spotify_band_data.csv")
'''