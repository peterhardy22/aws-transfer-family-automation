"""
Synopsis:
    This is the script used for retrieving the SFTP sevrer details for the sftp-user-creation Lambda function.

Description:
    This script is used in conjunction with the lambda_function.py script:
        1) Uses Boto3 to make a call to Transfer Family based on the AWS account and region.
        2) Retrieves the SFTP server id.
        3) REturns a dictionary storing the region and server id.

        Example of output: {'us-east-2': 's-0123abcd45ef6g7h8'}

Reference Materials:
    https://docs.aws.amazon.com/transfer/latest/userguide/configuring-servers.html

Notes:
    Version 1.0 Developer: Peter Hardy
    Version 1.0 Date: 07/01/2023
"""


from dotenv import load_dotenv
import os
import boto3

load_dotenv()
primary_region: str = os.getenv("PRIMARY_REGION")
transfer_client: str = os.getenv("TRANSFER_CLIENT")

def list_servers() -> dict:
    """This function checks AWS Transfer Family for serevers and reeturns the server id in a dictionary with its corresponding region as the key."""
    server_id_dict: dict = {}
    try:
        server_response: dict = transfer_client.list_servers()
        servers_list: list = server_response["Servers"]
        for server_id in servers_list:
            server_id: str = server_id.get("ServerId")
            server_id_dict[primary_region] = server_id
    except:
            print(f"There are not any listed servers in the region {primary_region}.")
    
    return server_id_dict