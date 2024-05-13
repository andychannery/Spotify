import os
# api
import requests
# reading data
import pandas as pd
import json
# debugging
import logging

# Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Environment variables
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
access_token = os.environ.get("ACCESS_TOKEN")
refresh_token = os.environ.get("REFRESH_TOKEN")

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

    return new_token_info['access_token']

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

# Writes track(s) to playlist
def write_to_playlist(token, track_uris, playlist_id):
    '''
    Given a list of track uris, adds them to the given playlist id
    '''
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)

    request_body = json.dumps({
        "uris": track_uris
    })
    
    logging.info("Adding tracks to playlist...")
    
    response = requests.post(url=url,
                             data=request_body,
                             headers=headers
                             )
    
    logging.info(f"Status code: {response.status_code}")

# fetch discover weekly playlist
def get_discover_weekly():
    # load environment variables
    discover_weekly_id = os.environ.get("DISCOVER_WEEKLY_ID")

    # get access token
    token = get_token()

    # get discover weekly tracks
    discover_weekly = get_playlist_tracks(token, discover_weekly_id)
    
    # get audio features for discover weekly tracks
    track_ids = discover_weekly.track_id.to_list()
    track_features = get_track_features(token, track_ids).drop(columns=['analysis_url', 'track_href', 'type'])

    # Build final dataframe
    df = discover_weekly.merge(track_features, how='inner', left_on='track_id', right_on='id').drop(columns=['id'])
    return df