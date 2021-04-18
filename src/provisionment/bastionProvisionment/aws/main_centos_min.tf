provider "aws" {
  region = "eu-central-1"
  #region = "us-east-2"
  shared_credentials_file = "/home/ipelu/.aws/credentials"
  profile                 = "aws"
}

variable "openUser" {
  default = "centos"
}

resource "aws_instance" "launcher" { # uses the default security group
  tags = {
      Name = "TSlauncher"
  }
  #ami = "ami-08ee2516c7709ea48" # Centos US
  ami = "ami-0957ba512eafd08d9" # Centos EU
  #ami = "ami-0fc20dd1da406780b" # Ubuntu US
  instance_type = "t2.medium"
  key_name = "exo"
  root_block_device {
      volume_size = 50
  }
  "vpc-7de20c15"
}
