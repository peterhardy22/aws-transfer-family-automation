terraform {
    
  backend "remote" {
    organizations = "the-arts-concierge"
    workspace {
      name = "AWS-SFTP"
    }
  }
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }

  required_version = ">= 1.2.0"
}