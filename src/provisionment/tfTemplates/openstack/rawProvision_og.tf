terraform {
  required_providers {
    openstack = {
      source = "terraform-provider-openstack/openstack"
    }
  }
}

provider "openstack" {
}

resource "openstack_compute_instance_v2" "kubenode" {
  count = var.useDefaultNetwork ? 0 : var.customCount
  flavor_name       = var.flavor
  name              = "${var.instanceName}-${count.index}"
  image_name        = yamldecode(file(var.configsFile))["imageID"]
  key_pair          = yamldecode(file(var.configsFile))["keyPair"]
  security_groups   = var.securityGroups
  region            = var.region
  availability_zone = var.availabilityZone
  block_device {
    uuid                  = yamldecode(file(var.configsFile))["imageID"]
    source_type           = "image"
    volume_size           = yamldecode(file(var.configsFile))["storageCapacity"]
    boot_index            = 0
    destination_type      = "volume"
    delete_on_termination = true
  }
  network {
    name = yamldecode(file(var.configsFile))["networkName"]
  }
}

resource "openstack_compute_instance_v2" "kubenode_defaultNetwork" {
  count = var.useDefaultNetwork ? var.customCount : 0
  flavor_name       = var.flavor
  name              = "${var.instanceName}-${count.index}"
  image_name        = yamldecode(file(var.configsFile))["imageID"]
  key_pair          = yamldecode(file(var.configsFile))["keyPair"]
  security_groups   = var.securityGroups
  region            = var.region
  availability_zone = var.availabilityZone
  block_device {
    uuid                  = yamldecode(file(var.configsFile))["imageID"]
    source_type           = "image"
    volume_size           = yamldecode(file(var.configsFile))["storageCapacity"]
    boot_index            = 0
    destination_type      = "volume"
    delete_on_termination = true
  }
}
