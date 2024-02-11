provider "aws" {
    region = var.region
}

resource "aws_iam_role" "sftp_admin_role" {
  name = "sftp-admin-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = [
            "iam:GetRole",
            "iam:PassRole"
        ]
        Effect   = "Allow"
        Sid      = "IAMRolePassing"
        Resource = [
            "arn:aws:iam::############:role/sftp-class1-role",
            "arn:aws:iam::############:role/sftp-standard-role"
        ]
      },
      {
        Action   = [
            "s3:*",
            "s3-object-lambda:*"
        ]
        Effect   = "Allow"
        Sid      = "S3FullAccess"
        Resource = [
            "arn:aws:s3:::dev-us-east-2-sftp",
            "arn:aws:s3:::dev-us-east-2-sftp/*",
            "arn:aws:s3:::dev-us-east-1-sftp",
            "arn:aws:s3:::dev-us-east-1-sftp/*"
        ]
      },
      {
        Action   = [
            "dynamodb:BatchGetItem",
            "dynamodb:BatchWriteItem",
            "dynamodb:ConditionCheckItem",
            "dynamodb:DeleteItem",
            "dynamodb:GetItem",
            "dynamodb:PutItem",
            "dynamodb:Query",
            "dynamodb:Scan",
            "dynamodb:UpdateItem"
        ]
        Effect   = "Allow"
        Sid      = "AccessDynamoDBTableAllIndexes"
        Resource = [
            "arn:aws:dynamodb:us-east-2:############:table/dev-global-sftp-user-table",
            "arn:aws:dynamodb:us-east-2:############:table/dev-global-sftp-user-table/index/*",
            "arn:aws:dynamodb:us-east-1:############:table/dev-global-sftp-user-table",
            "arn:aws:dynamodb:us-east-1:############:table/dev-global-sftp-user-table/index/*"
        ]
      },
      {
        Action   = "transfer:*"
        Effect   = "Allow"
        Sid      = "TransferFamilyFullAccess"
        Resource = "*"
      },
      {
        Action   = [
            "cloudtrail:GetEventSelectors",
            "cloudtrail:GetTrail",
            "cloudtrail:GetTrailStatus"
        ]
        Effect   = "Allow"
        Sid      = "CloudTrailAccess"
        Resource = [
            "arn:aws:cloudtrail:us-east-2:############:trail/my-global-cloudtrail",
            "arn:aws:cloudtrail:us-east-1:############:trail/my-global-cloudtrail"
        ]
      },
      {
        Action   = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:DescribeLogStreams",
            "logs:PutLogEvents"
        ]
        Effect   = "Allow"
        Sid      = "CloudWatchLogging"
        Resource = "arn:aws:logs:*:*:log-group:/aws/transfer/*"
      },
      {
        Action   = "sns:Publish"
        Effect   = "Allow"
        Sid      = "SNSPublish"
        Resource = "arn:aws:sns:us-east-2:############:error_handling_sftp"
      },
      {
        Action   = [
            "ec2:CreateNetworkInterface",
            "ec2:DeleteNetworkInterface",
            "ec2:DescribeNetworkInterfaces"
        ]
        Effect   = "Allow"
        Sid      = "EC2Access"
        Resource = "*"
      }
    ]
  })
}    

output "sftp_admin_role_arn" {
  value = aws_iam_role.sftp_admin_role.arn
}

resource "aws_iam_role" "sftp_class1_role" {
  name = "sftp-class1-role"

  assume_role_policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowSFTPAdminAssumeRole",
            "Effect": "Allow",
            "Action": [
                "iam:GetRole"
            ],
            "Resource": "arn:aws:iam::############:role/sftp-admin-role"
        },
        {
            "Sid": "AllowBucketPolicyForTransferFamily",
            "Effect": "Allow",
            "Action": [
                "s3:DeleteObject",
                "s3:DeleteObjectVersion",
                "s3:GetObject",
                "s3:GetObjectVersion",
                "s3:PutObject",
                "s3:PutObjectAcl"
            ],
            "Resource": [
                "arn:aws:s3:::dev-us-east-2-sftp",
                "arn:aws:s3:::dev-us-east-2-sftp/*"
            ]
        },
        {
            "Sid": "ListAllMyBuckets",
            "Effect": "Allow",
            "Action": "s3:ListAllMyBuckets",
            "Resource": "*"
        },
        {
            "Sid": "ListBucket",
            "Effect": "Allow",
            "Action": [
                "s3:GetBucketLocation",
                "s3:ListBucket"
            ],
            "Resource": "arn:aws:s3:::dev-us-east-2-sftp"
        },
        {
            "Sid": "CloudWatchLogging",
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:DescribeLogStreams",
                "logs:PutLogEvents"
            ],
            "Resource": "arn:aws:logs:*:*:log-groups:/aws/transfer/*"
        }
    ]
})
} 