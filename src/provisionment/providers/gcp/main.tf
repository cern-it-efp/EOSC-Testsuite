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
