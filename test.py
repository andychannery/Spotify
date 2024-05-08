# etl helpers
from etl.common import get_token
from etl.fetch import get_playlist_tracks, get_artist_attribute, get_track_features
from etl.write import write_to_playlist, write_to_bq
# environment variables
from dotenv import load_dotenv
import os
# logger
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def main():
    # load dotenv file
    load_dotenv()
    
    # fetch playlists from Spotify then write directly to BigQuery
    token = get_token()
    playlists = ["LIKE_PLAYLIST", "DISLIKE_PLAYLIST", "DISCOVER_WEEKLY"]
    
    for playlist in playlists:
        playlist_id = os.getenv(playlist + "_ID")
        
        # fetch playlist data        
        playlist_tracks = get_playlist_tracks(token, playlist_id)
        playlist_track_features = get_track_features(token, ','.join(playlist_tracks.track_id.to_list()))        
        playlist_artists = get_artist_attribute(token, ','.join(playlist_tracks.artist_id.to_list()))

        # write playlist data to BigQuery
        for df, item in zip([playlist_tracks, playlist_track_features, playlist_artists],                             
                            ["TRACKS", "TRACK_FEATURES", "ARTISTS"]):
            logging.info(f"Writing RAW.{playlist}_{item} to BigQuery...")
            write_to_bq(df,                  
                table_id=f"RAW.{playlist}_{item}",                
                project_id=os.getenv("PROJECT_ID"), 
                if_exists='replace')

# Not sure if I can also set up DBT to regenerate tables upon raw tables updating via github actions
# TODO: set up DBT project to create staging tables then eventually mart or dim/facts 

# TODO: read like and dislike playlists from BQ, retrain model, read discover weekly from BQ, then make inference and write to Spotify

if __name__ == "__main__":
    main()