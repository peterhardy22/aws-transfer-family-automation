provider "aws" {
    region = var.region
}

resource "aws_transfer_server" "example" {
  endpoint_type = "VPC"

  endpoint_details {
    
  }

  protocols   = ["SFTP"]
}