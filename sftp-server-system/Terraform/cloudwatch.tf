provider "aws" {
    region = var.region
}

resource "aws_cloudwatch_log_group" "sftp_user_creation_lambda_log_group" {
    name = "/aws/lambda/${aws_lambda_function.sftp_user_creation_lambda_function.function_name}"
    retention_in_days = 545

    depends_on = [aws_lambda_function.sftp_user_creation_lambda_function]
}

