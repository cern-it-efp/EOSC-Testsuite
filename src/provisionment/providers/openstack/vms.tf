provider "openstack" {}


resource "openstack_compute_instance_v2" "kubenode" {
  count = "3"
  name  = "kubenode-slave${count.index+1}-JBSZ"

  image_name = "CentOS 7"

  flavor_name = "eo1.medium"

  key_pair = "mykey"
}

