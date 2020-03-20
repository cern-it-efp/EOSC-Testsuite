variable "publicIP"{
  default = "185.178.84.49"
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
