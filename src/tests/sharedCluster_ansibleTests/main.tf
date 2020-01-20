variable "template"{
  default = "Linux CentOS 7 64-bit"
  #default = "Linux Ubuntu 18.04 LTS 64-bit"
}

provider "exoscale" {
  config = "~/Desktop/exoCreds"
}

resource "exoscale_compute" "kubenode" {
  count = 6
  zone            = "ch-gva-2"
  size            = "Medium"
  display_name    = "ansiblevm-${count.index}"
  template        = var.template # OK
  key_pair        = "k_cl"
  security_groups = ["default"]
  disk_size       = 50
}
