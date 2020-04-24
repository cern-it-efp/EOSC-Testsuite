provider "google" {
  credentials = file("~/Desktop/.gcp.json")
  project     = "ocrets"
}

# User defined when importing the pub key (project scope SSH key) via UI
variable "openUser" {
  default = "openu"
}

resource "google_compute_instance" "launcher" {
 name         = "launcher"
 machine_type = "n1-highmem-16"
 zone         = "us-west1-a"
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

# ~~~~~~~~~~~~~~

resource "null_resource" "docker" {
  connection {
    host = google_compute_instance.launcher.network_interface.0.access_config.0.nat_ip
    user        = var.openUser
    private_key = file("~/.ssh/id_rsa")
  }
  provisioner "remote-exec" {
    inline = [
      "sudo yum update -y ; sudo yum install docker -y ; systemctl start docker",
      "sudo docker run --name tslauncher -itd --net=host cernefp/tslauncher",
      "echo sudo docker exec -it tslauncher bash >> ~/.bashrc"
    ]
  }
}
