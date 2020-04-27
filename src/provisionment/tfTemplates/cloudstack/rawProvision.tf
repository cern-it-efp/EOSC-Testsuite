provider "cloudstack" {
  config  = yamldecode(file(var.configsFile))["authFile"]
  profile = "cloudstack"
}

resource "cloudstack_instance" "kubenode" {
  count                = var.customCount
  name                 = "${var.instanceName}-${count.index}"
  zone                 = yamldecode(file(var.configsFile))["zone"]
  service_offering     = var.flavor
  template             = yamldecode(file(var.configsFile))["template"]
  keypair              = yamldecode(file(var.configsFile))["keyPair"]
  security_group_names = var.securityGroups
  root_disk_size       = var.storageCapacity
}
