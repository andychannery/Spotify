from fetch import *
from dotenv import load_dotenv
import os

load_dotenv()

discover_weekly_id = os.getenv("DISCOVER_WEEKLY_ID")
personal_playlist_id = os.getenv("PERSONAL_PLAYLIST_ID")
token = get_token()
# personal_playlist = get_playlist_tracks(token, personal_playlist_id)
# track_features = get_track_features(token, ','.join(personal_playlist['track_id'].to_list()))
# artist_features = get_artist_attribute(token, ','.join(personal_playlist['artist_id'].to_list()))
top_tracks = get_user_top_items(token)

print(top_tracks)

