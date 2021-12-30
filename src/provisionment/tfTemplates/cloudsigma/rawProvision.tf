terraform {
  required_providers {
    cloudsigma = {
      source  = "cloudsigma/cloudsigma"
    }
  }
}

resource "random_password" "psswd" {
  length  = 12
  special = true
}

provider "cloudsigma" {
  location = yamldecode(file(var.configsFile))["location"]
  username = yamldecode(file(yamldecode(file(var.configsFile))["authFile"]))["username"]
  password = yamldecode(file(yamldecode(file(var.configsFile))["authFile"]))["password"]
}

# ID String for resources
resource "random_string" "id" {
  length  = 5
  special = false
  upper   = false
}

resource "cloudsigma_drive" "os_drive" {
  count = var.customCount
  clone_drive_id = yamldecode(file(var.configsFile))["clone_drive_id"]
  media = "disk"
  name  = "os-drive-${random_string.id.result}"
  size  = yamldecode(file(var.configsFile))["storageCapacity"]
}

resource "cloudsigma_ssh_key" "key" {
  name       = "ts-key-${random_string.id.result}"
  public_key = file(yamldecode(file(var.configsFile))["pathToPubKey"])
}

resource "cloudsigma_server" "server" {
  count = var.useStaticIPs ? 0 : var.customCount
  cpu          = yamldecode(file(var.configsFile))["flavor"]["cpu"]
  memory       = yamldecode(file(var.configsFile))["flavor"]["memory"]
  name         = "${var.instanceName}-${count.index}"
  vnc_password = random_password.psswd.result
  drive {
    uuid = element(cloudsigma_drive.os_drive.*.uuid, count.index)
  }
  ssh_keys = [cloudsigma_ssh_key.key.uuid]
}

resource "cloudsigma_server" "server_staticIPs" {
  count = var.useStaticIPs ? var.customCount : 0
  cpu          = yamldecode(file(var.configsFile))["flavor"]["cpu"]
  memory       = yamldecode(file(var.configsFile))["flavor"]["memory"]
  name         = "${var.instanceName}-${count.index}"
  vnc_password = random_password.psswd.result
  drive {
    uuid = element(cloudsigma_drive.os_drive.*.uuid, count.index)
  }
  network {
    ipv4_address = element(var.staticIPs, count.index)
    type         = "static"
  }
  ssh_keys = [cloudsigma_ssh_key.key.uuid]
}
