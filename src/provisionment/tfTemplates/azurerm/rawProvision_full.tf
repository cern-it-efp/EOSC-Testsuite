provider "azurerm" {
  subscription_id = yamldecode(file(var.configsFile))["subscriptionId"]
  features {}
}

# Create one virtual network
resource "azurerm_virtual_network" "myterraformnetwork" {
  name                = "myVnet"
  address_space       = ["10.0.0.0/16"]
  location            = yamldecode(file(var.configsFile))["location"]
  resource_group_name = yamldecode(file(var.configsFile))["resourceGroupName"]
}

# Create one subnet
resource "azurerm_subnet" "myterraformsubnet" {
  name                 = "mySubnet"
  resource_group_name = yamldecode(file(var.configsFile))["resourceGroupName"]
  virtual_network_name = azurerm_virtual_network.myterraformnetwork.name
  address_prefixes       = ["10.0.1.0/24"]
}

# Create public IPs
resource "azurerm_public_ip" "terraformpublicip" {
  count = var.customCount
  name                = "myPublicIP${count.index}-${var.clusterRandomID}"
  location            = yamldecode(file(var.configsFile))["location"]
  resource_group_name = yamldecode(file(var.configsFile))["resourceGroupName"]
  allocation_method   = "Dynamic"
}

# Create NICs
resource "azurerm_network_interface" "terraformnic" {
  depends_on = [azurerm_subnet.myterraformsubnet]
  count                     = var.customCount
  name                      = "myNIC${count.index}-${var.clusterRandomID}"
  location                  = yamldecode(file(var.configsFile))["location"]
  resource_group_name       = yamldecode(file(var.configsFile))["resourceGroupName"]
  ip_configuration {
    name                          = "myNicConfiguration"
    subnet_id                     = azurerm_subnet.myterraformsubnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = element(azurerm_public_ip.terraformpublicip.*.id, count.index)
  }
}

# Create VMs
resource "azurerm_virtual_machine" "kubenode" {
  count                 = var.customCount
  name                  = "${var.instanceName}-${count.index}"
  location              = yamldecode(file(var.configsFile))["location"]
  resource_group_name   = yamldecode(file(var.configsFile))["resourceGroupName"]
  vm_size               = var.flavor
  network_interface_ids = [element(azurerm_network_interface.terraformnic.*.id, count.index)]
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
      key_data = yamldecode(file(var.configsFile))["pubSSH"]
      path     = "/home/${yamldecode(file(var.configsFile))["openUser"]}/.ssh/authorized_keys"
    }
  }
}
