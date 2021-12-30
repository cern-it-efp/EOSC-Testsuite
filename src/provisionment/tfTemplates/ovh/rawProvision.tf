terraform {
  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
    }
  }
}

provider "openstack" {
  region = yamldecode(file(var.configsFile))["region"]
}

# Creating the instance
resource "openstack_compute_instance_v2" "instance" {
  count       = var.customCount
  name        = "${var.instanceName}-${count.index}"
  flavor_name = var.flavor
  user_data   = "#cloud-config\n\nssh_authorized_keys:\n  - ${file(yamldecode(file(var.configsFile))["pathToPubKey"])}"

  block_device { # Boots from volume
    uuid                  = yamldecode(file(var.configsFile))["imageID"]
    source_type           = "image"
    volume_size           = yamldecode(file(var.configsFile))["storageCapacity"]
    boot_index            = 0
    destination_type      = "volume"
    delete_on_termination = true
  }
}
