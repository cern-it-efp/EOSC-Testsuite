provider "openstack" {}

resource "openstack_compute_instance_v2" "kubemaster" {
  name = "kubenode-master-JBSZ"

  image_name = "CentOS 7 (19.15.1)"

  flavor_name = "eo1.medium"

  key_pair = "mykey"
}

resource "openstack_compute_instance_v2" "kubenode" {
  count = "3"
  name  = "kubenode-slave${count.index+1}-JBSZ"

  image_name = "CentOS 7 (19.15.1)"

  flavor_name = "eo1.medium"

  key_pair = "mykey"
}

resource "null_resource" "kubemaster_boots" {
  connection {
    host        = "185.178.87.16"
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
    command = "echo 185.178.87.16 > ../master_ip && ./ssh_connect.sh --usr root --ip 185.178.87.16 --file cluster_creator.sh --opts -m; mkdir -p ~/.kube & ./ssh_connect.sh --scp --src root@185.178.87.16:~/.kube/config --dst ~/.kube/config"
  }

  provisioner "remote-exec" {
    inline = [
      "echo $(kubeadm token create --print-join-command)' --ignore-preflight-errors=SystemVerification' > ~/join.sh",
    ]
  }

  provisioner "local-exec" {
    command = "timeout 240 ./ssh_connect.sh --scp --src root@185.178.87.16:~/join.sh --dst ./join.sh --hide-logs; if [ $? -eq 124 ]; then echo ' ! ! ! ERROR: Timeout trying to fetch join command from master node ! ! ! ' ; exit 1 ; else exit 0; fi"
  }
}

resource "null_resource" "kubenode_boots" {
  count = "3"

  connection {
    host        = "${openstack_compute_instance_v2.kubenode.network.0.fixed_ip_v4}"
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
    command = "./ssh_connect.sh --usr root --ip ${self.network.0.fixed_ip_v4} --file cluster_creator.sh"
  }

  provisioner "local-exec" {
    command = "echo 'Waiting for join command... ' ; timeout 240 ./ssh_connect.sh --usr root --ip ${self.network.0.fixed_ip_v4} --file ./join.sh --hide-logs; if [ $? -eq 124 ]; then echo ' ! ! ! ERROR: Timeout waiting for join command at ${self.network.0.fixed_ip_v4} ! ! ! ' ; exit 1 ; else exit 0 ; fi"
  }
}
