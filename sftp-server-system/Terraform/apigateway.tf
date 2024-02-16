provider "aws" {
    region = var.region
}

resource "aws_api_gateway_rest_api" "sftp_api_gateway" {

    name = "${var.resource_name}-${var.aws_environment}-${var.region_prefix}-api-gateway"

    endpoint_configuration {
      types            = ["PRIVATE"]
      vpc_endpoint_ids = [data.aws_vpcs.sftp_vpc.id]
    }

    policy = jsonencode({
      Version = "2012-10-17"
      Statement = [{
        Effect = "Allow"
        Action = "execute-api:Invoke"
        Principal = "*"
        Resource = "arn:aws:execute-api:us-east-2:############:*/*/*/*"
        Condition = {
          StringEquals = {
            "aws:SourceVpc" = data.aws_vpcs.sftp_vpc.id
          }
        }
      }]
    })
}