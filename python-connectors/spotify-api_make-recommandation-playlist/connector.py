# This file is the actual code for the custom Python dataset spotify-api_make-recommandation-playlist

# import the base class for the custom dataset
from dataiku.connector import Connector
from spotifyapi.spotify_utils import init_spotify_auth
import itertools
class MyConnector(Connector):
    ALL_FEATURES = [
        "acousticness",
        "danceability",
        "duration_ms",
        "energy",
        "instrumentalness",
        "key",
        "liveness",
        "loudness",
        "mode",
        "speechiness",
        "tempo",
        "time_signature",
        "valence",
        "popularity"
    ]
    FEATURE_MODIFIERS = [
        "max",
        "min",
        "target"
    ]

    def __init__(self, config, plugin_config):
        Connector.__init__(self, config, plugin_config)  # pass the parameters to the base class
        self.auth_mode = self.config.get("auth_mode")
        self.spotify_auth = self.config.get("spotify_client_crendentials") if self.auth_mode == "client_credentials" else self.config.get("spotify_sso")
        
        self.spotify_client = init_spotify_auth(self.auth_mode, self.spotify_auth)
        self.validate_params()

    def get_read_schema(self):
            return None

    def validate_params(self):
        seed_artists_ids = self.config.get("seed_artists_ids", [])
        seed_tracks_ids = self.config.get("seed_tracks_ids", [])
        seed_genres = self.config.get("seed_genres", [])

        if len(seed_artists_ids + seed_tracks_ids + seed_genres) == 0:
            raise ValueError("At least one of seed_artists_ids, seed_tracks_ids or seed_genres must be provided")

        nb_of_tracks = self.config.get("nb_of_tracks")
        if nb_of_tracks is None or not 0 < nb_of_tracks <= 100:
            raise ValueError("nb_of_tracks must be a positive integer between 1 and 100")

        extra_features = self.config.get("extra_features")
        allowed_values_for_features = ["_".join(f) for f in list(itertools.product(self.FEATURE_MODIFIERS, self.ALL_FEATURES))]

        if extra_features is not None:
            for feature_name, feature_value in extra_features.items():
                if feature_name not in allowed_values_for_features:
                    raise ValueError("Invalid feature: {}".format(feature_name))
                try:
                    _ = float(feature_value)
                except ValueError:
                    raise ValueError("Value for feature {} should be a float (Currently {})".format(feature_name, feature_value))


    def generate_playlist_on_recommandation(self):
        extra_features = self.config.get("extra_features", {})
        generated_playlist = self.spotify_client.recommendations(
            seed_artists=self.config.get("seed_artists_ids"),
            seed_tracks=self.config.get("seed_tracks_ids"),
            seed_genres=self.config.get("seed_genres"),
            limit=self.config.get("nb_of_tracks"),
            **extra_features
        )
        return generated_playlist

    def add_features_to_tracks(self, tracks):
        tracks_with_features = []
        tracks_ids = [track.get("id") for track in tracks]
        tracks_features = self.spotify_client.audio_features(tracks_ids)
        for track_i, track in enumerate(tracks):
            tracks_with_features.append(dict(track, **tracks_features[track_i]))
        return tracks_with_features

    def generate_rows(self, dataset_schema=None, dataset_partitioning=None,
                            partition_id=None, records_limit = -1):
        generated_playlist = self.generate_playlist_on_recommandation()
        tracks_in_playlist = generated_playlist.get("tracks", [])
        if self.config.get("add_features_to_tracks"):
            tracks_in_playlist = self.add_features_to_tracks(tracks_in_playlist)
        for track in tracks_in_playlist:
            yield track
