provider "cloudstack" {
  #config = "/home/ipelu/Desktop/exoCreds"
  #profile = "local"
  api_url    = "https://api.exoscale.ch/compute"
  api_key    = ""
  secret_key = ""
}

resource "cloudstack_instance" "web" {
  name                 = "server-1"
  service_offering     = "Medium"
  template             = "Linux CentOS 7.6 64-bit"
  zone                 = "ch-gva-2"
  security_group_names = ["default"]
  keypair              = "k_cl"
}
