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
sts_client = session.client("secretsmanager", region_name=region)


def lambda_handler(event: dict, context: dict) -> None:
    pass