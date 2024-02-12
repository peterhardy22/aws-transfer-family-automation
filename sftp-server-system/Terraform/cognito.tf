provider "aws" {
    region = var.region
}

resource "aws_cognito_user_pool" "cognito_user_pool" {
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