provider "aws" {
    region = var.region
}

resource "aws_dynamodb_global_table" "sftp_global_user_table" {
  
}