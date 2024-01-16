"""
Synopsis:
    Lambda function for creating, modifying and deleting AWS Transfer Family users from SFTP servers.

Description:
    This script does the following:
        1) Takes in a payload sent from the ServiceNow AWS SFTP request form through API Gateway for the following potential actions:
            - Create a new Transfer Family user.
            - Modify an existing user's public SSH key.
            - Modify an existing user's username.
            - Delete a user from Transfer Family.
        2) A response is returned to the API Gateway which is used to determine if the request was successful or a failure.

Parameters:
    The following parameters are used from the payload:
        1) servicenow_request_number: Request Item number associated with the AWS SFTP Request Form.
        2) request_type: Determines which action is to be performed regarding the user:
            - create_user: Creates a new Transfer Family user.
            - update_ssh_key: Modifys an existing user's public SSH key.
            - update_user_name: Modifys an existing user's username.
            - delete_user: Deletes a user from Transfer Family.
        3) user_name: Username for Transfer Family user.
        4) access_level: Determines the level of confidentiality the user will be sharing data wise:
            - class1: The Class 1 access level determines this users data will contain PII (Personally Identifiable Information).
            - standard: THe Standard access level determines this users data will not contain PII.
        5) ssh_key: Public SSH key used for authenticating a Transfer Family user.
        6) ip_range: IP range Transfer Family user will be logging in from.
        7) dr_ip_range: Failover IP range Transfer Family user can use to log in from.
        8) new_user_name: Username if modification of existing Transfer Family username is requested.
    
    Payload example:

    Create a Transfer Family user:
    {"servicenow_request_number": "RITM0222222",
    "request_type": "create_user",
    "user_name": "Peter",
    "access_level": "standard",
    "ssh_key": "ssh-rsa #############################"}
            
Reference Materials:
    https://aws.amazon.com/aws-transfer-family/
    https://aws.amazon.com/dynamodb/
    https://aws.amazon.com/s3/
    https://aws.amazon.com/api-gateway/
    https://www.servicenow.com/
    
Notes:  
    Version 1.0 Developer: Peter Hardy
    Version 1.0 Date: 08/01/23
"""

import json
from datetime import date, datetime, timedelta

import boto3

from sftp_user_manager import *

def lambda_handler(event, context) -> dict:
    """Main lambda function for maintaining AWS Transfer Family users for SFTP."""
    