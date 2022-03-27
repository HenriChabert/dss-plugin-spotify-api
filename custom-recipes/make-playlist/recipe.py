# Code for custom code recipe make-playlist (imported from a Python recipe)

# Import the classes for accessing DSS objects from the recipe
import dataiku
from dataiku.customrecipe import *
from dataiku import pandasutils as pdu
import pandas as pd
import requests
import base64
import six
from unidecode import unidecode
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Define API keys
spotify_preset = get_recipe_config().get("spotify_preset")
spotify_client_id = spotify_preset.get("spotify_client_id")
spotify_client_secret = spotify_preset.get("spotify_client_secret")

#Establish API handle
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id=spotify_client_id,
    client_secret=spotify_client_secret))

# Get the artist ID
artist = get_recipe_config()['Artist']
artist = unidecode(artist)
artist = ' '.join(artist.split())
artist = artist.replace(' ','+')
results = spotify.search(artist)
artist_id = results['tracks']['items'][0]['artists'][0]['id']

# Get the genre
genre = get_recipe_config()['Genre']

# Get the number of songs
limit = get_recipe_config()['Song_Number']

# Get the prediction
results = spotify.recommendations(seed_artists=[artist_id],seed_genres=[genre],limit=limit)

# Create dataframe to store our songs
df = pd.DataFrame()

#Retrieve name, ID, artist
for track in results['tracks']:

    name = track['name']
    rec_artist = track['album']['artists'][0]['name']
    release_date = track['album']['release_date']
    duration = track['duration_ms']
    explicit = track['explicit']
    popularity = track['popularity']
    app = pd.DataFrame({
        'Song': [name],
        'Artist': [rec_artist],
        'Release_Date': [release_date],
        'Song_Duration': [duration],
        'Explicit': [explicit],
        'Popularity': [popularity]
    })
    df = df.append(app)

# Write the output to the output dataset
main_output_name = get_output_names_for_role('main_output')[0]
output_dataset =  dataiku.Dataset(main_output_name)
output_dataset.write_with_schema(df)