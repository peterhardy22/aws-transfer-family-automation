provider "aws" {
    region = var.region
}

resource "aws_dynamodb_table" "sftp_global_user_table" {
    name = "${var.resource_name}-${var.aws_environment}-${var.region_prefix}-global-users-table"
    billing_mode = "PAY_PER_REQUEST"
    stream_view_type = "NEW_AND_OLD_IMAGES"

    attribute {
        name = "user_name"
        type = "S"
    }

    replica {
      region_name = "us-east-1"
    }
}