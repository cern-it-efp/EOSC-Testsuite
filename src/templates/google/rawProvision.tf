provider "google" {
  credentials = file(var.credentials)
  project     = "${var.project}"
}

resource "google_compute_instance" "kubenode" {

  count        = "${var.customCount}"
  machine_type = "${var.machineType}" # "n1-standard-2"
  name         = "${var.instanceName}-${count.index}"
  zone         = "${var.zone}" # "us-west1-a"

  boot_disk {
    initialize_params {
      image = "${var.image}" # "centos-cloud/centos-7"
      size  = 100
    }
  }
  network_interface {
    network = "default"
    access_config {}
  }

  # Extra stuff for GPU
  guest_accelerator {
    count = "${var.gpuCount}" # in case the GAN test is set, this has to be used
    type  = "${var.gpuType}"  # "nvidia-tesla-p100"
  }
  scheduling {
    on_host_maintenance = "TERMINATE"
  }
  ############################

  ############################
  # key pairs: The general example uses project-wide SSH keys: user linked to a SSH key defined at project level, these can access all the VMs under the project unless specified (checked "Block project-wide SSH keys")
  # Sec. groups: VMs connected to the "default" network have the right traffic
  ############################

}
