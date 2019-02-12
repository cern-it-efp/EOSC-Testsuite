provider "PROVIDER_NAME" {
  CREDENTIALS_PLACEHOLDER
}

resource "PROVIDER_INSTANCE_NAME" "kubemaster" {

  MASTER_DEFINITION_PLACEHOLDER

  provisioner "local-exec" {
    command = "echo ${self.ip_address} > aux/master_ip"
  }

  connection {
    type        = "ssh"
    user        = "root"
    private_key = "${file("PATH_TO_KEY_VALUE")}" #must be the key used for the VM: "key_par"
  }

  provisioner "local-exec" {
    command = "ssh -o 'StrictHostKeyChecking no' root@${self.ip_address} 'bash -s' -- < aux/cluster_creator.sh -m -l &> /dev/null"
  }

  provisioner "remote-exec" {
    inline = [
      "JOIN_COMMAND=$(kubeadm token create --print-join-command)' --ignore-preflight-errors=SystemVerification'",
      "echo $JOIN_COMMAND > ~/join.sh",
    ]
  }

  provisioner "local-exec"{
    command = "scp -o 'StrictHostKeyChecking no' root@${self.ip_address}:~/join.sh ./join.sh &> /dev/null",
  }

  provisioner "local-exec" {
    command = "mkdir ~/.kube & scp -o 'StrictHostKeyChecking no' root@${self.ip_address}:~/.kube/config ~/.kube/config &> /dev/null",
  }
}

resource "PROVIDER_INSTANCE_NAME" "kubenode" {
  count      = "SLAVES_AMOUNT"

  SLAVE_DEFINITION_PLACEHOLDER

  connection {
    type        = "ssh"
    user        = "root"
    private_key = "${file("PATH_TO_KEY_VALUE")}" #must be the key used for the VM: "key_par".
  }

  provisioner "local-exec" {
    command = "ssh -o 'StrictHostKeyChecking no' root@${self.ip_address} 'bash -s' -- < aux/cluster_creator.sh -l &> /dev/null"
  }

  provisioner "local-exec" {
    command = "echo 'Waiting for join command... ' ; while [ ! -e ./join.sh ]; do : ; done"
  }

  provisioner "local-exec" { 
    command = "ssh -o 'StrictHostKeyChecking no' root@${self.ip_address} 'bash -s' -- < ./join.sh &> /dev/null "
  }

  provisioner "local-exec" { #needed for being able to run this several times
    command ="rm -f join.sh"
  }

}
