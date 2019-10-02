provider "cloudstack" {
  #config = ""
  #profile = "" # ?
  api_url    = ""
  api_key    = ""
  secret_key = ""
  config = "${var.configPath}" # failed, required 'profile'
}

resource "cloudstack_instance" "kubenode" {
  count           = "${var.customCount}"
  zone            = "${var.zone}"
  service_offering            = "${var.size}"
  name            = "${var.instanceName}-${count.index}"
  template        = "${var.template}"
  keypair        = "${var.keyPair}"
  security_group_names = "${var.securityGroups}"
  disk_size       = "${var.diskSize}"

}
