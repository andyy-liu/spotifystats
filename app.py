import os
from flask import Flask, session, request, redirect, render_template, url_for
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
load_dotenv()

client_id = os.environ['SPOTIPY_CLIENT_ID']
client_secret = os.environ['SPOTIPY_CLIENT_SECRET']
redirect_uri = os.environ['SPOTIPY_REDIRECT_URI']
scope = 'user-library-read playlist-modify-public playlist-modify-private user-top-read' # what the app gets access to

app = Flask(__name__)

app.config['SECRET_KEY'] = os.urandom(64)

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

    if request.args.get("code"): # checks if user has "code" which is what is obtained from the auth_url
        auth_manager.get_access_token(request.args.get("code")) # exchanges url for access token which is what allows the user to make requests
        return redirect('/tracks')

    if not auth_manager.validate_token(cache_handler.get_cached_token()): # check for token - if none proceed to next line
        auth_url = auth_manager.get_authorize_url() # pulls auth_url 
        return redirect(auth_url) # redirects user to auth_url page

    spObject = spotipy.Spotify(auth_manager=auth_manager) # if signed in already, sends to data page
    return redirect('/tracks')

@app.route('/tracks')
def topTracks():
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
                'artist': item['artists'][0]['name'],
                'url': item['album']['external_urls']['spotify']
            }
            if spObject_range == 'short_term':
                sTracks.append(track_info)
            elif spObject_range == 'medium_term':
                mTracks.append(track_info)
            elif spObject_range == 'long_term':
                aTracks.append(track_info)
            ctr += 1
        
    return render_template("tracks.html", sTracks=sTracks, mTracks=mTracks, aTracks=aTracks)

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
                'url': item['external_urls']['spotify']
            }
            if spObject_range == 'short_term':
                sArtists.append(artist_info)
            elif spObject_range == 'medium_term':
                mArtists.append(artist_info)
            elif spObject_range == 'long_term':
                aArtists.append(artist_info)
            ctr += 1
    return render_template("artists.html", sArtists=sArtists, mArtists=mArtists, aArtists=aArtists)

@app.route('/archive', methods=["POST","GET"])
def archive():
    if request.method == "POST":
        num_playlist = request.form["nm"]
        cache_handler = spotipy.cache_handler.FlaskSessionCacheHandler(session)
        auth_manager = spotipy.oauth2.SpotifyOAuth(cache_handler=cache_handler)

        spObject = spotipy.Spotify(auth_manager=auth_manager)

        playlists = spObject.current_user_playlists(limit=num_playlist)

        user_id = spObject.current_user()['id']
        song_uris = []
        archive_playlist = spObject.user_playlist_create(user_id, 'Archive', public='False', description=f'Collection of songs from the past {num_playlist} playlists')
        archive_id = archive_playlist['id']

        for playlist in playlists['items']:
            tmp_id = playlist['id']
            tmp = spObject.playlist_items(tmp_id, fields='items.track.id')
            for song in tmp['items']:
                try:
                    song_uri = song['track']['id']
                    song_uris.append(song_uri)
                except Exception as e:
                    print(f"Error in processing song: {e}")

        batch_size = 100
        for i in range(0, len(song_uris), batch_size):
            batch_uris = song_uris[i:i + batch_size]
            spObject.playlist_add_items(archive_id, batch_uris)
        success="Success!"
        return render_template("archive.html", hooray=success)
    else:
        return render_template("archive.html")

if __name__ == '__main__':
    app.run(debug=True)