"""
Synopsis:
    This script is only ever to be run in the event that all of the users an SFTP server have been lost or need to be repopulated.

Description:
    This script is used in the event that the Transfer Family SFTP users have been deleted unintentionally.
    To run the script:
        1) Federate into the AWS account where the SFTP server is hosted.
        2) Run the script.

    There are 2 functions that are used to run this script:

    1) list_users(user_table_name:str) -> list
       This function scans the DynamoDB user table and retrieves all items (users) and their details.
    
    2) create_user() -> None
       This functions uses the DynamoDB user table to recreate all users on the SFTP server.

Reference Materials:
    https://docs.aws.amazon.com/transfer/latest/userguide/service-managed-users.html

Notes:
    Version 1.0 Developer: Peter Hardy
    Version 1.0 Date: 07/01/2023
"""

import json
from datetime import date, datetime, timedelta
import os

import boto3
from dotenv import load_dotenv

from sftp_server_manager import list_servers


def list_users(user_table_name: str) -> list:
    """This function takes in the DynamoDB user table name and returns a list of user data"""
    user_store_response: dict = dynamodb_client.scan(TableName=user_table_name)
    users: list = user_store_response.get("Items")
    return users


def create_users() -> None:
    users_list: list = list_users(user_table_name)
    server_id: str = server_id_dict[primary_region]
    for user in users_list:
        user_name: str = user["user_name"]["S"]
        ssh_key: str = user["ssh_key"]["S"]
        access_level: str = user["access_level"]["S"]

        role_arn: str = class1_role_arn if access_level == "class1" else standard_role_arn

        transfer_client.create_user(
            HomeDirectoryType="LOGICAL",
            HomeDirectoryMappings=[
                {
                    "Entry": f"/",
                    "Target": f"/{primary_sftp_s3_bucket}/{access_level.upper()}/{user_name}"
                }
            ],
            Role=role_arn,
            ServerId=server_id,
            SshPublicKeyBody=ssh_key,
            UserName=user_name
        )
        print(f"User {user_name} has been added to the Transfer Family SFTP server {server_id} in the (primary_region) region.")
    print("This user restore process for the Transfer Family SFTP server {server_id} has been completed.")


if __name__ == "__main__":
    load_dotenv()

    dynamodb_client = os.getenv("DYNAMODB_CLIENT")
    transfer_client = os.getenv("TRANSFER_CLIENT")
    primary_region: str = os.getenv("PRIMARY_REGION")
    user_table_name: str = os.getenv("USER_TABLE_NAME")
    primary_sftp_s3_bucket: str = os.getenv("PRIMARY_SFTP_S3_BUCKET")
    class1_role_arn: str = os.getenv("CLASS1_ROLE_ARN")
    standard_role_arn: str = os.getenv("STANDARD_ROLE_ARN")

    server_id_dict: dict = list_servers()
    create_users()