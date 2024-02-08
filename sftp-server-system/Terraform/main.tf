provider "aws" {
    region = var.region
}

data "aws_vpcs" "sftp_vpc" {

}

resource "aws_transfer_server" "example" {
  endpoint_type = "VPC"

  endpoint_details {
    subnet_ids = data.aws_vpcs.sftp_vpc.subnet_ids
    vpc_id     = data.aws_vpcs.sftp_vpc.id
  }

  protocols   = ["SFTP"]
}