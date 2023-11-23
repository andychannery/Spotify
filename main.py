# environment variables
from dotenv import load_dotenv
import os
# fetch functions
from etl.fetch import get_token, get_playlist_tracks, get_track_features
from etl.write import write_to_playlist
# working with data
import numpy as np
import pandas as pd
# modelling
from sklearn.ensemble import RandomForestClassifier
import xgboost as xgb
import pickle

# environment variables
load_dotenv()

# fetch discover weekly playlist
def get_discover_weekly():
    # load environment variables
    discover_weekly_id = os.getenv("DISCOVER_WEEKLY_ID")

    # get access token
    token = get_token()

    # get discover weekly tracks
    discover_weekly = get_playlist_tracks(token, discover_weekly_id)
    
    # get audio features for discover weekly tracks
    track_ids = ','.join(discover_weekly.track_id.to_list())
    track_features = get_track_features(token, track_ids).drop(columns=['analysis_url', 'track_href', 'type'])

    # Build final dataframe
    df = discover_weekly.merge(track_features, how='inner', left_on='track_id', right_on='id').drop(columns=['id'])
    return df


if __name__ == "__main__":
    # load in model
    rf = pickle.load(open('ml_models/rf.sav', 'rb'))
    xgb = pickle.load(open('ml_models/xgb.sav', 'rb'))
    
    # fetch discover weekly playlist
    discover_weekly = get_discover_weekly()

    # make inference
    y_pred_rf = rf.predict(discover_weekly.drop(columns=['artist_id', 'track_id', 'track_name', 'uri', 'mode', 'time_signature']))
    y_pred_xgb = xgb.predict(discover_weekly.drop(columns=['artist_id', 'track_id', 'track_name', 'uri', 'mode', 'time_signature']))

    pred_like = discover_weekly[y_pred_rf.astype(bool)]
    pred_dislike = discover_weekly[(1 - y_pred_rf).astype(bool)]

    # # add predicted like songs to predicted like playlist
    write_to_playlist(get_token(), pred_like.uri.to_list(), os.getenv('PREDICTED_LIKE_ID'))

    # # add predicted dislike songs to predicted dislike playlist
    write_to_playlist(get_token(), pred_dislike.uri.to_list(), os.getenv('PREDICTED_DISLIKE_ID'))
