provider "aws" {
    region = var.region
}

resource "aws_dynamodb_global_table" "sftp_global_user_table" {
    name = "${var.resource_name}-${var.aws_environment}-${var.region_prefix}-global-users-table"
    
    replica {
      region_name = "us-east-1"
    }
}