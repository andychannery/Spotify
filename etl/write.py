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
