variable "configsPath" { default = "" }

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

variable "domainName" {  default = "OTC-EU-DE-00000000001000046175" }

variable "tenantName" {  default = "eu-de" }

variable "imageID" {
  default = "6cc1f24a-f081-45c7-bd71-abe3fbc759f7" # Ubuntu 18.04 AI Environment
  #default = "b1b0db52-4c6c-46d4-892d-ff7b23d46968" # OTC-Automated-AI-CondaImage
}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

provider "opentelekomcloud" {
  access_key = yamldecode(file(var.configsPath))["access_key"]
  secret_key = yamldecode(file(var.configsPath))["secret_key"]
  domain_name = var.domainName
  tenant_name = var.tenantName
  auth_url    = "https://iam.eu-de.otc.t-systems.com/v3"
}

resource "opentelekomcloud_compute_instance_v2" "enganvm" {
  name = yamldecode(file(var.configsPath))["vmName"]
  flavor_name = yamldecode(file(var.configsPath))["flavor_name"]
  key_pair = yamldecode(file(var.configsPath))["key_pair"]
  security_groups = yamldecode(file(var.configsPath))["security_groups"]
  availability_zone = yamldecode(file(var.configsPath))["availabilityZone"]
  #network { # requires the ID as 'name'
  #  name = var.networkID # var.networkName
  #}
  block_device {
    uuid                  = var.imageID
    source_type           = "image"
    volume_size           = yamldecode(file(var.configsPath))["storageCapacity"]
    boot_index            = 0
    destination_type      = "volume"
    delete_on_termination = true
    volume_type           = "SATA"
  }
}

resource "opentelekomcloud_compute_floatingip_associate_v2" "myip" {
  floating_ip = yamldecode(file(var.configsPath))["public_ip"]
  instance_id = opentelekomcloud_compute_instance_v2.enganvm.id
}

resource null_resource "allow_root" {
  depends_on = [opentelekomcloud_compute_floatingip_associate_v2.myip]
  provisioner "remote-exec" {
    connection {
      host        = yamldecode(file(var.configsPath))["public_ip"]
      type        = "ssh"
      user        = "ubuntu"
      private_key = file(yamldecode(file(var.configsPath))["sshKey"])
    }
    inline = [
      "sudo mkdir /root/.ssh",
      "sudo cp /home/ubuntu/.ssh/authorized_keys /root/.ssh",
      "sudo sed -i 's/PermitRootLogin forced-commands-only/PermitRootLogin yes/g' /etc/ssh/sshd_config",
      "sudo systemctl restart sshd"
    ]
  }
}

resource null_resource "ai_stack_custom" {
  depends_on = [null_resource.allow_root]
  connection {
    host        = yamldecode(file(var.configsPath))["public_ip"]
    type        = "ssh"
    user        = "root"
    private_key = file(yamldecode(file(var.configsPath))["sshKey"])
  }
  provisioner "file" {
   source      = "otc_custom_image_config_TF1.sh"
   destination = "/tmp/otc_custom_image_config_TF1.sh"
 }
 provisioner "remote-exec" {
   inline = [
     "bash /tmp/otc_custom_image_config_TF1.sh",
   ]
 }
}
