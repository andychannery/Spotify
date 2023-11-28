# environment variables
import os
# fetch functions
from common import *
# modelling
import pickle
import json


def lambda_handler(event, context):

    rf = pickle.load(open('rf.sav', 'rb'))
    
    # fetch discover weekly playlist
    discover_weekly = get_discover_weekly()

    # make inference
    y_pred_rf = rf.predict(discover_weekly.drop(columns=['artist_id', 'track_id', 'track_name', 'uri', 'mode', 'time_signature']))

    # using random forest predictions
    pred_like = discover_weekly[y_pred_rf.astype(bool)]
    pred_dislike = discover_weekly[(1 - y_pred_rf).astype(bool)]

    # add predicted like songs to predicted like playlist
    write_to_playlist(get_token(), pred_like.uri.to_list(), os.environ.get('PREDICTED_LIKE_ID'))

    # add predicted dislike songs to predicted dislike playlist
    write_to_playlist(get_token(), pred_dislike.uri.to_list(), os.environ.get('PREDICTED_DISLIKE_ID'))
    
    return {
        'statusCode': 200,
        'body': json.dumps('Spotify Playlist Successfully Updated!')
    }
