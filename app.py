import os
from flask import Flask, session, request, redirect, render_template, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth

client_id = os.environ['SPOTIPY_CLIENT_ID']
client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
redirect_uri = os.environ['SPOTIPY_REDIRECT_URI']
scope = 'user-library-read playlist-modify-public playlist-modify-private user-read-currently-playing user-top-read' # what the app gets access to

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(64)

# Endpoints/Routes
@app.route('/')
def index():
    return render_template("data.html")

@app.route('/login')
def login():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(client_id=client_id,
                                               client_secret = client_secret,
                                               redirect_uri = redirect_uri,
                                               scope=scope, 
                                               cache_handler=cache_handler, 
                                               show_dialog=True)

    if request.args.get("code"): # redirects from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/data')

    if not auth_manager.validate_token(cache_handler.get_cached_token()): # check for token - if none then gets auth_url and sends to user
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_url)

    spotify = spotipy.Spotify(auth_manager=auth_manager) # if signed in already, sends to data page
    return redirect('/data')

@app.route('/data')
def data():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)

    sp = spotipy.Spotify(auth_manager=auth_manager)

    ranges = ['short_term', 'medium_term', 'long_term']
    result_string = ''

    for sp_range in ranges:
        result_string += f"range: {sp_range}\n"
        results = sp.current_user_top_tracks(time_range=sp_range, limit=50)
        for i, item in enumerate(results['items']):
            result_string += f"{i} {item['name']} // {item['artists'][0]['name']}\n"
    return result_string

@app.route('/tracks')
def topTracks():
    return