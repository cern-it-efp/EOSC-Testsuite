provider "PROVIDER_NAME" {
  CREDENTIALS_PLACEHOLDER
}

resource "PROVIDER_INSTANCE_NAME" "kubemaster" {

  MASTER_DEFINITION_PLACEHOLDER

  connection {
    type        = "ssh"
    user        = "root"
    private_key = "${file("PATH_TO_KEY_VALUE")}"
  }
  provisioner "remote-exec" {
    inline = [
      "echo DOCKER_CE_VER=DOCKER_CE_PH >> /etc/environment",
      "echo DOCKER_EN_VER=DOCKER_EN_PH >> /etc/environment",
      "echo K8S_VER=K8S_PH >> /etc/environment",
      "source /etc/environment"
    ]
  }
  provisioner "local-exec" {
    command = "echo NODE_IP_GETTER > ../master_ip && ./ssh_connect.sh --usr root --ip NODE_IP_GETTER --file aux/cluster_creator.sh --opts -m; mkdir -p ~/.kube & ./ssh_connect.sh --scp --src root@NODE_IP_GETTER:~/.kube/config --dst ~/.kube/config"
  }
  provisioner "remote-exec" {
    inline = [
      "echo $(kubeadm token create --print-join-command)' --ignore-preflight-errors=SystemVerification' > ~/join.sh"
    ]
  }
  provisioner "local-exec"{
    command = "timeout 240 ./ssh_connect.sh --scp --src root@NODE_IP_GETTER:~/join.sh --dst ./join.sh --hide-logs; if [ $? -eq 124 ]; then echo ' ! ! ! ERROR: Timeout trying to fetch join command from master node ! ! ! ' ; exit 1 ; else exit 0; fi"
  }
}

resource "PROVIDER_INSTANCE_NAME" "kubenode" {
  count      = "SLAVE_NODES"

  SLAVE_DEFINITION_PLACEHOLDER

  connection {
    type        = "ssh"
    user        = "root"
    private_key = "${file("PATH_TO_KEY_VALUE")}"
  }
  provisioner "remote-exec" {
    inline = [
      "echo DOCKER_CE_VER=DOCKER_CE_PH >> /etc/environment",
      "echo DOCKER_EN_VER=DOCKER_EN_PH >> /etc/environment",
      "echo K8S_VER=K8S_PH >> /etc/environment",
      "source /etc/environment"
    ]
  }
  provisioner "local-exec" {
    command = "./ssh_connect.sh --usr root --ip NODE_IP_GETTER --file aux/cluster_creator.sh"
  }
  provisioner "local-exec" {
    command = "echo 'Waiting for join command... ' ; timeout 240 ./ssh_connect.sh --usr root --ip NODE_IP_GETTER --file ./join.sh --hide-logs; if [ $? -eq 124 ]; then echo ' ! ! ! ERROR: Timeout waiting for join command at NODE_IP_GETTER ! ! ! ' ; exit 1 ; else exit 0 ; fi"
  }
}
