# etl helpers
from etl.common import get_token
from etl.fetch import get_playlist_tracks, get_track_uris
from etl.write import write_to_playlist, remove_from_playlist
# environment variables
import os
from dotenv import load_dotenv
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

    token = get_token()

    # fetch playlist data
    personal_playlist_tracks = set(get_playlist_tracks(token, os.getenv("PERSONAL_PLAYLIST_ID"))['track_id'])
    predicted_dislike_tracks = set(get_playlist_tracks(token, os.getenv("PREDICTED_DISLIKE_ID"))['track_id'])
    predicted_like_tracks = set(get_playlist_tracks(token, os.getenv("PREDICTED_LIKE_ID"))['track_id'])
    dislike_tracks = set(get_playlist_tracks(token, os.getenv("DISLIKE_PLAYLIST_ID"))['track_id'])
    like_tracks = set(get_playlist_tracks(token, os.getenv("LIKE_PLAYLIST_ID"))['track_id'])
    
    # assign like predictions to actual like and dislike
    to_like_playlist = predicted_like_tracks.intersection(personal_playlist_tracks)
    # assume dislike predicts are accurate
    to_dislike_playlist = predicted_dislike_tracks.union(predicted_like_tracks.difference(to_like_playlist))
    # only add new songs to like and dislike
    to_like_playlist = to_like_playlist.difference(like_tracks)
    to_dislike_playlist = to_dislike_playlist.difference(dislike_tracks)

    # get uris for songs to load
    for playlist, to_playlist_id in zip([to_like_playlist, to_dislike_playlist], [os.getenv("LIKE_PLAYLIST_ID"), os.getenv("DISLIKE_PLAYLIST_ID")]):
        if len(playlist) > 0:
            # fetch song uris
            uris = get_track_uris(token, list(playlist))
            # write songs to playlist
            write_to_playlist(token, uris, to_playlist_id)
    
    # remove songs from prediction playlists
    remove_from_playlist(token, list(predicted_like_tracks), os.getenv("PREDICTED_LIKE_ID"))
    remove_from_playlist(token, list(predicted_dislike_tracks), os.getenv("PREDICTED_DISLIKE_ID"))

if __name__ == "__main__":
    main()