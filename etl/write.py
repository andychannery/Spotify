# common module
from etl.common import *
from etl.fetch import get_track_uris
# api
import requests
from google.oauth2 import service_account
# reading data
import json
import pandas_gbq
# debugging
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Writes track(s) to playlist
def write_to_playlist(token, track_uris, playlist_id):
    '''
    Given a list of track uris, adds them to the given playlist id
    '''
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)

    offset = 50
    ctr = 0
    chunks = ((len(track_uris) - 1) // offset) + 1    
    
    for _ in range(chunks):
        uris = track_uris[ctr:ctr+offset]
        
        try:            
            request_body = json.dumps({
                "uris": uris
            })
            logging.info("Adding tracks to playlist...")
            response = requests.post(url=url,
                             data=request_body,
                             headers=headers,
                             )
        except requests.exceptions.RequestException as err:
            logging.error(f"Failed to write to playlist: {err}")
            return None
        
        ctr += offset
    
    logging.info(f"Status code: {response.status_code}")

# Removes track(s) from playlist
def remove_from_playlist(token, track_ids, playlist_id):
    '''
    Given a list of track uris, remove them from the given playlist id
    '''
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = get_auth_header(token)

    offset = 50
    ctr = 0
    chunks = ((len(track_ids) - 1) // offset) + 1

    logging.info("Removing tracks from playlist...")
    for _ in range(chunks):
        ids = track_ids[ctr:ctr+offset]
        track_uris = get_track_uris(token, ids)
        formatted_track_uris = [{"uri": f"{uri}"} for uri in track_uris]

        request_body = json.dumps({
            "tracks": formatted_track_uris
        })     
        
        try:
            response = requests.delete(url=url,
                                    data=request_body,
                                    headers=headers,
                                    )
        except requests.exceptions.RequestException as err:
            logging.error(f"Failed to remove tracks from playlist: {err}")
            return None

        ctr += offset

    logging.info(f"Status code: {response.status_code}")

# Write dataframe to BigQuery
def write_to_bq(df, table_id, if_exists='replace', table_schema=None):
    # Service account authentication
    try:
        keyfile = get_keyfile()
        credentials = service_account.Credentials.from_service_account_info(           
            keyfile,
        )
    except ValueError as e:
        logging.info(f"Invalid credentials...")
        logging.info(f"Message: {e}")

    logging.info(f"Writing to {table_id}...")
    # Write dataframe to BigQuery
    try:
        if not table_schema:
            pandas_gbq.to_gbq(df, credentials=credentials, destination_table=table_id, if_exists=if_exists)
        else:
            pandas_gbq.to_gbq(df, credentials=credentials, destination_table=table_id, if_exists=if_exists, table_schema=table_schema)
    except pandas_gbq.gbq.GenericGBQException as e:
        logging.info(f"Write failed...")
        logging.info(f"Message: {e}")