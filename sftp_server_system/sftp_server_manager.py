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
import boto3


def list_servers() -> dict:
    pass