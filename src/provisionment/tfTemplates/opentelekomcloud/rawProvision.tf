provider "opentelekomcloud" {
  access_key = yamldecode(file(var.authFile))["accK"]
  secret_key = yamldecode(file(var.authFile))["secK"]
  domain_name = yamldecode(file(var.configsFile))["domainName"]
  tenant_name = yamldecode(file(var.configsFile))["tenantName"]
  auth_url    = "https://iam.eu-de.otc.t-systems.com/v3"
}

resource "opentelekomcloud_compute_instance_v2" "kubenode" {
  count = var.customCount
  name = "${var.instanceName}-${count.index}"
  #flavor_name = yamldecode(file(var.configsFile))["flavor"]
  flavor_name = var.flavor
  key_pair = yamldecode(file(var.configsFile))["keyPair"]
  #security_groups = yamldecode(file(var.configsFile))["securityGroups"]
  security_groups = var.securityGroups

  block_device {
    uuid                  = yamldecode(file(var.configsFile))["imageID"]
    source_type           = "image"
    volume_size           = yamldecode(file(var.configsFile))["diskSize"]
    boot_index            = 0
    destination_type      = "volume"
    delete_on_termination = true
    volume_type           = "SATA"
  }
}
