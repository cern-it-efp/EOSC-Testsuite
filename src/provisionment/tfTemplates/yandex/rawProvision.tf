terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
}

provider "yandex" {
  service_account_key_file = yamldecode(file(var.configsFile))["serviceAccountKeyFile"]
  cloud_id                 = yamldecode(file(var.configsFile))["cloudID"]
  folder_id                = yamldecode(file(var.configsFile))["folderID"]
  zone                     = yamldecode(file(var.configsFile))["zone"]
}

resource "random_string" "id" {
  length  = 5
  special = false
  upper   = false
}

resource "yandex_vpc_network" "network" {
  name = "tsn-${random_string.id.result}"
}

resource "yandex_vpc_subnet" "subnet" {
  name = "tssn-${random_string.id.result}"
  v4_cidr_blocks = ["10.2.0.0/16"]
  zone       = yamldecode(file(var.configsFile))["zone"]
  network_id = yandex_vpc_network.network.id
}

resource "yandex_vpc_security_group" "group" {
  name = "ts-secgroup-${random_string.id.result}"
  network_id  = "${yandex_vpc_network.network.id}"
  ingress {
    protocol       = "ANY"
    v4_cidr_blocks = ["0.0.0.0/0"]
    port           = -1
  }
  egress {
    protocol       = "ANY"
    port           = -1
    v4_cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "yandex_compute_instance" "kubenode" {
  count = var.customCount
  name        = "${var.instanceName}-${count.index}"
  platform_id = yamldecode(file(var.configsFile))["platformID"]
  zone        = yamldecode(file(var.configsFile))["zone"]

  resources {
    cores  = yamldecode(file(var.configsFile))["flavor"]["cores"]
    memory = yamldecode(file(var.configsFile))["flavor"]["memory"]
  }

  boot_disk {
    initialize_params {
      image_id = yamldecode(file(var.configsFile))["imageID"]
      size     = yamldecode(file(var.configsFile))["storageCapacity"]
    }
  }

  network_interface {
    subnet_id = yandex_vpc_subnet.subnet.id
    nat = true
    security_group_ids = [yandex_vpc_security_group.group.id]
  }

  metadata = {
    ssh-keys = "yandex:${file(yamldecode(file(var.configsFile))["pathToPubKey"])}"
  }
}
