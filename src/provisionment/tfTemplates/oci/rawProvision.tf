provider "oci" {
  tenancy_ocid = yamldecode(file(yamldecode(file(var.configsFile))["authFile"]))["tenancyOcid"]
  user_ocid = yamldecode(file(yamldecode(file(var.configsFile))["authFile"]))["userOcid"]
  fingerprint = yamldecode(file(yamldecode(file(var.configsFile))["authFile"]))["fingerprint"]
  private_key_path = yamldecode(file(yamldecode(file(var.configsFile))["authFile"]))["privateKeyPath"]
  region = yamldecode(file(var.configsFile))["region"]
}

resource "random_string" "id" {
  length  = 5
  special = false
  upper   = false
}

resource "oci_core_vcn" "vcn" {
    compartment_id = yamldecode(file(var.configsFile))["compartmentOcid"]
    cidr_blocks = ["10.0.0.0/16"]
    display_name = "tsvcn-${random_string.id.result}"
}

resource "oci_core_internet_gateway" "internet_gateway" {
    compartment_id = yamldecode(file(var.configsFile))["compartmentOcid"]
    vcn_id = oci_core_vcn.vcn.id
    display_name = "tsig-${random_string.id.result}"
}

resource "oci_core_route_table" "route_table" {
    compartment_id = yamldecode(file(var.configsFile))["compartmentOcid"]
    vcn_id = oci_core_vcn.vcn.id
    display_name = "tsrt-${random_string.id.result}"
    route_rules {
        network_entity_id = oci_core_internet_gateway.internet_gateway.id
        destination = "0.0.0.0/0"
    }
}

resource "oci_core_network_security_group" "network_security_group" {
    compartment_id = yamldecode(file(var.configsFile))["compartmentOcid"]
    vcn_id = oci_core_vcn.vcn.id
    display_name = "tsnsg-${random_string.id.result}"
}

resource "oci_core_network_security_group_security_rule" "network_security_group_security_rule_ingress" {
    network_security_group_id = oci_core_network_security_group.network_security_group.id
    direction = "INGRESS"
    protocol = "all"
    destination = "0.0.0.0/0"
    source = "0.0.0.0/0"
}

resource "oci_core_network_security_group_security_rule" "network_security_group_security_rule_egress" {
    network_security_group_id = oci_core_network_security_group.network_security_group.id
    direction = "EGRESS"
    protocol = "all"
    destination = "0.0.0.0/0"
    source = "0.0.0.0/0"
}

resource "oci_core_security_list" "security_list" {
    compartment_id = yamldecode(file(var.configsFile))["compartmentOcid"]
    vcn_id = oci_core_vcn.vcn.id
    display_name = "tssl-${random_string.id.result}"
    ingress_security_rules {
        protocol = "all"
        source = "0.0.0.0/0"
    }
    egress_security_rules {
        protocol = "all"
        destination = "0.0.0.0/0"
    }
}

resource "oci_core_subnet" "subnet" {
    cidr_block = "10.0.0.0/24"
    compartment_id = yamldecode(file(var.configsFile))["compartmentOcid"]
    vcn_id = oci_core_vcn.vcn.id
    availability_domain = yamldecode(file(var.configsFile))["availabilityDomain"]
    display_name = "tssn-${random_string.id.result}"
    route_table_id = oci_core_route_table.route_table.id
    security_list_ids = [oci_core_security_list.security_list.id]
}

resource "oci_core_instance" "kubenode" {
  count = var.useFlexShape ? 0 : var.customCount
  display_name        = "${var.instanceName}-${count.index}"
  availability_domain = yamldecode(file(var.configsFile))["availabilityDomain"]
  compartment_id      = yamldecode(file(var.configsFile))["compartmentOcid"]
  shape               = var.flavor
  create_vnic_details {
    subnet_id        = oci_core_subnet.subnet.id
    nsg_ids          = [oci_core_network_security_group.network_security_group.id]
  }
  source_details {
    source_type = "image"
    source_id   = yamldecode(file(var.configsFile))["imageOcid"]
    boot_volume_size_in_gbs = yamldecode(file(var.configsFile))["storageCapacity"]
  }
  metadata = {
    ssh_authorized_keys = file(yamldecode(file(var.configsFile))["pathToPubKey"])
  }
}
resource "oci_core_instance" "kubenode_flex" {
  count = var.useFlexShape ? var.customCount : 0
  display_name        = "${var.instanceName}-${count.index}"
  availability_domain = yamldecode(file(var.configsFile))["availabilityDomain"]
  compartment_id      = yamldecode(file(var.configsFile))["compartmentOcid"]
  shape               = var.flavor
  shape_config {
      memory_in_gbs = yamldecode(file(var.configsFile))["memoryInGbs"]
      ocpus = yamldecode(file(var.configsFile))["ocpus"]
  }
  create_vnic_details {
    subnet_id        = oci_core_subnet.subnet.id
    nsg_ids          = [oci_core_network_security_group.network_security_group.id]
  }
  source_details {
    source_type = "image"
    source_id   = yamldecode(file(var.configsFile))["imageOcid"]
    boot_volume_size_in_gbs = yamldecode(file(var.configsFile))["storageCapacity"]
  }
  metadata = {
    ssh_authorized_keys = file(yamldecode(file(var.configsFile))["pathToPubKey"])
  }
}
