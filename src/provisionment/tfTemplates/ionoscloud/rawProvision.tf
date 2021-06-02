terraform {
  required_providers {
    ionoscloud = {
      source = "ionos-cloud/ionoscloud"
    }
  }
}

provider "ionoscloud" {
  username = yamldecode(file(var.configsFile))["username"]
  password = yamldecode(file(var.configsFile))["password"]
}

resource "ionoscloud_datacenter" "ionos_resource" {
  name        = "datacenter0"
  location    = yamldecode(file(var.configsFile))["location"]
}

resource "ionoscloud_lan" "ionos_resource" {
  datacenter_id = ionoscloud_datacenter.ionos_resource.id
  public        = true
}

resource "ionoscloud_server" "ionos_resource" {
  count = var.customCount
  name              = "${var.instanceName}-${count.index}"
  datacenter_id     = ionoscloud_datacenter.ionos_resource.id
  cores             = yamldecode(file(var.configsFile))["flavor"]["cores"]
  ram               = yamldecode(file(var.configsFile))["flavor"]["ram"]
  #availability_zone = "ZONE_1"
  #cpu_family        = "AMD_OPTERON" # docs say it defaults to AMD_OPTERON but it's actually INTEL_XEON
  ssh_key_path      = [yamldecode(file(var.configsFile))["pathToPubKey"]]
  image_name        = yamldecode(file(var.configsFile))["image_name"]

  volume {
    name           = "new"
    size           = yamldecode(file(var.configsFile))["storageCapacity"]
    disk_type      = "HDD"
  }

  nic {
    lan             = ionoscloud_lan.ionos_resource.id
    dhcp            = true
    #ip              = ionoscloud_ipblock.ionos_resource.ips[count.index]
    firewall_active = false
  }
}
