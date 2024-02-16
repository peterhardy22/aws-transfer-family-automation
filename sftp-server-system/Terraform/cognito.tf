provider "aws" {
    region = var.region
}

resource "aws_cognito_user_pool" "snow_user_pool" {  
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  name = "${var.resource_name}-${var.aws_environment}-${var.region_prefix}-cognito-userpool-servicenow"

  username_configuration {
    case_sensitive = false
  }
}

output "snow_user_pool_arn" {
  value = aws_cognito_user_pool.snow_user_pool.arn
}

resource "aws_cognito_user_pool_domain" "snow_user_pool_domain" {
  domain       = "${var.resource_name}-${var.aws_environment}-${var.region_prefix}-servicenow"
  user_pool_id = aws_cognito_user_pool.snow_user_pool.id

  depends_on = [aws_cognito_user_pool.snow_user_pool]
}

resource "aws_cognito_user_pool_client" "snow_user_pool_client" {
  access_token_validity = 24
  allowed_oauth_flows = ["client_credentials"]
  callback_urls = ["http://dev.service-now.com/oauth_redirect.do"]
  enable_token_revocation = false
  explicit_auth_flows = [
    "ALLOW_CUSTOM_AUTH",
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH"
  ]
  generate_secret = true
  id_token_validity = 1
  logout_urls = ["https://www.amazon.com"]
  name = "servicenow-${var.aws_environment}"
  refresh_token_validity = 30
  supported_identity_providers = ["COGNITO"]
  user_pool_id = aws_cognito_user_pool.snow_user_pool.id

  depends_on = [aws_cognito_user_pool.snow_user_pool]
}