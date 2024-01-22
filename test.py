import os
import sys
from flask import Flask, session, request, redirect, render_template, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
load_dotenv()

client_id = os.environ['SPOTIPY_CLIENT_ID']
client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
redirect_uri = os.environ['SPOTIPY_REDIRECT_URI']
scope = 'user-library-read playlist-modify-public playlist-modify-private user-read-currently-playing user-top-read playlist-read-private' # what the app gets access to


auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=client_id,
                                               client_secret = client_secret,
                                               redirect_uri = redirect_uri,
                                               scope=scope, 
                                               show_dialog=True)

spObject = spotipy.Spotify(auth_manager=auth_manager)

playlists = spObject.current_user_playlists(limit=10)
user_id = spObject.current_user()['id']
song_uris = []
for playlist in playlists['items']:
        tmp_id = playlist['id']
        tmp = spObject.playlist_items(tmp_id, fields='items.track.id')
        for song in tmp['items']:
            try:
                song_uri = song['track']['id']
                song_uris.append(song_uri)
            except Exception as e:
                print(f"Error in processing song: {e}")
print(song_uris)
