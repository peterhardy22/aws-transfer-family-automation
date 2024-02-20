provider "aws" {
  alias = "us-east-2"
  region = "us-east-2"
  profile = "${var.aws_account_id}"
}

provider "aws" {
  alias = "us-east-1"
  region = "us-east-1"
  profile = "${var.aws_account_id}"
}