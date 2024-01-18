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

@app.template_filter(name='linebreaker')
def linebreaksbr_filter(text):
    return text.replace('\n', '<br>')

# Endpoints/Routes
@app.route('/')
def index():
    return render_template("index.html")

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

    spObject = spotipy.Spotify(auth_manager=auth_manager) # if signed in already, sends to data page
    return redirect('/data')

@app.route('/data')
def data():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)

    spObject = spotipy.Spotify(auth_manager=auth_manager)

    ranges = ['short_term', 'medium_term','long_term']
    sTracks = []  # Initialize an empty list to store the result strings
    mTracks = []
    aTracks = []
    

    for spObject_range in ranges:
        results = spObject.current_user_top_tracks(time_range=spObject_range, limit=25)
        ctr = 1
        for item in results['items']:
            track_info = {
                'number': ctr,
                'image': item['album']['images'][0]['url'],
                'name': item['name'],
                'artist': item['artists'][0]['name']
            }
            if spObject_range == 'short_term':
                sTracks.append(track_info)
            elif spObject_range == 'medium_term':
                mTracks.append(track_info)
            elif spObject_range == 'long_term':
                aTracks.append(track_info)
            ctr += 1
        
    return render_template("data.html", sTracks=sTracks, mTracks=mTracks, aTracks=aTracks)

@app.route('/artists')
def topArtists():
    cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
    auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)

    spObject = spotipy.Spotify(auth_manager=auth_manager)

    sArtists = []  # Initialize an empty list to store the result strings
    mArtists = []
    aArtists = []

    for spObject_range in ['short_term', 'medium_term', 'long_term']:
        results = spObject.current_user_top_artists(time_range=spObject_range, limit=25)
        ctr = 1
        for item in results['items']:
            artist_info = {
                'number': ctr,
                'name': item['name'],
                'image': item['images'][0]['url'],
            }
            if spObject_range == 'short_term':
                sArtists.append(artist_info)
            elif spObject_range == 'medium_term':
                mArtists.append(artist_info)
            elif spObject_range == 'long_term':
                aArtists.append(artist_info)
    return render_template("artists.html", sArtists=sArtists, mArtists=mArtists, aArtists=aArtists)

if __name__ == '__main__':
    app.run(debug=True)