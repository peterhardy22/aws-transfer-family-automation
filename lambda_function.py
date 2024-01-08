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
