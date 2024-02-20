provider "aws" {
    region = var.region
}

resource "aws_dynamodb_table" "sftp_user_table" {
    name = "${var.resource_name}-${var.aws_environment}-${var.region_prefix}-ue2-users-table"
    billing_mode = "PAY_PER_REQUEST"
    hash_key = "user_name"
    stream_enabled = true
    stream_view_type = "NEW_AND_OLD_IMAGES"
    table_class = "STANDARD_INFREQUENT_ACCESS"

    point_in_time_recovery {
        enabled = true
    }

    server_side_encryption {
        enabled = true
    }

    attribute {
        name = "user_name"
        type = "S"
    }
}

resource "aws_dynamodb_global_table" "sftp_global_user_table" {
    depends_on = [sftp_user_table_ue2, sftp_user_table_ue1]
    name = "${var.resource_name}-${var.aws_environment}-${var.region_prefix}-global-users-table"
    
    replica {
      region_name = "us-east-2"
    }

    replica {
      region_name = "us-east-1"
    }
}