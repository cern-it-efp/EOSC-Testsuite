provider "cloudstack" {
  config  = "${var.configPath}"
  profile = "cloudstack"
}

resource "cloudstack_instance" "kubenode" {
  count                = "${var.customCount}"
  zone                 = "${var.zone}"
  service_offering     = "${var.size}"
  name                 = "${var.instanceName}-${count.index}"
  template             = "${var.template}"
  keypair              = "${var.keyPair}"
  security_group_names = "${var.securityGroups}"
}
