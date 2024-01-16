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
                    dr_ip_range: str = None,
                    new_user_name: str = None) -> dict
    3) create_user_configs(user_name: str,
                    access_level: str,
                    ssh_key: str,
                    servicenow_request_number: str,
                    ip_range: str = None,
                    dr_ip_range: str = None,
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
primary_region: str = os.getenv("PRIMARY_REGION")
primary_sftp_s3_bucket: str = os.getenv("PRIMARY_SFTP_S3_BUCKET")
user_table_name: str = os.getenv("USER_TABLE_NAME")
class1_role_arn: str = os.getenv("CLASS1_ROLE_ARN")
sns_topic_arn: str = os.getenv("SNS_TOPIC_ARN")
standard_role_arn: str = os.getenv("STANDARD_ROLE_ARN")
dynamodb_client = os.getenv("DYNAMODB_CLIENT")
s3_client = os.getenv("S3_CLIENT")
sns_client = os.getenv("SNS_CLIENT")
transfer_client = os.getenv("TRANSFER_CLIENT")
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


def create_user(user_name: str, access_level: str, ssh_key: str,
                servicenow_request_number: str, ip_range: str = None,
                dr_ip_range: str = None, new_user_name: str = None) -> dict:
    """This function creates a new Transfer Family user for the SFTP server."""
    user_name_response: dict = check_user_store(user_name)

    if "Item" in user_name_response:
        result: str = f"({datetime.now()})  -  {user_name} is already in the SFTP user store."
        print(result)
        if new_user_name is not None:
            print(f"({datetime.now()})  -  New folder location will be created for {new_user_name}.")
            user_details: dict = user_name_response.get("Item")
            access_level: str = user_details["access_level"]["S"]
            ssh_key: str = user_details["ssh_key"]["S"]
            if user_details.get("ip_range") is not None:
                ip_range: str = user_details["ip_range"]["S"]
            
            create_user_configs(new_user_name, access_level, ssh_key, servicenow_request_number, ip_range, dr_ip_range, user_name)
            result: str = f"({datetime.now()})  -  Success! {servicenow_request_number} to update {user_name} to {new_user_name} has been completed."
            print(result)
            print("******************************************************************************************************")

            result_body: dict {
                "status_code": 200,
                "result": result
            }
            return result_body
        print("******************************************************************************************************")
        
        result_body: dict = {
            "status_code": 400,
            "result": result
        }
        subject: str = "SFTP User name Provided Already Exists"
        sns_client.publish(
            TopicArn=sns_topic_arn,
            Message=json.dumps({"default": json.dumps(result_body)}),
            Subject=subject,
            MessageStructure="json"
        )
        return result_body
    
    print(f"({datetime.now()})  -  {user_name} does not exist in the DynamoDB useer table.")
    print(f"({datetime.now()})  -  New Transfer Family user {user_name} will be created for SFTP server.")
    create_user_configs(user_name, access_level, ssh_key, servicenow_request_number, ip_range, dr_ip_range)
    result: str = "({datetime.now()})  -  Success {servicenow_request_number} to create new user {user_name} has been completed."
    print(result)
    print("******************************************************************************************************")

    result_body: dict = {
        "status_code": 200,
        "result": result
    }
    return result_body


def create_user_configs(user_name: str, access_level: str, ssh_key: str,
                    servicenow_request_number: str, ip_range: str = None,
                    dr_ip_range: str = None, new_user_name: str = None) -> dict:
    """This function determines the details for when creating a new Transfer Family usere for SFTP."""
    print("******************************************************************************************************")
    print(f"({datetime.now()})  -   Setting user configurations for adding {user_name} to the SFTP server.")

    role_arn: str = class1_role_arn if access_level == "class1" else standard_role_arn

    dynamodb_client.put_item(
        TableName=user_table_name,
        Item={
            "user_name": {"S": user_name},
            "access_level": {"S": access_level},
            "role_arn": {"S": role_arn},
            "ssh_key": {"S": ssh_key},
            "ip_range": {"S": str(ip_range)},
            "dr_ip_range": {"S": str(dr_ip_range)},
            "creation_date": {"S": f"{datetime.now()}"},
            "user_name": {"S": servicenow_request_number}
        }
    )
    print(f"({datetime.now()})  -   New Transfer Family user {user_name} has been added to the DynamoDB user table.")
    create_user_folder(user_name, access_level)
    print(f"({datetime.now()})  -   Adding {user_name} to the SFTP server.")
    server_id: str = server_id_dict[primary_region]
    transfer_client.create_user(
        HomeDirectoryType="LOGICAL",
        HomeDirectoryMappings=[
            {
                "Entry": f"/",
                "Target": f"/{primary_sftp_s3_bucket}/{access_level.upper()/{user_name}}"
            }
        ],
        Role=role_arn,
        ServerId=server_id,
        SshPublicKeyBody=ssh_key,
        UserName=user_name
    )
    print(f"({datetime.now()})  -   Transfer Family user {user_name} has been added to the SFTP server.")
    print("******************************************************************************************************")


def create_user_folder(user_name: str, access_level: str) -> None:
    """This function creates new folders for a Transfer Family user in the primary S3 SFTP bucket."""
    print("******************************************************************************************************")
    print(f"({datetime.now()})  -   Creating folder structure for {user_name}.")
    user_folder: str = f"{access_level.upper()}/{user_name}"
    user_in_folder: str = f"{access_level.upper()}/{user_name}/IN/"
    user_out_folder: str = f"{access_level.upper()}/{user_name}/OUT/"

    s3_client.put_object(
        Bucket=primary_sftp_s3_bucket,
        Key=user_folder
    )
    s3_client.put_object(
        Bucket=primary_sftp_s3_bucket,
        Key=user_in_folder
    )
    s3_client.put_object(
        Bucket=primary_sftp_s3_bucket,
        Key=user_out_folder
    )
    print(f"({datetime.now()})  -   Folder structure for {user_name} completed.")
    print("******************************************************************************************************")


