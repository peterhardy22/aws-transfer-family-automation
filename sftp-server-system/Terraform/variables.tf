variable "region" {
  description = "Value of the AWS Region"
  type        = string
}

variable "subnet_ids" {
  description = "List of subnet IDs"
  type        = list(string)
}

variable "vpc_name" {
  description = "Value of VPC name"
  type        = string
}