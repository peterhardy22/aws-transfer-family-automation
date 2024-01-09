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
smb_secret_name: str = os.environ["SFTP_SECRET"]
sftp_table_name: str = os.environ["SFTP_TABLE_NAME"]
sns_topic_arn: str = os.environ["SNS_TOPIC_ARN"]
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
    source_s3_bucket_name: str = event["Records"][0]["s3"]["bucket"]["name"]
    object_source_path: str = fr"s3://{source_s3_bucket_name}/{object_partial_source_path}/"

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
        
    if len(job_logistics_list) == 0:
        result_body: str = f"The file {event_file_name} does not exist in the logistics table for account_name: {account_name}."
        subject: str = f"AWS SFTP Logistics Lambda: {event_file_name} does not have logistics set up."
        sns_client.publish(
            TopicArn=sns_topic_arn,
            Message=json.dumps({"default": json.dumps(result_body)}),
            Subject=subject,
            MessageStructure="json"
        )
        sys.exit(1)

    for job_logistic in job_logistics_list:
        try:
            destination: str = job_logistic.get("destination")
            file_name: str = job_logistic.get("file_name")
            folder_name: str = job_logistic.get("folder_name")
            job_name: str = job_logistic["job_name"]
            new_file_name: str = job_logistic.get("new_file_name")
            server_name_list: list = job_logistic["server_name"].strip("][").split(", ")
            source: str = job_logistic["source"]
        except:
            result_body: str = f"The file {file_name} does not exist in the logistics table for account_name: {account_name}."
            subject: str = f"AWS SFTP Logistics Lambda: {file_name} does not have logistics set up."
            sns_client.publish(
                TopicArn=sns_topic_arn,
                Message=json.dumps({"default": json.dumps(result_body)}),
                Subject=subject,
                MessageStructure="json"
            )
            break

        if new_file_name is not None and new_file_name != "":
            file_name: str = new_file_name
        
        if folder_name is None and destination is None or folder_name == "" and destination == "" \
            or folder_name == "" and destination is None or folder_name is None and destination == "":
              result_body: str = f"The logistic in the table for file {file_name} is incomplete due to either the destination or folder_name value being empty."
              subject: str = f"AWS SFTP Logistics Lambda: {file_name} logistic is incomplete."
              sns_client.publish(
                  TopicArn=sns_topic_arn,
                  Message=json.dumps({"default": json.dumps(result_body)}),
                  Subject=subject,
                  MessageStructure="json"
              )
              break
        
        source_split: list = source.split("/")
        source_key: str = ("/").join(source_split[3::])
        destination_split: list = destination.split("/")

        if destination.startswith("s3://"):
            destination_s3_bucket_name: str = destination_split[2]
            partial_destination_key: str = ("/").join(destination_split[3::])
            destination_key: str = f"{partial_destination_key}{file_name}"

            copy_source: dict = {
                "Bucket": source_s3_bucket_name,
                "Key": f"{source_key}{event_file_name}"
            }
            try:
                s3_resource.meta.client.copy(copy_source, destination_s3_bucket_name, destination_key)
                print(f"File {file_name} was successfully placed in destination: {destination}.")
            except:
                result_body: str = f"An issue occured and the {file_name} was not able to be copied and placed into the S3 bucket destination: {destination}."
                subject: str = f"AWS SFTP Logistics Lambda: {file_name} could not be copied to another S3 bucket."
                sns_client.publish(
                    TopicArn=sns_topic_arn,
                    Message=json.dumps({"default": json.dumps(result_body)}),
                    Subject=subject,
                    MessageStructure="json"
                )
                break
        else:
            first_level_destination: str = destination_split[4]
            second_level_destination: str = ("//").join(destination_split[5::])

            if not os.path.isfile(f"/tmp/{event_file_name}"):
                print(f"Downloading {event_file_name} from SFTP S3 bucket.")
                s3_resource.meta.client.download_file(source_s3_bucket_name, f"{source_key}{event_file_name}", fr"/tmp/{event_file_name}")
                print(f"Finished downloading {event_file_name} from SFTP S3 bucket.")
            else:
                print(f"{event_file_name} already exists in Lambda function tmp folder.")

        if folder_name is not None and folder_name != "" and destination is not None:
            try:
                requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
            except:
                urllib3.disable_warnings(InsecureRequestWarning)
            
            orchestration_user_name, orchestration_pswd = get_secret(sts_client, orchestration_secret_name)
            orchestration_base_url: str = os.environ["ORCHESTRATION_BASE_URL"]
            token: str = login(orchestration_base_url, orchestration_user_name, orchestration_pswd)
            print("Ensuring file is in destination before ordering orchestration tool workflow.")
            time.sleep(2)
            status_code: str = order_job(orchestration_base_url, token, folder_name)

            if status_code == 200:
                print(f"The orchestration tool workflow {folder_name} has been ordered.")
                break
            else:
                print(status_code)
                result_body: str = f"An issue occured when trying to order the workflow in the orchestration tool for {folder_name}."
                subject: str = f"AWS SFTP Logistics Lambda: {folder_name} worklflow error in orchestration tool."
                sns_client.publish(
                    TopicArn=sns_topic_arn,
                    Message=json.dumps({"default": json.dumps(result_body)}),
                    Subject=subject,
                    MessageStructure="json"
                )
                break
        
        smb_user_name, smb_pswd = get_secret(sts_client, smb_secret_name)
        local_machine_name: str = os.environ["LOCAL_MACHINE_NAME"]
        domain: str = os.environ["DOMAIN"]

        for server_machine_name in server_name_list:
            try:
                conn = SMCConnection(smb_user_name, smb_pswd, server_machine_name,
                                     local_machine_name, domain=domain, use_ntlm_v2=True,
                                     is_direct_tcp=True)
                
                server_ip: str = socket.gethostbyname(server_machine_name)
                conn.connect(server_ip, 445)
            except:
                result_body: str = f"An issue occured with the SMB connection to server: {server_machine_name} and therefore the file {file_name} was not able to be moved."
                subject: str = f"AWS SFTP Logistics Lambda: {file_name} could not be copied to local file share."
                sns_client.publish(
                    TopicArn=sns_topic_arn,
                    Message=json.dumps({"default": json.dumps(result_body)}),
                    Subject=subject,
                    MessageStructure="json"
                )
                break
            try:
                file_object = open(fr"/tmp/{event_file_name}", "rb")
                print(f"Beginning copy of file {file_name} to file share {server_machine_name}.")
                conn.storeFile(first_level_destination, f"{second_level_destination}\{file_name}", file_object)
                conn.close()
                print(f"File {file_name} was successfully placed in destination: {destination}.")
            except:
                result_body: str = f"An issue occured inside the SMB connection to server: {server_machine_name} and therefore the file {file_name} was not able to be moved."
                subject: str = f"AWS SFTP Logistics Lambda: {file_name} could not be copied to local file share."
                sns_client.publish(
                    TopicArn=sns_topic_arn,
                    Message=json.dumps({"default": json.dumps(result_body)}),
                    Subject=subject,
                    MessageStructure="json"
                )

    s3_client.delete_object(
        Bucket=source_s3_bucket_name,
        Key=object_key
    )
    print(f"The file {event_file_name} has been removed from the SFTP s3 bucket.")