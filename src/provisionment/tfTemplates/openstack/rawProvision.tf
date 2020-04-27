provider "openstack" {
}

resource "openstack_compute_instance_v2" "kubenode" {
  count = var.useDefaultNetwork ? 0 : var.customCount
  flavor_name       = var.flavor
  name              = "${var.instanceName}-${count.index}"
  image_name        = yamldecode(file(var.configsFile))["imageName"]
  key_pair          = yamldecode(file(var.configsFile))["keyPair"]
  security_groups   = var.securityGroups
  region            = var.region
  availability_zone = var.availabilityZone
  network {
    name = yamldecode(file(var.configsFile))["networkName"]
  }
}

resource "openstack_compute_instance_v2" "kubenode_defaultNetwork" {
  count = var.useDefaultNetwork ? var.customCount : 0
  flavor_name       = var.flavor
  name              = "${var.instanceName}-${count.index}"
  image_name        = yamldecode(file(var.configsFile))["imageName"]
  key_pair          = yamldecode(file(var.configsFile))["keyPair"]
  security_groups   = var.securityGroups
  region            = var.region
  availability_zone = var.availabilityZone
}
