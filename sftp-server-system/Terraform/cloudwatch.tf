provider "aws" {
    region = var.region
}

resource "aws_cloudwatch_log_group" "sftp_user_creation_lambda_log_group" {
    name = "/aws/lambda/${aws_lambda_function.sftp_user_creation_lambda_function.function_name}"
    retention_in_days = 545

    depends_on = [aws_lambda_function.sftp_user_creation_lambda_function]
}

resource "aws_cloudwatch_metric_alarm" "sftp_user_creation_lambda_error_alarm" {
  alarm_name          = "${aws_lambda_function.sftp_user_creation_lambda_function.function_name}-cloudwatch-alarm"
  comparison_operator = "GreaterThanOrEqualToThreshold"
  evaluation_periods  = 1
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 120
  statistic           = "Sum"
  threshold           = 1
  treat_missing_data  = "notBreaching"
  alarm_description   = "Alarm triggered when Lambda function encounters errors"
  alarm_actions       = [aws_sns_topic.sftp_sns_topic.arn]
  dimensions = {
    FunctionName = aws_lambda_function.sftp_user_creation_lambda_function.function_name
  }
}