import spotipy
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from typing import List

def init_spotify_auth(auth_mode, spotify_auth):
    """
    Returns a Spotify object that can be used to access the API
    """
    if auth_mode == "client_credentials":
        client_id = spotify_auth.get("client_id")
        client_secret = spotify_auth.get("client_secret")
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        return Spotify(client_credentials_manager=client_credentials_manager)
    elif auth_mode == "sso_auth":
        return Spotify(auth=spotify_auth.get("spotify_oauth_token"))
    else:
        raise ValueError(f"Invalid auth mode: {auth_mode}")