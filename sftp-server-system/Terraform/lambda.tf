provider "aws" {
    region = var.region
}

resource "aws_lambda_function" "sftp_user_creation_lambda_function" {
    function_name = "${var.resource_name}-${var.aws_environment}-${var.region_prefix}-user-creation-lambda"
    role = data.terraform_remote_state.sftp_admin_role.outputs.sftp_admin_role_arn
    description = "Lambda function used for creating and modifying Transfer Family SFTP users"
    runtime = "python3.12"
    s3_bucket = var.sftp_s3_bucket
    s3_key = "sftp-user-creation/sftp-user-creation.zip"
    timeout = 15

    vpc_config {
      subnet_ids = data.aws_vpcs.sftp_subnets.ids
      security_group_ids = data.aws_vpcs.sftp_security_groups.ids
    }
}

resource "aws_lambda_permission" "sftp_lambda_api_gateway_permission" {
    action = "lambda:InvokeFunction"
    function_name = aws_lambda_function.sftp_user_creation_lambda_function.function_name
    principal = "apigateway.amazonaws.com"
    source_arn = "arn:aws:execute-api:${var.region}:${var.aws_account_id}:${aws_api_gateway_rest_api.sftp_api_gateway.id}/Dev/POST/sftp"
}