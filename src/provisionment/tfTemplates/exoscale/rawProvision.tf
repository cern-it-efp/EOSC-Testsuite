terraform {
  required_providers {
    exoscale = {
      source = "exoscale/exoscale"
    }
  }
}

provider "exoscale" {
  key = yamldecode(file(yamldecode(file(var.configsFile))["authFile"]))["key"] 
  secret = yamldecode(file(yamldecode(file(var.configsFile))["authFile"]))["secret"]
}

resource "random_string" "id" {
  length  = 5
  special = false
  upper   = false
}

resource "exoscale_ssh_key" "sshkey" {
  name       = "ts-sshkey-${random_string.id.result}"
  public_key = "${file(yamldecode(file(var.configsFile))["pathToPubKey"])}"
}

resource "exoscale_compute" "kubenode" {
  count           = var.customCount
  display_name    = "${var.instanceName}-${count.index}"
  zone            = yamldecode(file(var.configsFile))["zone"]
  size            = var.flavor
  template        = yamldecode(file(var.configsFile))["template"]
  key_pair        = exoscale_ssh_key.sshkey.name
  disk_size       = yamldecode(file(var.configsFile))["storageCapacity"]
  security_groups = var.securityGroups
}
