provider "google" {
  credentials = "${file("/gcp.json")}"
  project     = "ocrets"

}

resource "openstack_compute_instance_v2" "kubenode" {

  count                 = "${var.customCount}"
  machine_type = "n1-standard-2" # "${var.flavor}"
  name                  = "${var.instanceName}-${count.index}"
  zone         = "${var.zone}" # "us-west1-a"
  boot_disk {
    initialize_params {
      image = "${var.image}" # "centos-cloud/centos-7"
      size = 100
    }
  }

  network_interface {
    network = "default"
    access_config {}
  }

  # Extra stuff for GPU
  guest_accelerator {
    count = "${var.gpuCount}" # in case the GPU is set, this has to be used
    type = "${var.gpuType}" # "nvidia-tesla-p100"
  }
  scheduling {
    on_host_maintenance = "TERMINATE"
  }
  ############################



  key_pair = "${var.keyPair}"
  security_groups = var.securityGroups
  
}
