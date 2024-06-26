# etl helpers
from etl.common import get_token
from etl.fetch import get_playlist_tracks, get_artist_attribute, get_track_features
from etl.write import write_to_bq
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
    playlists = ["LIKE_PLAYLIST", "DISLIKE_PLAYLIST", "DISCOVER_WEEKLY", "PERSONAL_PLAYLIST"]
    
    for playlist in playlists:
        playlist_id = os.getenv(playlist + "_ID")
        
        # fetch playlist data        
        playlist_tracks = get_playlist_tracks(token, playlist_id)
        playlist_track_features = get_track_features(token, playlist_tracks.track_id.to_list())        
        playlist_artists = get_artist_attribute(token, playlist_tracks.artist_id.to_list())

        # write playlist data to BigQuery
        for df, item in zip([playlist_tracks, playlist_track_features, playlist_artists],                             
                            ["TRACKS", "TRACK_FEATURES", "ARTISTS"]):
            logging.info(f"Writing RAW.{playlist}_{item} to BigQuery...")
            write_to_bq(df,                  
                table_id=f"RAW.{playlist}_{item}",                
                if_exists='replace')

if __name__ == "__main__":
    main()