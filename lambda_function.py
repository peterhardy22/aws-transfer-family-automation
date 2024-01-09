from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
import json
import os
import requests
import socket
import smb
import sys
import time

from smb.SMBConnection import SMBConnection
from awsaccess import new_aws_session
from orchestrationcredentials import get_secret, login, order_job

try:
    from requests.packages.urlib3,exceptions import InsecureRequestWarning
except:
    from urllib3.exceptions import InsecureRequestWarning
    import urllib3


session = new_aws_session(os.environ["ACCOUNT_NUMBER"])
orchestration_secret_name: str = os.environ["ORCHESTRATION_SECRET"]
sftp_secret_name: str = os.environ["SFTP_SECRET"]
sftp_table_name: str = os.environ["SFTP_TABLE_NAME"]
region: str = os.environ["AWS_REGION"]

dynamodb_resource = session.resource("dynamodb", region_name=region)
dynamodb_table_resource = dynamodb_resource.Table(sftp_table_name)
s3_resource = session.resource("s3")
s3_client = session.client("s3")
sns_client = session.client("sns")
sts_client = session.client("secretsmanager", region_name=region)


def lambda_handler(event: dict, context: dict) -> None:
    """This Lambda function is used to determine what to do with any file (object) that is transfered over AWS SFTP.
    Determined by the account_name and file_name, a DynamoDB table is used to reference the logistics for the files endpoint.
    The main current endpoint possibilities:
        - Local file share
        - S3 bucket
        - Orchestration tool to handle processing of file internally.
    """
    print(f"Event Payload: {event}")

    object_key: str = event["Records"][0]["s3"]["object"]["key"]
    object_key_list: list = object_key.split("/")
    object_partial_source_path: str = "/".join(object_key_list[:-1])

    account_name: str = object_key_list[1]
    event_file_name: str = object_key_list[-1]
    source_bucket_name: str = event["Records"][0]["s3"]["bucket"]["name"]
    object_source_path: str = fr"s3://{source_bucket_name}/{object_partial_source_path}/"

    try:
        dynamodb_response: dict = dynamodb_table_resource.query(
            KeyConditionExpression=Key("account_name").eq(account_name)
        )
        account_logistics_list: list = dynamodb_response["Items"]
    except ClientError as error:
        print(f"The following error occurred when querying DynamoDB: {error}")
        if error.response["Error"]["Code"] == "ProvisionedThroughputExceededException":
            raise error
        if error.response["Error"]["Code"] == "ResourceNotFoundException":
            raise error
        if error.response["Error"]["Code"] == "RequestLimitExceeded":
            raise error
        if error.response["Error"]["Code"] == "InternalServerError":
            raise error
        sys.exit(1)
    
    job_logistics_list: list = []

    for account_logistic in account_logistics_list:
        prefix: str = account_logistic.get("file_name_prefix")
        suffix: str = account_logistic.get("file_name_suffix")

        if event_file_name == account_logistic.get("file_name") and object_source_path == account_logistic.get("source"):
            job_logistics_list.append(account_logistic)
        if prefix != None and prefix != "" and event_file_name.startswith(prefix):
            account_logistic["file_name"] = event_file_name
            job_logistics_list.append(account_logistic)
        if suffix != None and suffix != "" and event_file_name.endswith(suffix):
            account_logistic["file_name"] = event_file_name
            job_logistics_list.append(account_logistic)
        if prefix == "*" and object_source_path == account_logistic.get("source"):
            account_logistic["file_name"] = event_file_name
            job_logistics_list.append(account_logistic)
        
