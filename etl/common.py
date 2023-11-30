# environment variables
from dotenv import load_dotenv
import dotenv
import os
# api
import requests

# Load in env variables from .env file
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
refresh_token = os.getenv("REFRESH_TOKEN")
expires_at = os.getenv("EXPIRES_AT")


# Returns authorization header
def get_auth_header(token):
    return {"Authorization": f"Bearer {token}"}

# Returns API token
def get_token():
    url = "https://accounts.spotify.com/api/token"
    request_body = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }

    response = requests.post(url, data=request_body)
    new_token_info = response.json()

    dotenv_file = dotenv.find_dotenv()
    dotenv.load_dotenv(dotenv_file)

    os.environ["ACCESS_TOKEN"] = new_token_info['access_token']

    # Write changes to .env file.
    dotenv.set_key(dotenv_file, "ACCESS_TOKEN", os.environ["ACCESS_TOKEN"])

    return new_token_info['access_token']