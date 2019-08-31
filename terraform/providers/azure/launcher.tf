provider "azurerm" {}

variable "avar" {
  default = "~/afiletf" # debug
}

# Create virtual network (This can actually be done IN ADVANCE)
resource "azurerm_virtual_network" "myterraformnetwork" {
  name                = "myVnet"
  address_space       = ["10.0.0.0/16"]
  location            = "France Central"
  resource_group_name = "ocrets"
}

# Create subnet (This can actually be done IN ADVANCE)
resource "azurerm_subnet" "myterraformsubnet" {
  name                 = "mySubnet"
  resource_group_name  = "ocrets"
  virtual_network_name = "${azurerm_virtual_network.myterraformnetwork.name}"
  address_prefix       = "10.0.1.0/24"
}

# Create Network Security Group and rule (This can actually be done IN ADVANCE, like on Exoscale or Openstack as it is just one for all the VMs)
resource "azurerm_network_security_group" "myterraformnsg" {
  name                = "myNetworkSecurityGroup"
  location            = "France Central"
  resource_group_name = "ocrets"

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

# Create public IPs
resource "azurerm_public_ip" "myterraformpublicip" {
  name                = "myPublicIP"
  location            = "France Central"
  resource_group_name = "ocrets"
  allocation_method   = "Dynamic"
}

# Create network interface (This CAN'T be done in advance, as I need one per VM: too much GUI work)
resource "azurerm_network_interface" "terraformnic" {
  name                      = "myNIC"
  location                  = "France Central"
  resource_group_name       = "ocrets"
  network_security_group_id = "${azurerm_network_security_group.myterraformnsg.id}"

  ip_configuration {
    name                          = "myNicConfiguration"
    subnet_id                     = "${azurerm_subnet.myterraformsubnet.id}"
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = "${azurerm_public_ip.myterraformpublicip.id}"
  }
}

############################################### CREATE VM ###############################################

resource "azurerm_virtual_machine" "main" {
  name                  = "launcher" #NAME
  location              = "France Central"
  vm_size               = "Standard_D2s_v3"
  resource_group_name   = "ocrets"
  network_interface_ids = ["${azurerm_network_interface.terraformnic.id}"]

  storage_os_disk {
    name              = "myOsDisk"
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
    computer_name  = "myvm"
    admin_username = "uroot"
  }

  os_profile_linux_config {
    disable_password_authentication = true

    ssh_keys {
      key_data = "ssh-rsa ..."
      path     = "/home/uroot/.ssh/authorized_keys"
    }
  }
}
