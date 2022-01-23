provider "azurerm" {
  subscription_id = yamldecode(file(var.configsFile))["subscriptionId"]
  features {}
}

resource "random_string" "id" {
  length  = 5
  special = false
  upper   = false
}

# Create one virtual network
resource "azurerm_virtual_network" "network" {
  name                = "ts-vnet-${random_string.id.result}"
  address_space       = ["10.0.0.0/16"]
  location            = yamldecode(file(var.configsFile))["location"]
  resource_group_name = yamldecode(file(var.configsFile))["resourceGroupName"]
}

# Create one subnet
resource "azurerm_subnet" "subnet" {
  name                 = "ts-subnet-${random_string.id.result}"
  resource_group_name  = yamldecode(file(var.configsFile))["resourceGroupName"]
  virtual_network_name = azurerm_virtual_network.network.name
  address_prefixes     = ["10.0.1.0/24"]
}

# Create security group with inbound and outbound rules
resource "azurerm_network_security_group" "security_group" {
  name                = "ts-secgroup-${random_string.id.result}"
  location            = yamldecode(file(var.configsFile))["location"]
  resource_group_name = yamldecode(file(var.configsFile))["resourceGroupName"]

  security_rule {
    name                       = "inbound_rule"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
  security_rule {
    name                       = "outbound_rule"
    priority                   = 100
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

# Associate security group to network
resource "azurerm_subnet_network_security_group_association" "association" {
  subnet_id                 = azurerm_subnet.subnet.id
  network_security_group_id = azurerm_network_security_group.security_group.id
}

# Create public IPs
resource "azurerm_public_ip" "publicip" {
  count = var.customCount
  name                = "ts-publicIP${count.index}-${random_string.id.result}"
  location            = yamldecode(file(var.configsFile))["location"]
  resource_group_name = yamldecode(file(var.configsFile))["resourceGroupName"]
  allocation_method   = "Dynamic"
}

# Create NICs
resource "azurerm_network_interface" "nic" {
  depends_on = [azurerm_subnet.subnet]
  count                     = var.customCount
  name                      = "ts-nic${count.index}-${random_string.id.result}"
  location                  = yamldecode(file(var.configsFile))["location"]
  resource_group_name       = yamldecode(file(var.configsFile))["resourceGroupName"]
  ip_configuration {
    name                          = "nicConfiguration"
    subnet_id                     = azurerm_subnet.subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = element(azurerm_public_ip.publicip.*.id, count.index)
  }
}

# Create CPU VMs
resource "azurerm_virtual_machine" "kubenode" {
  count                 = var.isGPUcluster ? 0 : var.customCount
  name                  = "${var.instanceName}-${count.index}"
  location              = yamldecode(file(var.configsFile))["location"]
  resource_group_name   = yamldecode(file(var.configsFile))["resourceGroupName"]
  vm_size               = var.flavor
  network_interface_ids = [element(azurerm_network_interface.nic.*.id, count.index)]
  delete_os_disk_on_termination = true

  storage_os_disk {
    name              = "ts-osdisk-${count.index}-${random_string.id.result}"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    disk_size_gb      = var.storageCapacity
  }

  storage_image_reference {
    publisher = yamldecode(file(var.configsFile))["image"]["publisher"]
    offer     = yamldecode(file(var.configsFile))["image"]["offer"]
    sku       = yamldecode(file(var.configsFile))["image"]["sku"]
    version   = yamldecode(file(var.configsFile))["image"]["version"]
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

# Create GPU VMs
resource "azurerm_virtual_machine" "kubenode_gpu" {
  count                 = var.isGPUcluster ? var.customCount : 0
  name                  = "${var.instanceName}-${count.index}"
  location              = yamldecode(file(var.configsFile))["location"]
  resource_group_name   = yamldecode(file(var.configsFile))["resourceGroupName"]
  vm_size               = var.flavor
  network_interface_ids = [element(azurerm_network_interface.nic.*.id, count.index)]
  delete_os_disk_on_termination = true

  storage_os_disk {
    name              = "ts-osdisk-${count.index}-${random_string.id.result}"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    disk_size_gb      = var.storageCapacity
  }

  # Required when creating a VM from a Marketplace image (i.e. Nvidia's). Fails for OpenLogic
  plan {
    publisher = yamldecode(file(var.configsFile))["image"]["publisher"] # publisher
    name      = yamldecode(file(var.configsFile))["image"]["sku"] # sku
    product   = yamldecode(file(var.configsFile))["image"]["offer"] # offer
  }

  storage_image_reference {
    publisher = yamldecode(file(var.configsFile))["image"]["publisher"]
    offer     = yamldecode(file(var.configsFile))["image"]["offer"]
    sku       = yamldecode(file(var.configsFile))["image"]["sku"]
    version   = yamldecode(file(var.configsFile))["image"]["version"]
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
