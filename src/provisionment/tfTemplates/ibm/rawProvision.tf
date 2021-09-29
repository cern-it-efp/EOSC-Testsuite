terraform {
  required_providers {
    ibm = {
      source = "IBM-Cloud/ibm"
    }
  }
}

# Configure the IBM Provider
provider "ibm" {
    region = yamldecode(file(var.configsFile))["region"]
    ibmcloud_api_key = yamldecode(file(yamldecode(file(var.configsFile))["authFile"]))["ibmcloud_api_key"]
}

# ID String for resources
resource "random_string" "id" {
  length  = 5
  special = false
  upper   = false
}

# Create VPC
resource "ibm_is_vpc" "vpc" { # Available only in MZRs
  name = "ts-vpc-${random_string.id.result}"
}

# Create Security Group (and attach rules)
resource "ibm_is_security_group" "security_group" {
  name = "ts-secgroup-${random_string.id.result}"
  vpc  = ibm_is_vpc.vpc.id
}
resource "ibm_is_security_group_rule" "security_group_rule_all_in" {
    group = ibm_is_security_group.security_group.id
    direction = "inbound"
}
resource "ibm_is_security_group_rule" "security_group_rule_all_out" {
    group = ibm_is_security_group.security_group.id
    direction = "outbound"
}

# Create Subnet
resource "ibm_is_subnet" "subnet" {
  name            = "ts-subnet-${random_string.id.result}"
  vpc             = ibm_is_vpc.vpc.id
  zone            = yamldecode(file(var.configsFile))["zone"]
  total_ipv4_address_count = 32
}

# Create SSH Key
resource "ibm_is_ssh_key" "sshkey" {
  name       = "ts-sshkey-${random_string.id.result}"
  public_key = "${file(yamldecode(file(var.configsFile))["pathToPubKey"])}"
}

# Retrieve Image
data "ibm_is_image" "image" {
  name = yamldecode(file(var.configsFile))["image"] # "centos-7.x-amd64"
}

# Create Instance(s)
resource "ibm_is_instance" "instance" {
  count = var.customCount
  name    = "${var.instanceName}-${count.index}"
  image   = data.ibm_is_image.image.id
  profile = yamldecode(file(var.configsFile))["flavor"]
  primary_network_interface {
    subnet = ibm_is_subnet.subnet.id
    security_groups = [ibm_is_security_group.security_group.id]
  }
  vpc  = ibm_is_vpc.vpc.id
  zone = yamldecode(file(var.configsFile))["zone"]
  keys = [ibm_is_ssh_key.sshkey.id]
}

# Create Floating IP
resource "ibm_is_floating_ip" "floating_ip" {
  count = var.customCount
  name   = "ts-fip-${random_string.id.result}-${count.index}"
  target = ibm_is_instance.instance[count.index].primary_network_interface[0].id
}
