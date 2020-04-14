variable "auth" {
  default = "/home/ipelu/Desktop/oracle.yaml"
}
#---------------
variable "cidr_block_vcn" {
  default = "10.0.0.0/16"
}
variable "cidr_block_subnet" {
  default = "10.0.0.0/24"
}
#---------------
variable "instance_shape" {
  default = "VM.Standard1.1	"
}
variable "region" {
  default = "eu-frankfurt-1"
}
variable "availability_domain" {
  default = "BKrI:EU-FRANKFURT-1-AD-1" # "BKrI:EU-ZURICH-1-AD-1"
}
variable "private_key_path" {
  default = "/home/ipelu/.ssh/oracle.pem"
}
variable "ssh_public_key_path" {
  default = "/home/ipelu/.ssh/oraclePub.pem"
}
variable "diskSize" {
  default = 50
}
variable "fingerprint" {
  default = "d9:5a:05:58:e5:3a:d3:86:1b:6c:09:d5:70:99:83:ca"
}
variable "image_ocid" {
  default = "ocid1.image.oc1.eu-frankfurt-1.aaaaaaaawtnpiyjp36tyx7hkkymil2efkvitkrrnqi5qjpahcuoyvtcwhc5q" # Ubuntu 18.04
}

provider "oci" {
  tenancy_ocid = yamldecode(file(var.auth))["tenancy_ocid"]
  user_ocid = yamldecode(file(var.auth))["user_ocid"]
  fingerprint = var.fingerprint
  private_key_path = var.private_key_path
  region = var.region
}

resource "oci_core_vcn" "test_vcn" {
  cidr_block     = var.cidr_block_vcn
  compartment_id = yamldecode(file(var.auth))["compartment_ocid"]
  display_name = "vcnDisplayName"
  dns_label = "vcnDnsLabel"
}

resource "oci_core_subnet" "test_subnet" {
  depends_on = [oci_core_vcn.test_vcn]
  cidr_block          = var.cidr_block_subnet
  compartment_id      = yamldecode(file(var.auth))["compartment_ocid"]
  vcn_id              = oci_core_vcn.test_vcn.id

  #availability_domain = "${data.oci_identity_availability_domain.ad.name}"
  #display_name        = "TestSubnet"
  #dns_label           = "testsubnet"
  #security_list_ids   = ["${oci_core_vcn.test_vcn.default_security_list_id}"]
  #route_table_id      = oci_core_vcn.test_vcn.default_route_table_id
  #dhcp_options_id     = oci_core_vcn.test_vcn.default_dhcp_options_id
}

resource "oci_core_instance" "test_instance" {
  depends_on = [oci_core_subnet.test_subnet]
  availability_domain = var.availability_domain
  compartment_id      = yamldecode(file(var.auth))["compartment_ocid"]
  display_name        = "tslauncher"
  shape               = var.instance_shape

  #create_vnic_details {
  #  subnet_id        = oci_core_subnet.test_subnet.id
  #  assign_public_ip = true
  #}
  source_details {
    source_type = "image"
    source_id   = var.image_ocid
    boot_volume_size_in_gbs = var.diskSize
  }
  metadata = {
    ssh_authorized_keys = file(var.ssh_public_key_path)
  }
}
