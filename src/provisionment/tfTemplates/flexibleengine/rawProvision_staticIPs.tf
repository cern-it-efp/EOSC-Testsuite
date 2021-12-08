terraform {
  required_providers {
    flexibleengine = {
      source = "FlexibleEngineCloud/flexibleengine"
    }
  }
}

provider "flexibleengine" {
  access_key  = yamldecode(file(yamldecode(file(var.configsFile))["authFile"]))["accessKey"]
  secret_key  = yamldecode(file(yamldecode(file(var.configsFile))["authFile"]))["secretKey"]
  domain_name = yamldecode(file(yamldecode(file(var.configsFile))["authFile"]))["domainName"]
  region      = yamldecode(file(var.configsFile))["region"]
  auth_url    = "https://iam.eu-west-0.prod-cloud-ocb.orange-business.com/v3"
}

# ID String for resources
resource "random_string" "id" {
  length  = 5
  special = false
  upper   = false
}

# Create Virtual Private Cloud
resource "flexibleengine_vpc_v1" "vpc" {
  name = "ts-vpc-${random_string.id.result}"
  cidr = "10.1.0.0/16"
}

# Create subnet inside the VPC
resource "flexibleengine_vpc_subnet_v1" "subnet" {
  name = "ts-vpc-subnet-${random_string.id.result}"
  cidr       = "10.1.0.0/24"
  gateway_ip = "10.1.0.1"
  primary_dns = "8.8.8.8"
  vpc_id     = flexibleengine_vpc_v1.vpc.id
}

# Create security group
resource "flexibleengine_networking_secgroup_v2" "secgroup" {
  name        = "ts-secgroup-${random_string.id.result}"
}

# Add rules to the security group
resource "flexibleengine_networking_secgroup_rule_v2" "secgroup_rule_ingress4" {
  direction         = "ingress"
  ethertype         = "IPv4"
  security_group_id = flexibleengine_networking_secgroup_v2.secgroup.id
}
resource "flexibleengine_networking_secgroup_rule_v2" "secgroup_rule_ingress6" {
  direction         = "ingress"
  ethertype         = "IPv6"
  security_group_id = flexibleengine_networking_secgroup_v2.secgroup.id
}

# Create VM
resource "flexibleengine_compute_instance_v2" "kubenode" {
  depends_on = [flexibleengine_vpc_subnet_v1.subnet]
  count = var.customCount
  name = "${var.instanceName}-${count.index}"
  flavor_id       = var.flavor
  security_groups = [flexibleengine_networking_secgroup_v2.secgroup.name]
  user_data     = "#cloud-config\n\nssh_authorized_keys:\n  - ${file(yamldecode(file(var.configsFile))["pathToPubKey"])}"
  availability_zone = yamldecode(file(var.configsFile))["availabilityZone"]
  network {
    uuid = flexibleengine_vpc_subnet_v1.subnet.id
  }
  block_device { # Boots from volume
    uuid                  = yamldecode(file(var.configsFile))["imageID"]
    source_type           = "image"
    volume_size           = yamldecode(file(var.configsFile))["storageCapacity"]
    boot_index            = 0
    destination_type      = "volume"
    delete_on_termination = true
    #volume_type           = "SSD"
  }
}

# Associate the IPs to VMs
resource "flexibleengine_compute_floatingip_associate_v2" "server-fip-assoc" {
  count = var.customCount
  floating_ip = element(var.staticIPs, count.index)
  instance_id = element(flexibleengine_compute_instance_v2.kubenode.*.id, count.index)
}
