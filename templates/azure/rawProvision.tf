provider "azurerm" {
}

resource "azurerm_virtual_network" "myterraformnetwork" {
  name                = "myVnet"
  address_space       = ["10.0.0.0/16"]
  location            = "${var.location}"
  resource_group_name = "${var.resourceGroupName}"
}

resource "azurerm_subnet" "myterraformsubnet" {
  name                 = "mySubnet"
  location             = "${var.location}"
  resource_group_name  = "${var.resourceGroupName}"
  virtual_network_name = "${azurerm_virtual_network.myterraformnetwork.name}"
  address_prefix       = "10.0.1.0/24"
}

resource "azurerm_network_security_group" "myterraformnsg" {
  name                = "myNetworkSecurityGroup"
  location            = "${var.location}"
  resource_group_name = "${var.resourceGroupName}"

  security_rule {
    name                       = "SSH"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }
}

resource "azurerm_network_interface" "terraformnic" {
  count                     = "${var.amount}"
  name                      = "myNIC${count.index}-${var.clusterRandomID}"
  location                  = "${var.location}"
  resource_group_name       = "${var.resourceGroupName}"
  network_security_group_id = "${azurerm_network_security_group.myterraformnsg.id}"
  ip_configuration {
    name                          = "myNicConfiguration"
    subnet_id                     = "${azurerm_subnet.myterraformsubnet.id}"
    private_ip_address_allocation = "Dynamic"
  }
}

resource "azurerm_virtual_machine" "kubenode" {
  count                 = "${var.amount}"
  name                  = "${var.instanceName}"
  location              = "${var.location}"
  resource_group_name   = "${var.resourceGroupName}"
  network_interface_ids = [element(azurerm_network_interface.terraformnic.*.id, count.index)]
  storage_os_disk {
    name              = "myOsDisk${count.index}-${var.clusterRandomID}"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Premium_LRS"
  }
  storage_image_reference {
    publisher = "OpenLogic"
    offer     = "CentOS"
    sku       = "7.5"
    version   = "latest"
  }
  os_profile {
    computer_name  = "${var.instanceName}"
    admin_username = "${var.openUser}"
  }
  os_profile_linux_config {
    disable_password_authentication = true
    ssh_keys {
      key_data = "${var.pubSSH}"
      path     = "/home/${var.openUser}/.ssh/authorized_keys"
    }
  }
  provisioner "remote-exec" {
    connection {
      host        = element(azurerm_network_interface.terraformnic.*.private_ip_address, count.index)
      type        = "ssh"
      user        = "${var.openUser}"
      private_key = file("~/.ssh/id_rsa")
      timeout     = "30m"
    }
    inline = ["sudo mkdir /root/.ssh ; sudo cp /home/${var.openUser}/.ssh/authorized_keys /root/.ssh"]
  }
}
