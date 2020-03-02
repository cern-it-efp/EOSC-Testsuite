provider "google" {
  credentials = file("~/Desktop/.gcp.json")
  project     = "ocrets"
}

# The user defined when importing the pub key (project scope SSH key) via GUI
variable "openUser" {
  default = "openu"
}

// A single Google Cloud Engine instance
resource "google_compute_instance" "launcher" {
 name         = "launcher"
 machine_type = "n1-highmem-16"
 zone         = "us-west1-a"

 ####### to allocate gpu ###############
 #guest_accelerator {
#   type = "nvidia-tesla-p100"
#   count = 1
# }
# scheduling {
#   on_host_maintenance = "TERMINATE"
 #}
 #######################################

 boot_disk {
   initialize_params {
     image = "centos-cloud/centos-7"
     size = 50
   }
 }

 network_interface {
   network = "default"
   access_config {}
 }
}

resource null_resource "allow_root" {
  provisioner "remote-exec" {
    connection {
      host        = google_compute_instance.launcher.network_interface.0.access_config.0.nat_ip
      type        = "ssh"
      user        = var.openUser
      private_key = file("~/.ssh/id_rsa")
    }
    inline = [
      "sudo mkdir /root/.ssh",
      "sudo cp /home/${var.openUser}/.ssh/authorized_keys /root/.ssh",
      "sudo sed -i 's/PermitRootLogin no/PermitRootLogin yes/g' /etc/ssh/sshd_config",
      "sudo systemctl restart sshd"
    ]
  }
}
