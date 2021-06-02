variable "configsFile" {
  default = "/home/ipelu/p.yaml"
}
variable "customCount" {
  default = 1 # TODO: this is calculated according to the number of tests selected
}

# -----------------------------------------

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
  username = yamldecode(file(var.configsFile))["username"]
  password = yamldecode(file(var.configsFile))["password"]
}

resource "cloudsigma_drive" "os_drive" {
  count = var.customCount
  clone_drive_id = yamldecode(file(var.configsFile))["clone_drive_id"]
  media = "disk"
  name  = "os-drive"
  size  = yamldecode(file(var.configsFile))["size"]
}

resource "cloudsigma_ssh_key" "key" {
  name       = "key"
  public_key = file(yamldecode(file(var.configsFile))["pub_key_path"])
}

resource "cloudsigma_server" "server" {
  count = var.customCount
  cpu          = yamldecode(file(var.configsFile))["cpu"]
  memory       = yamldecode(file(var.configsFile))["memory"]
  name         = "server"
  vnc_password = random_password.psswd.result
  drive {
    uuid = element(cloudsigma_drive.os_drive.*.uuid, count.index)
  }
  ssh_keys = [cloudsigma_ssh_key.key.uuid]
}
