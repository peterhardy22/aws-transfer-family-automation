"""
Synopsis:
    This script holds an assortment of functions that allow you to create, modify and delete AWS Transfer Family SFTP server users.

Description:
    The following functions and their parameters populate the script below:

    1) check_user_store(user_name: str) -> dict
    2) create_user(user_name: str,
                    access_level: str,
                    ssh_key: str,
                    servicenow_request_number: str,
                    ip_range: str = None,
                    dr_ip_range: str = None
                    new_user_name: str = None) -> dict
    3) create_user_configs(user_name: str,
                    access_level: str,
                    ssh_key: str,
                    servicenow_request_number: str,
                    ip_range: str = None,
                    dr_ip_range: str = None
                    new_user_name: str = None) -> dict
    4) create_user_folder(user_name: str, access_level: str) -> None
    5) update_ssh_key(user_name: str, ssh_key: str, servicenow_request_number: str) -> dict
    6) delete_user(user_name: str, servicenow_request_number: str) -> dict

Reference Material:
    https://docs.aws.amazon.com/transfer/latest/userguide/create-user.html

Notes:
    Version 1.0 Developer: Peter Hardy
    Version 1.0 Date: 07/01/2023
"""


from datetime import date, datetime, timedelta
from dotenv import load_dotenv
import json
import os
import sys

import boto3
import botocore.exceptions

from sftp_server_manager import list_servers


load_dotenv()
dynamodb_client: str = os.getenv("DYNAMODB_CLIENT")
user_table_name: str = os.getenv("USER_TABLE_NAME")
server_id_dict: dict = list_servers()


def check_user_store(user_name: str) -> dict:
    """This function checks if the user_name provided already exists in the DynamoDB user table.
    Returns a dictionary that lists the details of that user: access level, public ssh key, role arn, creation date, ip range and dr ip range."""
    print(f"({datetime.now()})  -  Checking if {user_name} is already in the SFTP user store.")

    user_name_response: dict = dynamodb_client.get_item(
        TableName=user_table_name,
        Key={
            "user_name": {"S": user_name}
        }
    )
    return user_name_response

