variable "ip" {
  default = "45.130.30.9"
}
variable "openUser" {
  default = "eouser"
}
variable "key" {
  default = "~/.ssh/id_rsa"
}

provider "openstack" {}

resource "openstack_compute_instance_v2" "tslauncher" {
  flavor_name           = "eo1.medium"
  name                  = "tslauncher"
  image_name = "CentOS 7"
  key_pair = "mykey"
  security_groups = ["default","allow_ping_ssh_rdp"]

}

resource "openstack_compute_floatingip_associate_v2" "fip_1" {
  floating_ip = var.ip
  instance_id = openstack_compute_instance_v2.tslauncher.id
  fixed_ip    = openstack_compute_instance_v2.tslauncher.network.0.fixed_ip_v4
}

resource "null_resource" "docker" {
  depends_on = [openstack_compute_floatingip_associate_v2.fip_1]
  connection {
    host = var.ip
    user        = var.openUser
    private_key = file(var.key)
  }
  provisioner "remote-exec" {
    inline = [
      "sudo yum update -y ; sudo yum install docker -y ; sudo systemctl start docker",
      "sudo docker run --name tslauncher -itd --net=host cernefp/tslauncher",
      "echo sudo docker exec -it tslauncher bash >> ~/.bashrc"
    ]
  }
}
