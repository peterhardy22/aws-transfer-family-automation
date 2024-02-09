provider "aws" {
    region = var.region
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
