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

resource "aws_api_gateway_authorizer" "sftp_api_gateway_authorizer" {
    name = "Snow-Pawtrol"
    provider_arns = data.terraform_remote_state.snow_user_pool.outputs.snow_user_pool_arn
    rest_api_id = aws_api_gateway_rest_api.sftp_api_gateway.id
    type = "COGNITO_USER_POOLS"

    depends_on = [aws_cognito_user_pool.snow_user_pool]
}

resource "aws_api_gateway_resource" "sftp_api_gateway_resource" {
    parent_id = aws_api_gateway_rest_api.sftp_api_gateway.root_resource_id
    path_part = var.resource_name
    rest_api_id = aws_api_gateway_rest_api.sftp_api_gateway.id
}