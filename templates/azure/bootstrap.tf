resource "null_resource" "allow_root" {
  count = var.customCount
  provisioner "remote-exec" {
    connection {
      host        = element(azurerm_network_interface.terraformnic.*.private_ip_address, count.index)
      type        = "ssh"
      user        = var.openUser
      private_key = file("~/.ssh/id_rsa")
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

resource "null_resource" "kubenode_bootstraper" {
  depends_on = [null_resource.kubenode_bootstraper[0], null_resource.allow_root]

  count = var.customCount

  connection {
    host        = element(azurerm_network_interface.terraformnic.*.private_ip_address, count.index)
    type        = "ssh"
    user        = "root"
    private_key = file(var.pathToKey)
    timeout     = "10m"
  }

  provisioner "remote-exec" {
    inline = [
      "echo DOCKER_CE_VER=${var.dockerCeVer} >> /etc/environment",
      "echo DOCKER_EN_VER=${var.dockerEnVer} >> /etc/environment",
      "echo K8S_VER=${var.k8sVer} >> /etc/environment",
      ". /etc/environment",
    ]
  }

  #------------------------------------------- THESE ARE FOR MASTER (count.index == 0)--------------------------------------------------------------------------------------
  provisioner "local-exec" {
    command = "if [ ${count.index} == 0 ]; then timeout ${var.sshcTimeout} ${var.sshConnect} --key ${var.pathToKey} --usr root --ip ${element(azurerm_network_interface.terraformnic.*.private_ip_address, count.index)} --file ${var.clusterCreator} --opts -m; mkdir -p ~/.kube & ${var.sshConnect} --key ${var.pathToKey} --scp --src root@${element(azurerm_network_interface.terraformnic.*.private_ip_address, count.index)}:~/.kube/config --dst ${var.kubeconfigDst}; fi"

    interpreter = ["/bin/bash", "-c"]
  }

  provisioner "remote-exec" {
    inline = [
      "if [ ${count.index} == 0 ]; then echo $(kubeadm token create --print-join-command)' --ignore-preflight-errors=SystemVerification' > ~/join.sh; fi",
    ]
  }

  provisioner "local-exec" {
    command = "if [ ${count.index} == 0 ]; then timeout ${var.sshcTimeout} ${var.sshConnect} --key ${var.pathToKey} --scp --src root@${element(azurerm_network_interface.terraformnic.*.private_ip_address, count.index)}:~/join.sh --dst ./join.sh --hide-logs; if [ $? -eq 124 ]; then echo ' ! ! ! ERROR: Timeout trying to fetch join command from master node ! ! ! ' ; exit 1 ; else exit 0; fi; fi"

    interpreter = ["/bin/bash", "-c"]
  }

  #--------------------------------------------------------------------------------------------------------------------------------------------------------

  #------------------------------------------- THESE ARE FOR SLAVES (count.index > 0)--------------------------------------------------------------------------------------
  provisioner "local-exec" {
    command = "if [ ${count.index} \\> 0 ]; then timeout ${var.sshcTimeout} ${var.sshConnect} --key ${var.pathToKey} --usr root --ip ${element(azurerm_network_interface.terraformnic.*.private_ip_address, count.index)} --file ${var.clusterCreator}; fi"

    interpreter = ["/bin/bash", "-c"]
  }
  provisioner "local-exec" {
    command = "if [ ${count.index} \\> 0 ]; then echo 'Waiting for join command... ' ; timeout ${var.sshcTimeout} ${var.sshConnect} --key ${var.pathToKey} --usr root --ip ${element(azurerm_network_interface.terraformnic.*.private_ip_address, count.index)} --file ./join.sh --hide-logs; if [ $? -eq 124 ]; then echo ' ! ! ! ERROR: Timeout waiting for join command at ${element(azurerm_network_interface.terraformnic.*.private_ip_address, count.index)} ! ! ! ' ; exit 1 ; else exit 0 ; fi; fi"

    interpreter = ["/bin/bash", "-c"]
  }
  #--------------------------------------------------------------------------------------------------------------------------------------------------------
}
