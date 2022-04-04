# This file is the actual code for the custom Python exporter export-to-spotify

from dataiku.exporter import Exporter
import os
from spotipy import Spotify
from spotifyapi.spotify_utils import init_spotify_auth

def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]

class SpotifyExporter(Exporter):
    def __init__(self, config, plugin_config):
        self.config = config
        self.plugin_config = plugin_config
        self.spotify_auth = self.config.get("spotify_auth")
        self.spotify_client: Spotify = init_spotify_auth("sso_auth", self.spotify_auth)
        self.tracks_to_export_to_spotify = []

    def validate_params(self, column_names):
        tracks_ids_column = self.config.get("track_id_column")
        if not tracks_ids_column in column_names:
            raise ValueError(f"The provided column name {tracks_ids_column} is not in the schema. Schema: {column_names}")

    def open(self, schema: list):
        column_names = [c["name"] for c in schema["columns"]]
        self.validate_params(column_names)
        self.tracks_ids_column_index = column_names.index(self.config.get("track_id_column"))
        self.current_user = self.spotify_client.current_user()

        playlist_name = self.config.get("playlist_name")

        try:
            new_playlist = self.spotify_client.user_playlist_create(
                user=self.current_user.get("id"),
                name=playlist_name,
                public=self.config.get("is_public"),
                collaborative=self.config.get("is_collaborative"),
            )
        except Exception as err:
            raise Exception(f"There have been a problem creating the playlist {playlist_name}. Make sure you use SSO Auth method and retry. Original Error: {err}")

        self.playlist_id = new_playlist.get("id")


    def write_row(self, row):
        self.tracks_to_export_to_spotify.append(row[self.tracks_ids_column_index])

    def perform_push_to_spotify(self):
        for tracks_chunck in batch(self.tracks_to_export_to_spotify, 100):
            self.spotify_client.user_playlist_add_tracks(
                user=self.current_user,
                playlist_id=self.playlist_id,
                tracks=tracks_chunck
            )

    def close(self):
        self.perform_push_to_spotify()

