# common module
from etl.common import *
# api
import requests
from google.oauth2 import service_account
# reading data
import json
import pandas as pd
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

    request_body = json.dumps({
        "uris": track_uris
    })
    
    logging.info("Adding tracks to playlist...")
    
    response = requests.post(url=url,
                             data=request_body,
                             headers=headers
                             )
    
    logging.info(f"Status code: {response.status_code}")

# Write dataframe to BigQuery
def write_to_bq(df, credentials_path, table_id, project_id, if_exists='replace', table_schema=None):
    
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
    )

    logging.info(f"Writing to {project_id}.{table_id}...")
    # Write dataframe to BigQuery
    try:
        if not table_schema:
            pandas_gbq.to_gbq(df, credentials=credentials, destination_table=table_id, if_exists=if_exists)
        else:
            pandas_gbq.to_gbq(df, credentials=credentials, destination_table=table_id, if_exists=if_exists, table_schema=table_schema)
    except pandas_gbq.gbq.GenericGBQException as e:
        logging.info(f"Write failed...")
        logging.info(f"Message: {e}")