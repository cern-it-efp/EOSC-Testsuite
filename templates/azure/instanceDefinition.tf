name                  = "kubenode"#NAME
location                  = "${var.location}"
resource_group_name       = "${var.resourceGroupName}"
network_interface_ids = [element(azurerm_network_interface.terraformnic.*.id, count.index)]
storage_os_disk {
  name              = "myOsDisk${count.index}"
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
  computer_name  = "kubenode"#NAME
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
    host = element(azurerm_network_interface.terraformnic.*.private_ip_address,count.index)
    type        = "ssh"
    user        = "${var.openUser}"
    private_key = file("~/.ssh/id_rsa")
    timeout     = "30m"
  }
  inline = ["sudo mkdir /root/.ssh ; sudo cp /home/${var.openUser}/.ssh/authorized_keys /root/.ssh"]
}
