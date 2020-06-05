variable "openUser" {
  default = "uroot"
}
variable "ssh_private_key_path" {
  default = "~/.ssh/id_rsa"
}

provider "azurerm" {
  subscription_id = "54f623f0-8c18-40dd-9530-d32d2f1ee14f"
  features {}
}

# Create virtual network (This can actually be done IN ADVANCE)
resource "azurerm_virtual_network" "myterraformnetwork" {
  name                = "myVnet"
  address_space       = ["10.0.0.0/16"]
  location            = "West Europe"
  resource_group_name = "efprg"
}

# Create subnet (This can actually be done IN ADVANCE)
resource "azurerm_subnet" "myterraformsubnet" {
  name                 = "mySubnet"
  resource_group_name  = "efprg"
  virtual_network_name = azurerm_virtual_network.myterraformnetwork.name
  address_prefix       = "10.0.1.0/24"
}

# Create public IPs
resource "azurerm_public_ip" "myterraformpublicip" {
  name                = "myPublicIP"
  location            = "West Europe"
  resource_group_name = "efprg"
  allocation_method   = "Dynamic"
}

# Create network interface (This CAN'T be done in advance, as I need one per VM: too much GUI work)
resource "azurerm_network_interface" "terraformnic" {
  name                      = "myNIC"
  location                  = "West Europe"
  resource_group_name       = "efprg"

  ip_configuration {
    name                          = "myNicConfiguration"
    subnet_id                     = azurerm_subnet.myterraformsubnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.myterraformpublicip.id
  }
}

############################################### CREATE VM ###############################################

resource "azurerm_virtual_machine" "main" {
  name                  = "tslauncher"
  location              = "West Europe"
  vm_size               = "Standard_D2s_v3"
  resource_group_name   = "efprg"
  network_interface_ids = [azurerm_network_interface.terraformnic.id]
  delete_os_disk_on_termination = true

  storage_os_disk {
    name              = "myOsDisk"
    caching           = "ReadWrite"
    create_option     = "FromImage"
    managed_disk_type = "Premium_LRS"
  }

  storage_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

  os_profile {
    computer_name  = "tslauncher"
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

resource "null_resource" "docker" {
  depends_on = [azurerm_virtual_machine.main]
  connection {
    host = azurerm_public_ip.myterraformpublicip.ip_address
    user        = var.openUser
    private_key = file(var.ssh_private_key_path)
  }
  provisioner "remote-exec" {
    inline = [
      "sudo apt-get update -y ; sudo apt-get install docker.io -y ; sudo docker run --name tslauncher -itd --net=host cernefp/tslauncher",
      "echo sudo docker exec -it tslauncher bash >> ~/.bashrc"
    ]
  }
}
