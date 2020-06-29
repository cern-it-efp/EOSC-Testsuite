provider "google" {
  credentials = file(yamldecode(file(var.configsFile))["pathToCredentials"])
  project     = yamldecode(file(var.configsFile))["project"]
}

resource "google_compute_instance" "kubenode" {
  count        = var.customCount
  machine_type = var.flavor
  name         = "${var.instanceName}-${count.index}"
  zone         = yamldecode(file(var.configsFile))["zone"]

  metadata = {
    #ssh-keys = "${yamldecode(file(var.configsFile))["openUser"]}:${file(var.pathToPubKey)}" # WORKS: takes configs' pub. key
    #ssh-keys = "foobar" # WORKS: takes project-wide keys
    ssh-keys = var.gcp_keyAsMetadata # WORKS: dynamically done on python level
  }

  boot_disk {
    initialize_params {
      image = yamldecode(file(var.configsFile))["image"]
      size  = var.storageCapacity
    }
  }
  network_interface {
    network = "default"
    access_config {}
  }
  guest_accelerator { # Extra stuff for GPUs
    count = var.gpuCount
    type  = var.gpuType
  }
  scheduling { # Required when using GPUs
    on_host_maintenance = "TERMINATE"
  }
}
