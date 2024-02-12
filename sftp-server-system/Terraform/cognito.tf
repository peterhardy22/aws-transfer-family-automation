provider "aws" {
    region = var.region
}

resource "aws_cognito_user_pool" "cognito_user_pool" {
  name = ""
}