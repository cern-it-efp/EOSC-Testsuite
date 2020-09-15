#variable "networkID" {
#  default = "2593d7a9-0ecd-4a19-b4bc-65ca2c62e1c7"
#}
variable "availabilityZone" {
  default = "eu-de-01"
}
variable "networkName" {
  default = "vpc-default"
}
variable "public_ip" {
  default = "80.158.55.22"
}
variable "openUser" {
  default = "ubuntu"
}
variable "keyPair" {
  default = "exo"
}
variable "storageCapacity" {
  default = 50
}
variable "flavor" { # https://open-telekom-cloud.com/resource/blob/data/173316/3c1e928bf9537cbef2b1407655a0d25c/open-telekom-cloud-service-description.pdf
  default = "s2.medium.4"
}
variable "imageID" {
  # default = "" # Centos
  default = "1616e0b6-503a-4698-946f-cf9942c4c73b" # Standard_Ubuntu_18.04_latest
}
variable "secGroups" {
  default = ["default","Sys-FullAccess"]
}
variable "authFile" {
  default = "/tsk.yaml"
}
# ------------------------------------------------------------------------------
variable "domain_name" {
  default = "OTC-EU-DE-00000000001000046175"
}
variable "tenant_name" {
  default = "eu-de" # project
}

provider "opentelekomcloud" {
  access_key = yamldecode(file(var.authFile))["accK"]
  secret_key = yamldecode(file(var.authFile))["secK"]
  domain_name = var.domain_name
  tenant_name = var.tenant_name
  auth_url    = "https://iam.eu-de.otc.t-systems.com/v3"
}

resource "opentelekomcloud_compute_instance_v2" "tslauncher" {
  name = "tslauncher"
  flavor_name = var.flavor
  key_pair = var.keyPair
  security_groups = var.secGroups
  availability_zone = var.availabilityZone
  #network { # requires the ID as 'name'
  #  name = var.networkID # var.networkName
  #}
  block_device {
    uuid                  = var.imageID
    source_type           = "image"
    volume_size           = var.storageCapacity
    boot_index            = 0
    destination_type      = "volume"
    delete_on_termination = true
    volume_type           = "SATA"
  }
}

resource "opentelekomcloud_compute_floatingip_associate_v2" "myip" {
  floating_ip = var.public_ip
  instance_id = opentelekomcloud_compute_instance_v2.tslauncher.id
}

resource "null_resource" "allow_root" {
  depends_on = [opentelekomcloud_compute_floatingip_associate_v2.myip]
  connection {
    type        = "ssh"
    host = var.public_ip
    user        = var.openUser
    private_key = file("~/.ssh/id_rsa")
  }
  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update -y ; sudo apt-get install docker.io -y",
      "sudo docker run --name tslauncher -itd --net=host cernefp/tslauncher",
      "echo sudo docker exec -it tslauncher bash >> ~/.bashrc"
    ]
  }
}
