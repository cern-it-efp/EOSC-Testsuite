provider "azurerm" {
  subscription_id = yamldecode(file(var.configsFile))["subscriptionId"]
  features {}
}

resource "azurerm_network_interface" "terraformnic" {
  count                     = var.customCount
  name                      = "myNIC${count.index}-${var.clusterRandomID}"
  location                  = yamldecode(file(var.configsFile))["location"]
  resource_group_name       = yamldecode(file(var.configsFile))["resourceGroupName"]
  ip_configuration {
    name                          = "myNicConfiguration"
    subnet_id                     = yamldecode(file(var.configsFile))["subnetId"]
    private_ip_address_allocation = "Dynamic"
  }
}

resource "azurerm_virtual_machine" "kubenode" {
  count                 = var.customCount
  name                  = "${var.instanceName}-${count.index}"
  location              = yamldecode(file(var.configsFile))["location"]
  resource_group_name   = yamldecode(file(var.configsFile))["resourceGroupName"]
  vm_size               = yamldecode(file(var.configsFile))["flavor"]
  network_interface_ids = [element(azurerm_network_interface.terraformnic.*.id, count.index)]
  delete_os_disk_on_termination = true

  storage_os_disk {
    name              = "myOsDisk${count.index}-${var.clusterRandomID}"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Premium_LRS"
  }
  storage_image_reference {
    publisher = var.publisher
    offer     = var.offer
    sku       = var.sku
    version   = var.imageVersion
  }
  os_profile {
    computer_name  = "${var.instanceName}-${count.index}"
    admin_username = yamldecode(file(var.configsFile))["openUser"]
  }
  os_profile_linux_config {
    disable_password_authentication = true
    ssh_keys {
      key_data = yamldecode(file(var.configsFile))["pubSSH"]
      path     = "/home/${yamldecode(file(var.configsFile))["openUser"]}/.ssh/authorized_keys"
    }
  }
}
