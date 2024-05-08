# environment variables
from dotenv import load_dotenv
import dotenv
import os
# api
import requests

####################################################
#####################SPOTIFY########################
####################################################

# Load in env variables from .env file
load_dotenv()

# client_id = os.getenv("CLIENT_ID")
# client_secret = os.getenv("CLIENT_SECRET")
# access_token = os.getenv("ACCESS_TOKEN")
# refresh_token = os.getenv("REFRESH_TOKEN")
# expires_at = os.getenv("EXPIRES_AT")


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

    response = requests.post(url, data=request_body)
    new_token_info = response.json()

    dotenv_file = dotenv.find_dotenv()
    dotenv.load_dotenv(dotenv_file)

    print(f"Access token in JSON file: {new_token_info}")

    os.getenv["ACCESS_TOKEN"] = new_token_info['access_token']

    # Write changes to .env file.
    dotenv.set_key(dotenv_file, "ACCESS_TOKEN", os.environ["ACCESS_TOKEN"])

    return new_token_info['access_token']

####################################################
#####################BIG QUERY######################
####################################################

def get_keyfile():
    variables_keys = {
        "type": os.getenv("TYPE"),
        "project_id": os.getenv("PROJECT_ID"),
        "private_key_id": os.getenv("PRIVATE_KEY_ID"),
        "private_key": os.getenv("PRIVATE_KEY"),
        "client_email": os.getenv("CLIENT_EMAIL"),
        "client_id": os.getenv("BQ_CLIENT_ID"),
        "auth_uri": os.getenv("AUTH_URI"),
        "token_uri": os.getenv("TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("AUTH_PROVIDER_X509_CERT_URL"),
        "client_x509_cert_url": os.getenv("CLIENT_X509_CERT_URL"),
        "universe_domain": os.getenv("UNIVERSE_DOMAIN")
    }
    return variables_keys
