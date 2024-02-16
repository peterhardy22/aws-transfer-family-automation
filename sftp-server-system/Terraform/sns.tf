provider "aws" {
    region = var.region
}

resource "aws_sns_topic" "sftp_sns_topic" {
    name = "${aws_lambda_function.sftp_user_creation_lambda_function.function_name}-sns-error-topic"
}

resource "aws_sns_topic_subscription" "sftp_sns_topic_subscription" {
    endpoint = "help@help.com"
    protocol = "email"
    topic_arn = aws_sns_topic.sftp_sns_topic.arn
}