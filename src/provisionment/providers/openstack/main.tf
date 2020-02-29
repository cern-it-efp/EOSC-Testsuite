provider "openstack" {
  #key = "${var.api_key}"
  #secret = "${var.secret_key}"
  #token = "${var.api_key}"
  #auth_url = "${var.auth_url}"
}

#Key creation is required too as the user might not have a key already created on the provider (it might be his first use of it), however do not automate this! just inform the user and document how to do it

resource "openstack_compute_instance_v2" "k8s-master" {
  name = "k8s-master"
  image_name = "${var.image-name}"
  flavor_name = "${var.image-flavor}"
  key_pair = "${var.key-pair}"
  security_groups = ["${split(",", var.security-groups)}"]
  connection {
    private_key = "${file("${var.path_to_key}")}" #must be the key used for the VM: "key_par"
  }
  provisioner "local-exec" {
    command: "export MASTER_IP=${self.network.0.fixed_ip_v4}"
  }
  provisioner "file" {
    source      = "../../cluster_creator.sh"
    destination = "/tmp/cluster_creator.sh"
  }
  #if gpu option is used: (according to Konstantinos nvidia-docker is not needed)
  provisioner "file" {
    source      = "../../cuda_install_cc7_392-24.sh"
    destination = "/tmp/cuda_install_cc7_392-24.sh.sh"
  }
  provisioner "file" {
    source      = "../../device_plugin.yaml"
    destination = "/tmp/device_plugin.yaml"
  }
  provisioner "remote-exec" {
    inline = [
      "yum -y install git nano",
      "chmod +x /tmp/cluster_creator.sh",
      "/tmp/cluster_creator.sh -m",
      "JOIN_COMMAND=$(kubeadm token create --print-join-command)' --ignore-preflight-errors=SystemVerification'",
      "echo $JOIN_COMMAND > ~/join.sh"
    ]
  }
}

resource "openstack_compute_instance_v2" "k8s-node" {
  count = "${var.node-count}"
  name = "k8s-node-${count.index+1}"
  image_name = "${var.image-name}"
  flavor_name = "${var.image-flavor}"
  key_pair = "${var.key-pair}"
  security_groups = ["${split(",", var.security-groups)}"]
  connection {
      private_key = "${file("${var.path_to_key}")}" #must be the key used for the VM: "key_par"
  }
  provisioner "file" {
    source      = "../../cluster_creator.sh"
    destination = "/tmp/cluster_creator.sh"
  }
  provisioner "file" { #slaves need the key to connect via ssh to the master in order to fetch the join.sh file containing the join command
    source      = "${var.path_to_key}"
    destination = "~/.ssh/id_rsa"
  }
  #if gpu option is used: (according to Konstantinos nvidia-docker is not needed)
  provisioner "file" {
    source      = "../../cuda_install_cc7_392-24.sh"
    destination = "/tmp/cuda_install_cc7_392-24.sh.sh"
  }
  provisioner "remote-exec" "this"{ # NOTE THE GPU OPTION. If the gpu option is used, the test_suite.sh file must generate a main.tf file with a provisioner copying the needed scripts (the above one) and the command specifying the --gpu option on the slave (below). Also note the flavor must change!
    inline = [
      "yum -y install git nano",
      "chmod 600 ~/.ssh/id_rsa",
      "chmod +x /tmp/cluster_creator.sh",
      "/tmp/cluster_creator.sh",
      "while [[ ! -e ~/join.sh ]]; do scp -o 'StrictHostKeyChecking no' root@${openstack_compute_instance_v2.k8s-master.network.0.fixed_ip_v4}:~/join.sh ~/join.sh; done",
      "chmod +x ~/join.sh",
      "~/join.sh"
    ]
  }
  #get rid of this! instead put the copying of the join.sh file in a while loop that checks when the file exists and only then runs it.
  #   Or better (to avoid network overflow), make the resource creation in steps: first create machines with docker and kubernetes,
  #   then update the master to init the cluster and then update the slaves to join the cluster
  #depends_on = ["openstack_compute_instance_v2.k8s-master"]
  #Usage of ${openstack_compute_instance_v2.k8s-master.ip_address} on the slave resource definition, makes TF wait for master! automatic depend.
}
