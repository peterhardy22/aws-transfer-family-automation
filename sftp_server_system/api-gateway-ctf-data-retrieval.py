"""
Synopsis:
    This script is only ever to be run during the CloudFormation deployment of the SFTP server system.

Description:
    This script is used after running the sftp-api-gateway-cloudformation.yml template to auto populate the following Parameters
    in the sftp-api-gateway-configs-cloudformation.yml template:

    1) pAPIGatewayID : API Gateway ID used for ServiceNow integration.
    2) pAPIGatewayRootResourceId: API Gateway's Root Resource Id used for the ParentId.
    3) pAPIGatewayAuthorizerId: Authorizer identifier for Cognito.
    4) pSFTPUserCreationLambdaArn: ARN of sftp-user-creation Lambda function.

Reference Materials:
    https://aws.amazon.com/aws-transfer-family/    

Notes:
    Version 1.0 Developer: Peter Hardy
    Version 1.0 Date: 06/01/2023
"""

from datetime import datetime
from pathlib import Path
from typing import List, Tuple

from mailer import Mailer, Message

import boto3
from ruamel.yaml import YAML


def api_gateway_data_retrieval() -> str:
    """This function retrieves the API Gateway Id, Authorizer Id and Resouce Root Id."""
    api_client = boto3.cleint("apigateway")
    api_response: dict = api_client.get_rest_apis()
    rest_apis_list: list = api_response["items"]
    
    for rest_api in rest_apis_list:
        if rest_api["name"] == "dev-ue2-servicenow-api-gateway":
            api_gateway_id: str = rest_api["id"]
    
    api_authorizers_response: dict = api_client.get_authorizers(
        restApiId=api_gateway_id
    )
    authorizer_id: str = api_authorizers_response["items"][0]["id"]
    
    api_resources_response: dict = api_client.get_resources(
        restApiId=api_gateway_id
    )
    resource_root_id: str = api_resources_response["items"][0]["id"]

    return api_gateway_id, authorizer_id, resource_root_id


def lambda_arn_retrieval() -> str:
    lambda_client = boto3.cleint("lambda")
    lambda_response: dict = lambda_client.get_function(
        FunctionName="dev-ue2-transfer-family-sftp-user-creation"
    )
    sftp_user_lambda_arn: str = lambda_response["Configuration"]["FunctionArn"]

    return sftp_user_lambda_arn


def write_to_yaml(api_gateway_id: str, authorizer_id: str, resource_root_id: str, sftp_user_lambda_arn: str) -> None:
    """This function takes in 3 Id's for API Gateway then adds them to a CloudFormation YAML template."""
    path = Path("sftp-api-gateway-configs-cloudformation.yml")
    yaml = YAML()

    yaml_data: dict = yaml.load(path)
    parameters: dict = yaml_data["Parameters"]
    parameters["pAPIGatewayId"]["Default"] = api_gateway_id 
    parameters["pAPIGatewayRootResourceId"]["Default"] = resource_root_id
    parameters["pAPIGatewayAuthorizerId"]["Default"] = authorizer_id
    parameters["pSFTPUserCreationLambdaArn"]["Default"] = sftp_user_lambda_arn
    
    yaml.dump(yaml_data, path)


def email_aws_details(api_gateway_id: str) -> Tuple[str, str, List[str]]:
    """This function sends an email containing the data it retrieved and added to the CloudFormation YAML template."""
    email_from = "sftp.deployment@development.com"
    email_list = ["snow@development.com"]
    
    cognito_client = boto3.client("cognito-idp")
    user_pools_response: dict = cognito_client.list_user_pools(
        MaxResults=25
    )
    user_pools_list: list = user_pools_response["UserPools"]
    for user_pool in user_pools_list:
        if user_pool["Name"] == "dev-ue2-sftp-cognito-userpool-servicenow":
            user_pool_id: str = user_pool["Id"]

    user_pool_clients_response: dict = cognito_client.list_user_pool_clients(
        UserPoolId=user_pool_id
    )
    user_pool_clients_list: list = user_pool_clients_response["UserPoolClients"]
    for user_pool_client in user_pool_clients_list:
        if user_pool_client["ClientName"] == "servicenow-dev":
            client_id: str = user_pool_client["ClientId"]
    
    user_pool_client_response: dict = cognito_client.describe_user_pool_client(
        UserPoolId=user_pool_id,
        ClientId=client_id
    )
    client_secret: str = user_pool_client_response["UserPoolClient"]["ClientSecret"]

    today= datetime.now()
    message = Message(From=email_from, To=email_list, charset="utf-8")
    message.Subject = "New ServiceNow API Gateway & Cognito Details for ITSM Integration"
    message.Html = """<html>
    <a>ServiceNow API Gateway</a>
    <h2>ServiceNow API Gateway Deployment<span style="color:red;">Alert</span> @ {today}</h3>
    <br/>
    <h3>The following details should be used for the backend integration of the ServiceNow AWS SFTP Request form: <br/></h4>
    <h4>1.)     Endpoint URL for the dev-ue2-sftp-api-gateway-servicenow API Gateway: vpce-#################.execute-api.us-east-2.vpce.amazonaws.com<br/></h4>
    <h4>2.)     API Gateway Resource Endpoint: DEV/sftp<br/></h4>
    <h4>3.)     Authentication URL: https://dev-ue2-servicenow.auth,us-east-2.amazoncognito.com<br/></h4>
    <h4>4.)     API Gateway Id: {api_gateway_id}<br/></h4>
    <h4>5.)     Client Id: {client_id}<br/></h4>
    <h4>6.)     Client Secret: {client_secret}<br/></h4>
    </html>
    """.format(today=today, api_gateway_id=api_gateway_id, client_id=client_id, client_secret=client_secret)
    sender = Mailer("process-automation.loc")
    sender.send(message)

    return client_id, client_secret, email_list


if __name__ == "__main__":
    api_gateway_id, authorizer_id, resource_root_id = api_gateway_data_retrieval()
    sftp_user_lambda_arn = lambda_arn_retrieval()

    write_to_yaml(api_gateway_id, authorizer_id, resource_root_id, sftp_user_lambda_arn)
    email_aws_details(api_gateway_id)