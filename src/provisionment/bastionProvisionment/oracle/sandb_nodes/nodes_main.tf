variable "subnet_id" {
  default = "ocid1.subnet.oc1.eu-frankfurt-1.aaaaaaaan3gvymfka62o3zp76uwdhxh4i6xqjsexob6mrtpdtttqjfxom43q"
}
variable "auth" {
  default = "/home/ipelu/Desktop/oracle.yaml"
}
variable "instance_shape" {
  default = "VM.Standard1.1"
}
variable "region" {
  default = "eu-frankfurt-1"
}
variable "availability_domain" {
  default = "BKrI:EU-FRANKFURT-1-AD-1"
}
variable "private_key_path" {
  default = "/home/ipelu/.ssh/oracle.pem"
}
variable "ssh_public_key_path" {
  default = "/home/ipelu/.ssh/oracle.pub" # no pem
}
variable "diskSize" {
  default = 50
}
variable "fingerprint" {
  default = "d9:5a:05:58:e5:3a:d3:86:1b:6c:09:d5:70:99:83:ca"
}
variable "image_ocid" {
  #default = "ocid1.image.oc1.eu-frankfurt-1.aaaaaaaawtnpiyjp36tyx7hkkymil2efkvitkrrnqi5qjpahcuoyvtcwhc5q" # Ubuntu 18.04
  default = "ocid1.image.oc1.eu-frankfurt-1.aaaaaaaagjbl7scqx2wfepx4ztdvndjiua2fofrmujbjyhuodsmysijwu7wq" # Ubuntu 16.04
  #default = "ocid1.image.oc1.eu-frankfurt-1.aaaaaaaa6zpubgqnm3j46smrd7fjehmmj3emusyfljypxcwzrmlcnuno7gra" # CentOS 7
}
# ---------------------------------------------------

provider "oci" {
  tenancy_ocid = yamldecode(file(var.auth))["tenancy_ocid"]
  user_ocid = yamldecode(file(var.auth))["user_ocid"]
  fingerprint = var.fingerprint
  private_key_path = var.private_key_path
  region = var.region
}

resource "oci_core_instance" "kubenode" {
  count = 3
  display_name        = "node-${count.index}"
  availability_domain = var.availability_domain
  compartment_id      = yamldecode(file(var.auth))["compartment_ocid"]
  shape               = var.instance_shape

  create_vnic_details {
    subnet_id        = var.subnet_id
    assign_public_ip = true
    #assign_public_ip = false # public IPs are prohibited in the subnet created by OKE
  }
  source_details {
    source_type = "image"
    source_id   = var.image_ocid
    boot_volume_size_in_gbs = var.diskSize
  }
  metadata = {
    ssh_authorized_keys = file(var.ssh_public_key_path)
  }
}
