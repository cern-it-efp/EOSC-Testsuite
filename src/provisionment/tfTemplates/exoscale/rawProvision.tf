provider "exoscale" {
  config = yamldecode(file(var.configsFile))["authFile"]
}

resource "exoscale_compute" "kubenode" {
  count           = var.customCount
  display_name    = "${var.instanceName}-${count.index}"
  zone            = yamldecode(file(var.configsFile))["zone"]
  size            = var.flavor
  template        = yamldecode(file(var.configsFile))["template"]
  key_pair        = yamldecode(file(var.configsFile))["keyPair"]
  disk_size       = yamldecode(file(var.configsFile))["storageCapacity"]
  security_groups = var.securityGroups
}
