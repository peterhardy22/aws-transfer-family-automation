provider "aws" {
    region = var.region
}

resource "aws_cognito_user_pool" "snow_user_pool" {
  name = "${var.resource_name}-${var.aws_environment}-${var.region_prefix}-cognito-userpool-servicenow"
  
  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  username_configuration {
    case_sensitive = false
  }
}

resource "aws_cognito_user_pool_domain" "snow_user_pool_domain" {
  domain       = "${var.resource_name}-${var.aws_environment}-${var.region_prefix}-servicenow"
  user_pool_id = aws_cognito_user_pool.snow_user_pool.id

  depends_on = [aws_cognito_user_pool.snow_user_pool]
}

