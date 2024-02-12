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

variable "subnet_ids" {
  description = "List of subnet IDs"
  type        = list(string)
}

variable "vpc_name" {
  description = "Value of VPC name"
  type        = string
}