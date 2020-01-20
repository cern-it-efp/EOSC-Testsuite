provider "aws" {
  region = "us-east-2"
  shared_credentials_file = "/creds"
}
variable "ami" {
  default = "ami-08ee2516c7709ea48" # Centos US
  #default = "ami-e1496384" # Ubuntu US
  #default = "ami-0957ba512eafd08d9" # Centos EU
}
variable "pathToKey" {
  default = "~/.ssh/id_rsa"
}

resource "aws_instance" "kubenode" {

  count = 3
  tags = {
    Name = "ansiblevm-${count.index}"
  }
  ami = var.ami
  instance_type = "t2.medium"
  key_name = "exo"
  root_block_device {
      volume_size = 50
  }
}
