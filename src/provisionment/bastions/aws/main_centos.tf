provider "aws" {
  region = "us-east-2"
}

variable "openUser" {
  default = "centos"
}

resource "aws_instance" "launcher" { # With no more code, this VM will use the default security group that has nothing. Simply add to it (via GUI) the ssh rule
  tags = {
      Name = "TSlauncher"
  }
  ami = "ami-08ee2516c7709ea48" # Centos US
  #ami = "ami-0957ba512eafd08d9" # Centos EU
  #ami = "ami-0fc20dd1da406780b" # Ubuntu US
  instance_type = "t2.medium"
  key_name = "exo"
  root_block_device {
      volume_size = 50
  }
}
