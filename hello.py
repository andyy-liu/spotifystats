from flask import Flask, redirect, url_for, render_template, request, session, jsonify

import urllib.parse

import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth 
from spotipy.oauth2 import SpotifyClientCredentials

app = Flask(__name__)
client_id = '72316ef112a44109b3f8b41c418a810c'
secret = 'bb7dd04b3c904ee197dc23868cb84410'
scope = 'user-library-read playlist-modify-public playlist-modify-private'

auth = SpotifyOAuth(client_id=client_id, client_secret=secret, redirect_uri='http://127.0.0.1:5000/redirect', scope='user-library-read playlist-modify-public playlist-modify-private', )

# Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():
    token_info = auth.get_cached_token()
    if not token_info:
        auth_url = auth.get_authorize_url()
        return redirect(auth_url)
    
    token = token_info['access_token']
    spotipy.Spotify(auth=token)

@app.route('/redirect')
def callback():
    url = request.url
    code = auth.parse_response_code(url)
    token = auth.get_access_token(code)
    return redirect("/success")

@app.route("/success")
def home():
    return render_template()
app.run(debug=True)
