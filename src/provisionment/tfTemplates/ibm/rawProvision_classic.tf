terraform {
  required_providers {
    ibm = {
      source = "IBM-Cloud/ibm"
    }
  }
}

# Configure the IBM Provider
provider "ibm" {
    iaas_classic_username = yamldecode(file(yamldecode(file(var.configsFile))["authFile"]))["iaas_classic_username"]
    iaas_classic_api_key = yamldecode(file(yamldecode(file(var.configsFile))["authFile"]))["iaas_classic_api_key"]
}

# ID String for resources
resource "random_string" "id" {
  length  = 5
  special = false
  upper   = false
}

# Create SSH Key
resource "ibm_compute_ssh_key" "ssh_key" {
    label = "ts-sshkey-${random_string.id.result}"
    public_key = "${file(yamldecode(file(var.configsFile))["pathToPubKey"])}"
}

resource "ibm_compute_vm_instance" "instance" {
  count             = var.customCount
  hostname          = "${var.instanceName}-${count.index}"
  domain            = "ocre.ts"
  ssh_key_ids       = [ibm_compute_ssh_key.ssh_key.id]
  os_reference_code = yamldecode(file(var.configsFile))["os_reference_code"]
  datacenter        = yamldecode(file(var.configsFile))["datacenter"]
  network_speed     = yamldecode(file(var.configsFile))["network_speed"]
  flavor_key_name   = var.flavor
}
