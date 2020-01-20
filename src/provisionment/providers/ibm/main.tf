provider "ibm" {
  bluemix_api_key = "eoD3_AzeeXjaSr_JBLIeWec9m7yYYr-KIdcWUzA1Pxi"
}

resource "ibm_compute_vm_instance" "kubemaster" {
  hostname = "kubenode-master-SA07"
  domain   = "thisismyexample.com"

  #image_name = "CC7 - x86_64 [2018-12-03]"
  #flavor_name = "m2.medium"
  #key_pair = "os-new"
  #security_groups = ["default"]
  datacenter_choice = [
    {
      datacenter = "dal09"
    },
    {
      datacenter = "wdc54"
    },
    {
      datacenter = "dal09"
    },
    {
      datacenter = "dal06"
    },
    {
      datacenter = "dal09"
    },
    {
      datacenter = "dal09"
    },
  ]

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
    command = "echo ${self.ip_address} > ../master_ip && ./ssh_connect.sh --usr root --ip ${self.ip_address} --file cluster_creator.sh --opts -m; mkdir -p ~/.kube & ./ssh_connect.sh --scp --src root@${self.ip_address}:~/.kube/config --dst ~/.kube/config"
  }

  provisioner "remote-exec" {
    inline = [
      "echo $(kubeadm token create --print-join-command)' --ignore-preflight-errors=SystemVerification' > ~/join.sh",
    ]
  }

  provisioner "local-exec" {
    command = "timeout 240 ./ssh_connect.sh --scp --src root@${self.ip_address}:~/join.sh --dst ./join.sh --hide-logs; if [ $? -eq 124 ]; then echo ' ! ! ! ERROR: Timeout trying to fetch join command from master node ! ! ! ' ; exit 1 ; else exit 0; fi"
  }
}

resource "ibm_compute_vm_instance" "kubenode" {
  count = "3"

  hostname = "kubenode-slave${count.index+1}-SA07"
  domain   = "thisismyexample.com"

  #image_name = "CC7 - x86_64 [2018-12-03]"
  #flavor_name = "m2.medium"
  #key_pair = "os-new"
  #security_groups = ["default"]
  datacenter_choice = [
    {
      datacenter = "dal09"
    },
    {
      datacenter = "wdc54"
    },
    {
      datacenter = "dal09"
    },
    {
      datacenter = "dal06"
    },
    {
      datacenter = "dal09"
    },
    {
      datacenter = "dal09"
    },
  ]

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
    command = "./ssh_connect.sh --usr root --ip ${self.ip_address} --file cluster_creator.sh"
  }

  provisioner "local-exec" {
    command = "echo 'Waiting for join command... ' ; timeout 240 ./ssh_connect.sh --usr root --ip ${self.ip_address} --file ./join.sh --hide-logs; if [ $? -eq 124 ]; then echo ' ! ! ! ERROR: Timeout waiting for join command at ${self.ip_address} ! ! ! ' ; exit 1 ; else exit 0 ; fi"
  }
}
