resource null_resource "allow_root" {
  count = var.customCount
  provisioner "remote-exec" {
    connection {
      host        = LIST_IP_GETTER
      type        = "ssh"
      user        = var.openUser
      private_key = file(var.pathToKey)
      timeout     = "20m"
    }
    inline = [
      "sudo mkdir /root/.ssh",
      "sudo cp /home/${var.openUser}/.ssh/authorized_keys /root/.ssh",
      "sudo sed -i 's/PermitRootLogin no/PermitRootLogin yes/g' /etc/ssh/sshd_config",
      "sudo systemctl restart sshd"
    ]
  }
}
