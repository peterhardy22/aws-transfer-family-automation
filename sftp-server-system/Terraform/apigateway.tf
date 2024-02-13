provider "aws" {
    region = var.region
}

resource "aws_api_gateway_rest_api" "sftp_api_gateway" {
    name = "${var.resource_name}-${var.aws_environment}-${var.region_prefix}-api-gateway"
}