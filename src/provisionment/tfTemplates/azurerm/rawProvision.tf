provider "azurerm" {
  subscription_id = yamldecode(file(var.configsFile))["subscriptionId"]
  features {}
}

####################################################################################################

# Create one virtual network
resource "azurerm_virtual_network" "myterraformnetwork" {
  count = var.usePrivateIPs ? 0 : 1
  name                = "myVnet-${var.clusterRandomID}"
  address_space       = ["10.0.0.0/16"]
  location            = yamldecode(file(var.configsFile))["location"]
  resource_group_name = yamldecode(file(var.configsFile))["resourceGroupName"]
}

# Create one subnet
resource "azurerm_subnet" "myterraformsubnet" {
  count = var.usePrivateIPs ? 0 : 1
  name                 = "mySubnet-${var.clusterRandomID}"
  resource_group_name = yamldecode(file(var.configsFile))["resourceGroupName"]
  virtual_network_name = element(azurerm_virtual_network.myterraformnetwork.*.name, count.index)
  address_prefixes       = ["10.0.1.0/24"]
}

####################################################################################################

# Create public IPs
resource "azurerm_public_ip" "terraformpublicip" {
  count = var.customCount
  name                = "myPublicIP${count.index}-${var.clusterRandomID}"
  location            = yamldecode(file(var.configsFile))["location"]
  resource_group_name = yamldecode(file(var.configsFile))["resourceGroupName"]
  allocation_method   = "Dynamic"
}

# Create NICs
resource "azurerm_network_interface" "terraformnic_privateIPs" {
  depends_on = [azurerm_subnet.myterraformsubnet]
  count = var.usePrivateIPs ? var.customCount : 0
  name                      = "myNIC${count.index}-${var.clusterRandomID}"
  location                  = yamldecode(file(var.configsFile))["location"]
  resource_group_name       = yamldecode(file(var.configsFile))["resourceGroupName"]
  ip_configuration {
    name                          = "myNicConfiguration"
    subnet_id                     = yamldecode(file(var.configsFile))["subnetId"]
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = element(azurerm_public_ip.terraformpublicip.*.id, count.index)
  }
}
resource "azurerm_network_interface" "terraformnic_publicIPs" {
  depends_on = [azurerm_subnet.myterraformsubnet]
  count = var.usePrivateIPs ? 0 : var.customCount
  name                      = "myNIC${count.index}-${var.clusterRandomID}"
  location                  = yamldecode(file(var.configsFile))["location"]
  resource_group_name       = yamldecode(file(var.configsFile))["resourceGroupName"]
  ip_configuration {
    name                          = "myNicConfiguration"
    subnet_id                     = element(azurerm_subnet.myterraformsubnet.*.id, count.index)
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = element(azurerm_public_ip.terraformpublicip.*.id, count.index)
  }
}

####################################################################################################

# Create VMs
resource "azurerm_virtual_machine" "kubenode_privateIPs" {
  count = var.usePrivateIPs ? var.customCount : 0
  name                  = "${var.instanceName}-${count.index}"
  location              = yamldecode(file(var.configsFile))["location"]
  resource_group_name   = yamldecode(file(var.configsFile))["resourceGroupName"]
  vm_size               = var.flavor
  network_interface_ids = [element(azurerm_network_interface.terraformnic_privateIPs.*.id, count.index)]
  delete_os_disk_on_termination = true

  storage_os_disk {
    name              = "myOsDisk${count.index}-${var.clusterRandomID}"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Premium_LRS"
    disk_size_gb      = var.storageCapacity
  }

  plan {
    publisher = var.publisher
    name      = var.sku
    product   = var.offer
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
      key_data = file(yamldecode(file(var.configsFile))["pathToPubKey"])
      path     = "/home/${yamldecode(file(var.configsFile))["openUser"]}/.ssh/authorized_keys"
    }
  }
}
resource "azurerm_virtual_machine" "kubenode_publicIPs" {
  count = var.usePrivateIPs ? 0 : var.customCount
  name                  = "${var.instanceName}-${count.index}"
  location              = yamldecode(file(var.configsFile))["location"]
  resource_group_name   = yamldecode(file(var.configsFile))["resourceGroupName"]
  vm_size               = var.flavor
  network_interface_ids = [element(azurerm_network_interface.terraformnic_publicIPs.*.id, count.index)]
  delete_os_disk_on_termination = true

  storage_os_disk {
    name              = "myOsDisk${count.index}-${var.clusterRandomID}"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Premium_LRS"
    disk_size_gb      = var.storageCapacity
  }

  # fails for OpenLogic
  #plan {
  #  publisher = var.publisher
  #  name      = var.sku
  #  product   = var.offer
  #}

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
      key_data = file(yamldecode(file(var.configsFile))["pathToPubKey"])
      path     = "/home/${yamldecode(file(var.configsFile))["openUser"]}/.ssh/authorized_keys"
    }
  }
}
