provider "aws" {
  #region = "eu-central-1"
  region = "us-east-2"
}

variable "openUser" {
  default = "centos"
}

resource "aws_instance" "launcher" { # uses the default security group
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

resource "null_resource" "allow_root" {
  depends_on = [aws_instance.launcher]
  connection {
    type        = "ssh"
    host = aws_instance.launcher.public_ip
    user        = var.openUser
    private_key = file("~/.ssh/id_rsa")
  }
  provisioner "remote-exec" { # Not needed as the ami has docker: "sudo yum update -y ; sudo yum install docker.io -y"
    inline = [
      "sudo docker run --name tslauncher -itd --net=host cernefp/tslauncher",
      "echo sudo docker exec -it tslauncher bash >> ~/.bashrc"
    ]

  }
}
