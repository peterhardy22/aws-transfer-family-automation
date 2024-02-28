# aws-transfer-family-automation
Sets up an aws transfer family sftp server and leverages multiple lambda functions to automate user creation, user management, and event driven file actions.

IaC:
  1. CloudFormation
  2. Terraform

Resources:
  1. Transfer Family SFTP server
  2. API Gateway
  3. IAM roles
  4. S3 buckets
  5. Cognito user pool
  6. DynamoDB table
  7. Lambda functions
  8. SNS 