# import other files
import sys
sys.path.append("..")
# environment variables
from dotenv import load_dotenv
import os
# fetch functions
from etl.fetch import *
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
    track_features = get_track_features(token, track_ids).drop(columns=['analysis_url', 'track_href', 'type', 'uri'])

    # Build final dataframe
    df = discover_weekly.merge(track_features, how='inner', left_on='track_id', right_on='id').drop(columns=['id'])
    return df

# fetch corresponding audio features

# make inference on discover weekly playlist
# y_pred = loaded_model.predict(X)

# create write.py module

# add songs to predicted like and predicted dislike playlists

# automate process with lambda and eventbridge

if __name__ == "__main__":
    # load in model
    rf = pickle.load(open('rf.sav', 'rb'))
    xgb = pickle.load(open('xgb.sav', 'rb'))
    
    discover_weekly = get_discover_weekly()

    y_pred = rf.predict(discover_weekly)



