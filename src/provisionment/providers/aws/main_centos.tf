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
  #ami = "ami-e1496384" # Ubuntu US
  instance_type = "t2.medium"
  key_name = "exo"
  root_block_device {
      volume_size = 50
  }
}

resource null_resource "allow_root" {
  provisioner "remote-exec" {
    connection {
      host        = aws_instance.launcher.public_ip
      type        = "ssh"
      user        = var.openUser
      private_key = file("~/.ssh/id_rsa")
    }
    inline = [
      "sudo mkdir /root/.ssh",
      "sudo cp /home/${var.openUser}/.ssh/authorized_keys /root/.ssh",
      "sudo sed -i '1iPermitRootLogin yes\n' /etc/ssh/sshd_config",
      "sudo systemctl restart sshd || sudo service sshd restart"
    ]
  }
}
