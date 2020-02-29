##Setup needed variables
variable "node-count" {}

variable "image-name" {}
variable "image-flavor" {}
variable "security-groups" {}
variable "key-pair" {}
variable "exoscale_api_key" {}
variable "exoscale_secret_key" {}
variable "region" {}
variable "disk_size" {}

provider "exoscale" {
  key    = var.exoscale_api_key
  secret = var.exoscale_secret_key
}

resource "exoscale_compute" "k8s-master" {
  display_name    = "kubemaster"
  template        = var.image-name
  zone            = var.region
  size            = var.image-flavor
  disk_size       = var.disk_size
  security_groups = ["${split(",", var.security-groups)}"]
  key_pair        = var.key-pair
}

resource "exoscale_compute" "k8s-node" {
  count           = var.node-count
  display_name    = "kubenode${count.index}"
  template        = var.image-name
  zone            = var.region
  size            = var.image-flavor
  disk_size       = var.disk_size
  security_groups = ["${split(",", var.security-groups)}"]
  key_pair        = var.key-pair
}
