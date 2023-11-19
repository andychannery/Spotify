# environment variables
from dotenv import load_dotenv
import dotenv
import os
# api
import requests
# reading data
import json
import pandas as pd
# debugging
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Load in env variables from .env file
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
refresh_token = os.getenv("REFRESH_TOKEN")
expires_at = os.getenv("EXPIRES_AT") # TODO: Implement expiry logic for refresh token


# Returns authorization header
def get_auth_header(token):
    return {"Authorization": f"Bearer {token}"}

# Returns API token
def get_token():
    url = "https://accounts.spotify.com/api/token"
    request_body = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }

    response = requests.post(url, data=request_body)
    new_token_info = response.json()

    dotenv_file = dotenv.find_dotenv()
    dotenv.load_dotenv(dotenv_file)

    os.environ["ACCESS_TOKEN"] = new_token_info['access_token']

    # Write changes to .env file.
    dotenv.set_key(dotenv_file, "ACCESS_TOKEN", os.environ["ACCESS_TOKEN"])

    return new_token_info['access_token']

# Returns DataFrame of playlist ids given a user's id
def get_user_playlists(token, user_id):
    '''
    TODO: Can loop through offsets of 50 to fetch more playlists all at once
    Given a user_id, returns a pandas dataframe with the following attributes:
        - playlist_id
    '''
    url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
    headers = get_auth_header(token)
    query = "?fields=items(id)&limit=50&offset=0"
    query_url = url + query
    logging.info(f"Fetching playlists...")
    result = requests.get(query_url, headers=headers)
    if result.status_code == 200: 
        json_result = json.loads(result.content)["items"]
    else:
        logging.error(f"Failed to fetch playlists: {result.text}")
        raise
    
    # json to pandas dataframe
    df = pd.json_normalize(json_result)    
    
    # rename columns
    cur_colnames = list(df.columns)
    new_colnames = ["playlist_id"]
    map_colnames = {cur_name : new_name for cur_name, new_name in zip(cur_colnames, new_colnames)}
    df.rename(columns=map_colnames, inplace=True) 
    return df

# Returns DataFrame of tracks given a playlist id
def get_playlist_tracks(token, playlist_id):
    '''
    Given a playlist_id, returns a pandas dataframe with the following attributes:
        - artist id
        - track name
        - track popularity rating (0-100)
    '''
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)
    offset = 0
    limit = 100
    final_result = []

    logging.info("Fetching tracks...")
    
    while True:
        query_params = {
            "fields":"items(track(name, id, popularity, artists(id)))",
            "limit":limit,
            "offset":offset,
        }

        result = requests.get(url, headers=headers, params=query_params)
        
        try:
            result.raise_for_status()
        except requests.exceptions.RequestException as err:
            logging.error(f"Failed to fetch tracks: {err}")
            return None
        
        json_result = json.loads(result.content)["items"]
        final_result.extend(json_result)
        
        if len(json_result) < limit:
            break
        else:
            offset += len(json_result)

    if not final_result:
        logging.info("There are no songs in this playlist...")

    # json to pandas dataframe
    df = pd.json_normalize(final_result)
    
    # convert list of dict to comma delimited string of artist ids (if more than one artist)
    df["track.artists"] = df["track.artists"].map(lambda row: ",".join([d["id"] for d in row]))
    
    # rename columns
    df.rename(columns={
        "track.artists": "artist_id",
        "track.id": "track_id",
        "track.name": "track_name",
        "track.popularity": "popularity",
    }, inplace=True)   
        
    return df  

# Returns DataFrame of artist attributes 
def get_artist_attribute(token, artist_id):
    '''
    Given artist(s) ids, returns a pandas dataframe with the following attributes:
    - artist_id
    - genres
    - name
    - popularity
    '''        
    headers = get_auth_header(token)
    artists = artist_id.split(',')
    chunks = ((len(artists) - 1) // 50) + 1
    final_result = []    
    offset = 50
    ctr = 0

    logging.info("Fetching artist(s)...")
    
    for _ in range(chunks):
        ids = ','.join(artists[ctr:ctr+offset])
        url = f"https://api.spotify.com/v1/artists/?ids={ids}"
        result = requests.get(url, headers=headers)
        
        try:
            json_result = json.loads(result.content)["artists"]
            final_result.extend(json_result)
        except requests.exceptions.RequestException as err:
            logging.error(f"Failed to fetch artist(s): {err}")
            return None
        
        ctr += offset
    
    # convert to pandas dataframe
    df = pd.DataFrame(final_result)[['id', 'genres', 'name', 'popularity']]
    df.rename(columns={'id':'artist_id'}, inplace=True)
    df.drop_duplicates(subset=['artist_id'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df

# Returns DataFrame of track features
def get_track_features(token, track_ids):
    '''
    Given track(s) ids, returns a pandas dataframe with the track_id and the track(s)' features:
    - track_id
    '''    
    headers = get_auth_header(token)    
    tracks = track_ids.split(',')
    chunks = ((len(tracks) - 1) // 50) + 1
    final_result = []
    offset = 50
    ctr = 0
    
    logging.info("Fetching track features...")
    
    for _ in range(chunks):
        ids = ','.join(tracks[ctr:ctr+offset])
        url = f"https://api.spotify.com/v1/audio-features/?ids={ids}"
        try:
            result = requests.get(url, headers=headers)
            json_result = json.loads(result.content)["audio_features"]
            final_result.extend(json_result)
        except requests.exceptions.RequestException as err:
            logging.error(f"Failed to fetch track features: {err}")
            return None
        
        ctr += offset

    df = pd.json_normalize(final_result)
    
    # json to pandas dataframe    
    return df


# Returns DataFrame of user's top item
def get_user_top_items(token, item='tracks'):
    
    # Returns a pandas dataframe with the user's top items:
    #     - tracks
    #     - artists
    
    url = f"https://api.spotify.com/v1/me/top/tracks"
    headers = get_auth_header(token)    
    final_result = []
    offset = 0
    limit = 50
    
    logging.info(f"Fetching user's top {item}...")
    
    while True:        
        query_params = {
            "limit": 50,
            "offset": 0,
        }
        try:
            result = requests.get(url, headers=headers, params=query_params)        
            json_result = json.loads(result.content)["audio_features"]
            final_result.extend(json_result)
        except requests.exceptions.RequestException as err:
            logging.error(f"Failed to fetch top {item}: {err}")
            return None
        
        if json_result < limit:
            break
        offset += 50
    
    df = pd.json_normalize(final_result)
    
    # json to pandas dataframe    
    return df

if __name__ == "__main__":    
    like_playlist = get_playlist_tracks(get_token(), os.getenv("LIKE_PLAYLIST_ID"))
    like_playlist['label'] = True
    dislike_playlist = get_playlist_tracks(get_token(), os.getenv("DISLIKE_PLAYLIST_ID"))
    dislike_playlist['label'] = False
    final_playlist = pd.concat([like_playlist, dislike_playlist])
