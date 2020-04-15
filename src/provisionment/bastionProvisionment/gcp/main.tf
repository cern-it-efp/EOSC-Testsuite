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
