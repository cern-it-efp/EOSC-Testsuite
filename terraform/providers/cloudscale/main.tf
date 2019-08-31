provider "cloudscale" {}

resource "cloudscale_server" "kubemaster" {
  name        = "kubenode-master-GBTY"
  image_slug  = "centos-7"
  flavor_slug = "flex-2"
  ssh_keys    = ["ssh-rsa ..."]

  connection {
    type        = "ssh"
    user        = "root"
    private_key = "${file("~/.ssh/id_rsa")}"
  }

  provisioner "remote-exec" {
    inline = [
      "echo DOCKER_CE_VER= >> /etc/environment",
      "echo DOCKER_EN_VER= >> /etc/environment",
      "echo K8S_VER= >> /etc/environment",
      "source /etc/environment",
    ]
  }

  provisioner "local-exec" {
    command = "echo ${self.public_ip} > ../master_ip && ./ssh_connect.sh --usr root --ip ${self.public_ip} --file cluster_creator.sh --opts -m; mkdir -p ~/.kube & ./ssh_connect.sh --scp --src root@${self.public_ip}:~/.kube/config --dst ~/.kube/config"
  }

  provisioner "remote-exec" {
    inline = [
      "echo $(kubeadm token create --print-join-command)' --ignore-preflight-errors=SystemVerification' > ~/join.sh",
    ]
  }

  provisioner "local-exec" {
    command = "timeout 240 ./ssh_connect.sh --scp --src root@${self.public_ip}:~/join.sh --dst ./join.sh --hide-logs; if [ $? -eq 124 ]; then echo ' ! ! ! ERROR: Timeout trying to fetch join command from master node ! ! ! ' ; exit 1 ; else exit 0; fi"
  }
}

resource "cloudscale_server" "kubenode" {
  count = "3"

  name        = "kubenode-slave${count.index+1}-GBTY"
  image_slug  = "centos-7"
  flavor_slug = "flex-2"
  ssh_keys    = ["ssh-rsa ..."]

  connection {
    type        = "ssh"
    user        = "root"
    private_key = "${file("~/.ssh/id_rsa")}"
  }

  provisioner "remote-exec" {
    inline = [
      "echo DOCKER_CE_VER= >> /etc/environment",
      "echo DOCKER_EN_VER= >> /etc/environment",
      "echo K8S_VER= >> /etc/environment",
      "source /etc/environment",
    ]
  }

  provisioner "local-exec" {
    command = "./ssh_connect.sh --usr root --ip ${self.public_ip} --file cluster_creator.sh"
  }

  provisioner "local-exec" {
    command = "echo 'Waiting for join command... ' ; timeout 240 ./ssh_connect.sh --usr root --ip ${self.public_ip} --file ./join.sh --hide-logs; if [ $? -eq 124 ]; then echo ' ! ! ! ERROR: Timeout waiting for join command at ${self.public_ip} ! ! ! ' ; exit 1 ; else exit 0 ; fi"
  }
}
