provider "azurerm" {
  subscription_id = "54f623f0-8c18-40dd-9530-d32d2f1ee14f"
}

# Create virtual network (This can actually be done IN ADVANCE)
resource "azurerm_virtual_network" "myterraformnetwork" {
  name                = "myVnet"
  address_space       = ["10.0.0.0/16"]
  location            = "West Europe"
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
  location            = "West Europe"
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
  location            = "West Europe"
  resource_group_name = "ocrets"
  allocation_method   = "Dynamic"
}

# Create network interface (This CAN'T be done in advance, as I need one per VM: too much GUI work)
resource "azurerm_network_interface" "terraformnic" {
  name                      = "myNIC"
  location                  = "West Europe"
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
  name                  = "tslauncher"
  location              = "West Europe"
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
    admin_username = "uroot" # no root here!
  }

  os_profile_linux_config {
    disable_password_authentication = true

    ssh_keys {
      key_data = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAgQCFPaN62APTqDCy3eB6qy+ALngWKg/RHCU0XWlL47JQ/Bj4zjHoyviFQ3+WgRgRxakKSdbpRU28qm0dUT+5Ki72doEmcmmqdzwhTa6H/0XwoeeRc12eIUw/sn2wTgdf/c57ft0deOyxeALVArAZwCXxywNeRcAjGJsvp4LW6jjZFQ=="
      path     = "/home/uroot/.ssh/authorized_keys"
    }
  }
}

resource null_resource "allow_root" {
  depends_on = [azurerm_virtual_machine.main]
  provisioner "remote-exec" {
    connection {
      host        = "${azurerm_public_ip.myterraformpublicip.ip_address}"
      type        = "ssh"
      user        = "uroot"
      private_key = file("~/.ssh/id_rsa")
    }
    inline = [
      "sudo mkdir /root/.ssh",
      "sudo cp /home/uroot/.ssh/authorized_keys /root/.ssh",
      "sudo sed -i 's/PermitRootLogin no/PermitRootLogin yes/g' /etc/ssh/sshd_config",
      "sudo systemctl restart sshd"
    ]
  }
}
