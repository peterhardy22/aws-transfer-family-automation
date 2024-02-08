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

resource "aws_iam_role" "sftp_admin_role" {
  name = "sftp-admin-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = [
            "iam:GetRole",
            "iam:PassRole"
        ]
        Effect   = "Allow"
        Sid      = ""
        Resource = [
                "arn:aws:iam::############:role/sftp-class1-role",
                "arn:aws:iam::############:role/sftp-standard-role"
            ]
      },
    ]
  })
}    

output "sftp_admin_role_arn" {
  value = aws_iam_role.sftp_admin_role.arn
}