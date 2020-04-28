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
  key_pair = "mykey"
  security_groups = ["default","allow_ping_ssh_rdp"]

  block_device {
    uuid                  = "9f954559-da79-4c6a-a0a0-aedb889e0c6a" # centos7
    source_type           = "image"
    volume_size           = null
    boot_index            = 0
    destination_type      = "volume"
    delete_on_termination = true
  }

}

resource "openstack_compute_floatingip_associate_v2" "fip_1" {
  floating_ip = var.ip
  instance_id = openstack_compute_instance_v2.tslauncher.id
  fixed_ip    = openstack_compute_instance_v2.tslauncher.network.0.fixed_ip_v4
}
