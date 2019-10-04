provider "exoscale" {
  config = "${var.configPath}"
}

resource "exoscale_compute" "kubenode" {
  count           = "${var.customCount}"
  zone            = "${var.zone}"
  size            = "${var.size}"
  display_name    = "${var.instanceName}-${count.index}"
  template        = "${var.template}"
  key_pair        = "${var.keyPair}"
  security_groups = "${var.securityGroups}"
  disk_size       = "${var.diskSize}"
}
