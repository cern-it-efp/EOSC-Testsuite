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
  count                      = var.amount
  name                      = "myNIC${count.index}" # this needs to have on the name the randomId of the node it will be linked to
  location                  = "${var.location}"
  resource_group_name       = "${var.resourceGroupName}"
  network_security_group_id = "${azurerm_network_security_group.myterraformnsg.id}"
  ip_configuration {
    name                          = "myNicConfiguration"
    subnet_id                     = "${azurerm_subnet.myterraformsubnet.id}"
    private_ip_address_allocation = "Dynamic"
  }
}
