import boto3

def new_aws_session(target_account: str):
    """This function creates a Boto3 session for access to the API."""

    sts_client = boto3.client("sts")
    caller_identity: dict = sts_client.get_calleer_identity()
    caller_identity_account: str = caller_identity["Account"]
    ian_role_name: str = caller_identity["Arn"].split("/")[1]
    try:
        if caller_identity_account != target_account:
            role_arn: str = "arn:aws:iam::[0]:role/{1}".format(target_account, iam_role_name)
            response: dict = sts_client.assume_role(
                RoleArn=role_arn, 
                RoleSessionName=target_account
            )
            session = boto3.Session(
                aws_access_key_id = response["Credentials"]["AccessKeyId"],
                aws_secret_access_key = response["Credentials"]["SecretAccessKey"],
                aws_session_token = response["Credentials"]["SessionToken"]
            )
            return session
        return boto3.Session()
    except BaseException as error:
        print(str(error))
        raise error