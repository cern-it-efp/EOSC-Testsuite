# TODO: add 'region'

terraform {
  required_providers {
    openstack = {
      source = "terraform-provider-openstack/openstack"
    }
  }
}

provider "openstack" {}

# ID String for resources
resource "random_string" "id" {
  length  = 5
  special = false
  upper   = false
}

# Create network
resource "openstack_networking_network_v2" "network" {
  name           = "ts-network-${random_string.id.result}"
  admin_state_up = "true"
}

# Create subnetwork
resource "openstack_networking_subnet_v2" "subnet" {
  name       = "ts-subnet-${random_string.id.result}"
  network_id = openstack_networking_network_v2.network.id
  cidr       = "10.1.0.0/24"
  dns_nameservers = ["8.8.8.8"]
}

# Create router
resource "openstack_networking_router_v2" "router" {
  name                = "ts-router-${random_string.id.result}"
  admin_state_up      = true
  external_network_id = yamldecode(file(var.configsFile))["externalNetID"]
}

# Connect router to subnet
resource "openstack_networking_router_interface_v2" "router_iface" {
  router_id = openstack_networking_router_v2.router.id
  subnet_id = openstack_networking_subnet_v2.subnet.id
}

# Get floating IPs
resource "openstack_networking_floatingip_v2" "floating_ip" {
  count = var.customCount
  pool = yamldecode(file(var.configsFile))["IPpool"]
}

# Create security group
resource "openstack_networking_secgroup_v2" "secgroup" {
  name        = "ts-secgroup-${random_string.id.result}"
}

# Add rules to the security group
resource "openstack_networking_secgroup_rule_v2" "secgroup_rule_ingress4" { # Egress exists by default for both v4 and v6
  direction         = "ingress"
  ethertype         = "IPv4"
  security_group_id = openstack_networking_secgroup_v2.secgroup.id
}
resource "openstack_networking_secgroup_rule_v2" "secgroup_rule_ingress6" {
  direction         = "ingress"
  ethertype         = "IPv6"
  security_group_id = openstack_networking_secgroup_v2.secgroup.id
}

# Create VMs
resource "openstack_compute_instance_v2" "server" {
  depends_on = [openstack_networking_subnet_v2.subnet]
  count = var.customCount
  name = "${var.instanceName}-${count.index}"
  #image_name = var.image
  image_id = yamldecode(file(var.configsFile))["imageID"]
  flavor_name = yamldecode(file(var.configsFile))["flavor"]
  security_groups = [openstack_networking_secgroup_v2.secgroup.name] # ["default","allow_ping_ssh_rdp"]
  #config_drive = "true"
  #power_state = "active"
  user_data     = "#cloud-config\n\nssh_authorized_keys:\n  - ${file(yamldecode(file(var.configsFile))["pathToPubKey"])}"
  network {
    uuid = openstack_networking_network_v2.network.id
  }
}

# Associate the IPs to VMs
resource "openstack_compute_floatingip_associate_v2" "server-fip-assoc" {
  count = var.customCount
  depends_on = [openstack_networking_router_interface_v2.router_iface]
  floating_ip = element(openstack_networking_floatingip_v2.floating_ip.*.address, count.index)
  instance_id = element(openstack_compute_instance_v2.server.*.id, count.index)
}
