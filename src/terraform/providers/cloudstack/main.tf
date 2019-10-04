provider "cloudstack" {
  config  = "/home/ipelu/Desktop/exoCreds"
  profile = "cloudstack"
}

resource "cloudstack_instance" "node" {
  name                 = "server-1"
  zone                 = "ch-gva-2"
  template             = "Linux CentOS 7.6 64-bit"
  security_group_names = ["default"]
  keypair              = "k_cl"
  service_offering     = "Medium"
}
