variable "aws_environment" {
  description = "Value of the AWS account"
  type        = string
  default     = "dev"
}

variable "region" {
  description = "Value of the AWS Region"
  type        = string
  default     = "us-east-2"
}

variable "region_prefix" {
  description = "Value of AWS Region abbreviated"
  type        = string
  default     = "ue2"
}

variable "resource_name" {
  description = "Determines specific app this is dedicated to"
  type        = string
  default     = "sftp"
}


variable "sftp_s3_bucket" {
  description = "Name of S3 bucket used for primary SFTP Transfer Family server"
  type = string
}


variable "vpc_name" {
  description = "Value of VPC name"
  type        = string
}

variable "security_group_ids" {
  description = "List of security group Ids"
  type        = list(string)
}

variable "subnet_ids" {
  description = "List of subnet Ids"
  type        = list(string)
}

