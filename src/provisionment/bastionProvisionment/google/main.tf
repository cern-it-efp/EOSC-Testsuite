provider "google" {
  credentials = file("/home/ipelu/Desktop/dsktp/rosetta_ialum.json")
  project     = "u-129e7a54-90a9-4371-95be"
}

# User defined when importing the pub key (project scope SSH key) via UI
variable "openUser" {
  default = "openu"
}
variable "pubKey" {
  default = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAgQCFPaN62APTqDCy3eB6qy+ALngWKg/RHCU0XWlL47JQ/Bj4zjHoyviFQ3+WgRgRxakKSdbpRU28qm0dUT+5Ki72doEmcmmqdzwhTa6H/0XwoeeRc12eIUw/sn2wTgdf/c57ft0deOyxeALVArAZwCXxywNeRcAjGJsvp4LW6jjZFQ=="
}

resource "google_compute_instance" "launcher" {
 name         = "launcher"
 machine_type = "n1-standard-2"
 zone         = "us-central1-a"
 boot_disk {
   initialize_params {
     image = "centos-cloud/centos-7"
     size = 150 # null equals to 20
   }
 }
 network_interface {
   network = "default"
   access_config {}
 }
 metadata = {
   ssh-keys = "${var.openUser}:${var.pubKey}"
 }
}
