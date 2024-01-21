import os
from flask import Flask, session, request, redirect, render_template, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
load_dotenv()

client_id = os.environ['SPOTIPY_CLIENT_ID']
client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
redirect_uri = os.environ['SPOTIPY_REDIRECT_URI']
scope = 'user-library-read playlist-modify-public playlist-modify-private user-read-currently-playing user-top-read' # what the app gets access to


auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=client_id,
                                               client_secret = client_secret,
                                               redirect_uri = redirect_uri,
                                               scope=scope, 
                                               show_dialog=True)

spObject = spotipy.Spotify(auth_manager=auth_manager)

ranges = ['short_term']
sTracks = []  # Initialize an empty list to store the result strings
mTracks = []
aTracks = []


for spObject_range in ranges:
    results = spObject.current_user_top_artists(time_range=spObject_range, limit=1)
    print(results['items']
)