module "sftp_user_table_ue2" {
  source = "main"

  providers = {
    aws = "aws.us-east-2"
  }
}

module "sftp_user_table_ue1" {
  source = "main"

  providers = {
    aws = "aws.us-east-1"
  }
}

resource "aws_dynamodb_global_table" "sftp_global_user_table" {
    depends_on = [
        module.sftp_user_table_ue2, 
        module.sftp_user_table_ue1
    ]
    
    name = "${var.resource_name}-${var.aws_environment}-${var.region_prefix}-global-users-table"
    
    replica {
      region_name = "us-east-2"
    }

    replica {
      region_name = "us-east-1"
    }
}