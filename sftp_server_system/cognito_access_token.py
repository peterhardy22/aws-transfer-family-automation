"""
Synopsis:
    This script can be used to retrieve the access token from a specified Cognito user pool.

Description:
    This script is used for testing a Cognito user pool with the following steps:
        1) Federate into the correct AWS account.
        2) Input the user pool client id for the client_id variable.
        3) Input the user pool client key for the secret_key variable.
        4) Run the script.

Reference Materials:
    https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-user-identity-pools.html

Notes:
    Version 1.0 Developer: Peter Hardy
    Version 1.0 Date: 06/01/2023
"""

import json
import random
import time
import token

import requests
from requests.auth import HTTPBasicAuth


cognito_url: str = "https://dev-ue2-servicenow.auth.us-east-2.amazoncognito.com/oauth2/token"

# Needs to be populated before running this script.
client_id: str = ""
secret_key: str = ""

headers: dict = {"Content-type": "application/x-www-form-urlencoded"}
cognito_parameters: dict = {
    "grant_type": "client_credentials",
    "client_id": client_id
}

cognito_token: str = requests.post(
    url=cognito_url,
    params=cognito_parameters,
    headers=headers,
    auth=(client_id, secret_key)
)
token_json: dict = cognito_token.json()
access_token: str = f"Bearer {token_json["access_token"]}"
print(access_token)