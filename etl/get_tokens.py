from flask import Flask, request, session, url_for
from flask_oauthlib.client import OAuth
from dotenv import load_dotenv
import dotenv
import os
from datetime import datetime

app = Flask(__name__)
load_dotenv()

# To make use of the flask session (i.e. access it) we need a secret key
app.secret_key = os.getenv("FLASK_SECRET_KEY")

oauth = OAuth(app)

# Spotify API to send these when user grants authorization
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

# Spotify auth endpoint
AUTH_URL = 'https://accounts.spotify.com/authorize'
# Spotify token endpoint
TOKEN_URL = 'https://accounts.spotify.com/api/token'
# Spotify base url
API_BASE_URL = 'https://api.spotify.com/v1/'

spotify = oauth.remote_app(
    'spotify',
    consumer_key=CLIENT_ID,
    consumer_secret=CLIENT_SECRET,
    base_url=API_BASE_URL,
    request_token_url=None,
    request_token_params={'scope': 'playlist-modify-public user-top-read user-read-recently-played playlist-modify-private'},
    access_token_method='POST',
    access_token_url=TOKEN_URL,
    authorize_url=AUTH_URL, 
)

# Login endpoint
@app.route('/')
def login():
    return spotify.authorize(callback=url_for('authorized', _external=True))

# Logout endpoint
@app.route('/logout')
def logout():
    session.pop('spotify_token', None)
    return 'Logged out successfully!'

# Callback endpoint
# User logs in successfully, Spotify API sends code to request access token
# User fails to log in successfully, Spotify calls the callback endpoint and gives an error
@app.route('/login/authorized')
def authorized():
    response = spotify.authorized_response()
    
    # unsuccessful login
    if response is None or 'access_token' not in response:
        return f'Access denied: reason={request.args["error_reason"]} error={request.args["error_description"]}'
    
    # successful login
    if 'access_token' in response:        
        session['access_token'] = response['access_token']
        session['refresh_token'] = response['refresh_token']
        session['expires_at'] = datetime.now().timestamp() + response['expires_in']

        dotenv_file = dotenv.find_dotenv()
        dotenv.load_dotenv(dotenv_file)

        os.environ["ACCESS_TOKEN"] = session['access_token']
        os.environ["REFRESH_TOKEN"] = session['refresh_token']
        os.environ["EXPIRES_AT"] = session['expires_at']

        # Write changes to .env file.
        dotenv.set_key(dotenv_file, "ACCESS_TOKEN", os.environ["ACCESS_TOKEN"])
        dotenv.set_key(dotenv_file, "REFRESH_TOKEN", os.environ["REFRESH_TOKEN"])
        dotenv.set_key(dotenv_file, "EXPIRES_AT", os.environ["EXPIRES_AT"])

        user_info = spotify.get('me')

    return f'Logged in as: {user_info.data["id"]}'

# Token getter & refresher
@spotify.tokengetter
def get_spotify_token():
    return session.get('access_token')

if __name__ == "__main__":
    app.run(debug=True)
    
    