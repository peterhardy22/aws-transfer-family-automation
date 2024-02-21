provider "aws" {
    region = var.region
}

data "aws_security_groups" "sftp_security_groups" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpcs.sftp_vpc.id]
  }
}

data "aws_subnets" "sftp_subnets" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpcs.sftp_vpc.id]
  }
}

data "aws_vpc" "sftp_vpc" {
    filter {
      name   = "tag:Name"
      values = [var.vpc_name]
  }
}

resource "aws_transfer_server" "sftp_server" {
  endpoint_type = "VPC"

  endpoint_details {
    subnet_ids = data.aws_vpcs.sftp_subnets.ids
    vpc_id     = data.aws_vpcs.sftp_vpc.id
  }

  logging_role = data.terraform_remote_state.sftp_admin_role.outputs.sftp_admin_role_arn
  protocols   = ["SFTP"]
  security_policy_name = "TransferSecurityPolicy-2024-01"

  depends_on = [aws_iam_role.sftp_admin_role]
}

resource "aws_dynamodb_table" "sftp_user_table" {
    name = "${var.resource_name}-${var.aws_environment}-${var.region_prefix}-ue2-users-table"
    billing_mode = "PAY_PER_REQUEST"
    hash_key = "user_name"
    stream_enabled = true
    stream_view_type = "NEW_AND_OLD_IMAGES"
    table_class = "STANDARD_INFREQUENT_ACCESS"

    point_in_time_recovery {
        enabled = true
    }

    server_side_encryption {
        enabled = true
    }

    attribute {
        name = "user_name"
        type = "S"
    }
}