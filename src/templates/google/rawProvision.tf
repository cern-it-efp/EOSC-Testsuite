provider "google" {
  credentials = file(var.credentials)
  project     = var.project
}

resource "google_compute_instance" "kubenode" {

  count        = var.customCount
  machine_type = var.machineType
  name         = "${var.instanceName}-${count.index}"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = var.image
      size  = 100
    }
  }
  network_interface {
    network = "default"
    access_config {}
  }

  # Extra stuff for GPU
  guest_accelerator {
    count = var.gpuCount # in case the GAN test is set, this has to be used
    type  = var.gpuType
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
