variable "image_ocid" {
  default = "ocid1.image.oc1.eu-frankfurt-1.aaaaaaaawtnpiyjp36tyx7hkkymil2efkvitkrrnqi5qjpahcuoyvtcwhc5q" # Ubuntu 18.04
  #default = "ocid1.image.oc1.eu-frankfurt-1.aaaaaaaagjbl7scqx2wfepx4ztdvndjiua2fofrmujbjyhuodsmysijwu7wq" # Ubuntu 16.04
  #default = "ocid1.image.oc1.eu-frankfurt-1.aaaaaaaa6zpubgqnm3j46smrd7fjehmmj3emusyfljypxcwzrmlcnuno7gra" # CentOS 7
}
variable "openUser" {
  default = "ubuntu"
  #default = "opc"
}
variable "auth" {
  default = "/home/ipelu/Desktop/oracle.yaml"
}
variable "cidr_block_vcn" {
  default = "10.0.0.0/16"
}
variable "cidr_block_subnet" {
  default = "10.0.0.0/24"
}
variable "instance_shape" {
  default = "VM.Standard1.1"
}
variable "region" {
  default = "eu-frankfurt-1"
}
variable "availability_domain" {
  default = "BKrI:EU-FRANKFURT-1-AD-3"
}
variable "auth_private_key_path" {
  default = "/home/ipelu/.ssh/oracle.pem"
}
variable "ssh_private_key_path" {
  default = "/home/ipelu/.ssh/id_rsa"
}
variable "ssh_public_key_path" {
  default = "/home/ipelu/.ssh/id_rsa.pub" # no pem
}
variable "storageCapacity" {
  default = 50
}
variable "fingerprint" {
  default = "d9:5a:05:58:e5:3a:d3:86:1b:6c:09:d5:70:99:83:ca"
}

provider "oci" {
  tenancy_ocid = yamldecode(file(var.auth))["tenancy_ocid"]
  user_ocid = yamldecode(file(var.auth))["user_ocid"]
  fingerprint = var.fingerprint
  private_key_path = var.auth_private_key_path
  region = var.region
}

resource "oci_core_vcn" "tslauncher_vcn" {
  cidr_block     = var.cidr_block_vcn
  compartment_id = yamldecode(file(var.auth))["compartment_ocid"]
  dns_label = "vcnDNSlabel"
}

resource "oci_core_internet_gateway" "tslauncher_internet_gateway" {
  compartment_id = yamldecode(file(var.auth))["compartment_ocid"]
  vcn_id         = oci_core_vcn.tslauncher_vcn.id
}

resource "oci_core_default_route_table" "default_route_table" {
  manage_default_resource_id = oci_core_vcn.tslauncher_vcn.default_route_table_id
  route_rules {
    destination       = "0.0.0.0/0"
    destination_type  = "CIDR_BLOCK"
    network_entity_id = oci_core_internet_gateway.tslauncher_internet_gateway.id
  }
}

resource "oci_core_security_list" "tslauncher_security_list" {
  compartment_id = yamldecode(file(var.auth))["compartment_ocid"]
  vcn_id = oci_core_vcn.tslauncher_vcn.id

  egress_security_rules { # Egress: allow everything
    destination = "0.0.0.0/0"
    protocol = "all"
  }

  ingress_security_rules {
    source = "0.0.0.0/0"
    protocol = 1
    icmp_options {
      type = 8
    }
  }
  ingress_security_rules {
    source = "0.0.0.0/0"
    protocol = 1
    icmp_options {
      type = 0
    }
  }

  ingress_security_rules { # Ingress: ssh (tcp) / 22
    source = "0.0.0.0/0"
    protocol = 6
    tcp_options {
      max = 22
      min = 22
    }
  }

  ingress_security_rules { # Ingress: kube API (tcp) / 6443
    source = "0.0.0.0/0"
    protocol = 6
    tcp_options {
      max = 6443
      min = 6443
    }
  }

  ingress_security_rules { # Ingress: node access API (tcp) / 10250
    source = "0.0.0.0/0"
    protocol = 6
    tcp_options {
      max = 10250
      min = 10250
    }
  }

  ingress_security_rules { # Ingress: flannel network (udp) / 8472
    source = "0.0.0.0/0"
    protocol = 17
    udp_options {
      max = 8472
      min = 8472
    }
  }
}

resource "oci_core_subnet" "tslauncher_subnet" {
  cidr_block          = var.cidr_block_subnet
  compartment_id      = yamldecode(file(var.auth))["compartment_ocid"]
  vcn_id              = oci_core_vcn.tslauncher_vcn.id
  security_list_ids   = [oci_core_security_list.tslauncher_security_list.id]
  route_table_id      = oci_core_vcn.tslauncher_vcn.default_route_table_id
  dns_label = "subnetDNSlabel"
}

resource "oci_core_instance" "tslauncher_instance" {
  display_name        = "tslauncher"
  availability_domain = var.availability_domain
  compartment_id      = yamldecode(file(var.auth))["compartment_ocid"]
  shape               = var.instance_shape

  create_vnic_details {
    subnet_id        = oci_core_subnet.tslauncher_subnet.id
    assign_public_ip = true
  }
  source_details {
    source_type = "image"
    source_id   = var.image_ocid
    boot_volume_size_in_gbs = var.storageCapacity
  }
  metadata = {
    ssh_authorized_keys = file(var.ssh_public_key_path)
  }
}

# ~~~~~~~~~~~~~~

resource "null_resource" "docker" {
  connection {
    host = oci_core_instance.tslauncher_instance.public_ip
    user        = var.openUser
    private_key = file(var.ssh_private_key_path)
  }
  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update -y ; sudo apt-get install docker.io -y",
      "sudo docker run --name tslauncher -itd --net=host cernefp/tslauncher",
      "echo sudo docker exec -it tslauncher bash >> ~/.bashrc"
    ]
    #inline = [
    #  "sudo yum update -y ; sudo yum install docker -y",
    #  "sudo docker run -itd --net=host cernefp/tslauncher"
    #]
  }
}
