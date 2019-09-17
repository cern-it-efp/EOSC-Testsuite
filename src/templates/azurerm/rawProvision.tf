provider "azurerm" {
}

resource "azurerm_network_interface" "terraformnic" {
  count                     = "${var.customCount}"
  name                      = "myNIC${count.index}-${var.clusterRandomID}"
  location                  = "${var.location}"
  resource_group_name       = "${var.resourceGroupName}"
  network_security_group_id = "${var.secGroupId}"
  ip_configuration {
    name                          = "myNicConfiguration"
    subnet_id                     = "${var.subnetId}"
    private_ip_address_allocation = "Dynamic"
  }
}

resource "azurerm_virtual_machine" "kubenode" {
  count                 = "${var.customCount}"
  name                  = "${var.instanceName}-${count.index}"
  location              = "${var.location}"
  resource_group_name   = "${var.resourceGroupName}"
  vm_size               = "${var.vmSize}"
  network_interface_ids = [element(azurerm_network_interface.terraformnic.*.id, count.index)]
  storage_os_disk {
    name              = "myOsDisk${count.index}-${var.clusterRandomID}"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Premium_LRS"
  }
  storage_image_reference {
    publisher = "${var.publisher}"
    offer     = "${var.offer}"
    sku       = "${var.sku}"
    version   = "${var.imageVersion}"
  }
  os_profile {
    computer_name  = "${var.instanceName}-${count.index}"
    admin_username = "${var.openUser}"
  }
  os_profile_linux_config {
    disable_password_authentication = true
    ssh_keys {
      key_data = "${var.pubSSH}"
      path     = "/home/${var.openUser}/.ssh/authorized_keys"
    }
  }
}
