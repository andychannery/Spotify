# common module
from etl.common import *
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


# Returns DataFrame of tracks given a playlist id
def get_playlist_tracks(token, playlist_id):
    '''
    Given a playlist_id, returns a pandas dataframe with the following attributes:
        - artist id
        - track id
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
    artists = ','.join(artist_id).split(',') # to handle multiple artists per track
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
    df.genres = df.genres.astype(str)
    df.rename(columns={'id':'artist_id'}, inplace=True)
    df.drop_duplicates(subset=['artist_id'], inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df

# Returns DataFrame of track features
def get_track_features(token, track_ids):
    '''
    Given a list of track(s) ids, returns a pandas dataframe with the track_id and the track(s)' features:
    - track_id
    '''    
    headers = get_auth_header(token)    
    # tracks = track_ids.split(',')
    tracks = ','.join(track_ids).split(',')
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

# Returns a list of track uris
def get_track_uris(token, track_ids):
    '''
    Given a list of track ids, returns a list of uris corresponding to each track id
    '''    
    track_features = get_track_features(token, track_ids)
    logging.info("Fetching track uris...")
    uris = track_features['uri'].tolist()
    return uris