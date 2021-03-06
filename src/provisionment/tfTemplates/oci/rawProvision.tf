provider "oci" {
  tenancy_ocid = yamldecode(file(yamldecode(file(var.configsFile))["authFile"]))["tenancy_ocid"]
  user_ocid = yamldecode(file(yamldecode(file(var.configsFile))["authFile"]))["user_ocid"]
  fingerprint = yamldecode(file(yamldecode(file(var.configsFile))["authFile"]))["fingerprint"]
  private_key_path = yamldecode(file(yamldecode(file(var.configsFile))["authFile"]))["auth_private_key_path"]
  region = yamldecode(file(yamldecode(file(var.configsFile))["authFile"]))["region"]
}

resource "oci_core_instance" "kubenode" {
  count = var.customCount
  display_name        = "${var.instanceName}-${count.index}"
  availability_domain = yamldecode(file(var.configsFile))["availability_domain"]
  compartment_id      = yamldecode(file(var.configsFile))["compartment_ocid"]
  shape               = var.flavor

  create_vnic_details {
    subnet_id        = yamldecode(file(var.configsFile))["subnet_ocid"]
    assign_public_ip = true
  }
  source_details {
    source_type = "image"
    source_id   = yamldecode(file(var.configsFile))["image_ocid"]
    boot_volume_size_in_gbs = var.storageCapacity
  }
  metadata = {
    ssh_authorized_keys = file(yamldecode(file(var.configsFile))["ssh_public_key_path"])
  }
}
