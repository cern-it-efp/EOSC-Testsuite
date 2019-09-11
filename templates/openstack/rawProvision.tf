provider "openstack" {
  # Keep this empty: by now, only authentication with external file is supported (like cloudferro and CERN os)
}

resource "openstack_compute_instance_v2" "kubenode" {
  count                 = "${var.customCount}"
  name                  = "${var.instanceName}-${count.index}"
  image_name = "${var.imageName}"
  key_pair = "${var.keyPair}"
  security_groups = var.securityGroups
  region = "${var.region}" # errors if set to "" ?
  availability_zone = "${var.availabilityZone}" # errors if set to "" ?
}
