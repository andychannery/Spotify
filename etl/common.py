# environment variables
from dotenv import load_dotenv, find_dotenv
import os
# encoding
import json
import base64
# api
import requests

####################################################
#####################SPOTIFY########################
####################################################

# Load in env variables from .env file
load_dotenv()

# Returns authorization header
def get_auth_header(token):
    return {"Authorization": f"Bearer {token}"}

# Returns API token
def get_token():
    url = "https://accounts.spotify.com/api/token"
    request_body = {
        "grant_type": "refresh_token",
        "refresh_token": os.getenv("REFRESH_TOKEN"),
        "client_id": os.getenv("CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET"),
    }

    try:
        response = requests.post(url, data=request_body)
        new_token_info = response.json()

    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh.args[0]}")

    return new_token_info['access_token']

####################################################
#####################BIG QUERY######################
####################################################

def get_keyfile():
    # fetch encoded credentials    
    load_dotenv(find_dotenv())
    encoded_key = os.getenv("GOOGLE_SERVICE_ACCOUNT_KEY")

    # decode
    service_account_json = json.loads(base64.b64decode(encoded_key).decode('utf-8'))
    return service_account_json
