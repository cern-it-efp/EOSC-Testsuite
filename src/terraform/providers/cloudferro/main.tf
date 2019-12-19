variable "publicIP"{
  default = "185.178.84.15"
}

provider "openstack" {
}

resource "openstack_compute_instance_v2" "tslauncher" {
  flavor_name           = "eo1.medium"
  name                  = "tslauncher"
  image_name = "CentOS 7"
  key_pair = "mykey"
  security_groups = ["default","allow_ping_ssh_rdp"]
}

# here: get and associate floating IP

resource "null_resource" "allow_root" {
  provisioner "remote-exec" {
    connection {
      host        = "${var.publicIP}"
      type        = "ssh"
      user        = "eouser"
      private_key = file("/home/ipelu/.ssh/id_rsa")
      timeout     = "20m"
    }
    inline = [
      "sudo mkdir /root/.ssh",
      "sudo cp /home/eouser/.ssh/authorized_keys /root/.ssh",
      "sudo sed -i '1iPermitRootLogin yes\n' /etc/ssh/sshd_config",
      "sudo systemctl restart sshd || sudo service sshd restart"
    ]
  }
}
