provider "opentelekomcloud" {
  access_key = yamldecode(file(yamldecode(file(var.configsFile))["authFile"]))["accK"]
  secret_key = yamldecode(file(yamldecode(file(var.configsFile))["authFile"]))["secK"]
  domain_name = yamldecode(file(var.configsFile))["domainName"]
  tenant_name = yamldecode(file(var.configsFile))["tenantName"]
  auth_url    = "https://iam.eu-de.otc.t-systems.com/v3"
}

resource "opentelekomcloud_compute_instance_v2" "kubenode" {
  count = var.useDefaultNetwork ? 0 : var.customCount
  name = "${var.instanceName}-${count.index}"
  flavor_name = var.flavor
  key_pair = yamldecode(file(var.configsFile))["keyPair"]
  security_groups = var.securityGroups
  availability_zone = var.availabilityZone
  network {
    name = yamldecode(file(var.configsFile))["networkID"]
  }
  block_device {
    uuid                  = yamldecode(file(var.configsFile))["imageID"]
    source_type           = "image"
    volume_size           = yamldecode(file(var.configsFile))["storageCapacity"]
    boot_index            = 0
    destination_type      = "volume"
    delete_on_termination = true
    volume_type           = "SATA"
  }
}

resource "opentelekomcloud_compute_instance_v2" "kubenode_defaultNetwork" {
  count = var.useDefaultNetwork ? var.customCount : 0
  name = "${var.instanceName}-${count.index}"
  flavor_name = var.flavor
  key_pair = yamldecode(file(var.configsFile))["keyPair"]
  security_groups = var.securityGroups
  availability_zone = var.availabilityZone
  block_device {
    uuid                  = yamldecode(file(var.configsFile))["imageID"]
    source_type           = "image"
    volume_size           = yamldecode(file(var.configsFile))["storageCapacity"]
    boot_index            = 0
    destination_type      = "volume"
    delete_on_termination = true
    volume_type           = "SATA"
  }
}
