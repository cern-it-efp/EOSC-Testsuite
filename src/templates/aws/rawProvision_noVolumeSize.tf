provider "aws" {
  region                  = "${var.region}"
  shared_credentials_file = "${var.sharedCredentialsFile}"
}

resource "aws_instance" "kubenode" {

  count         = "${var.customCount}"
  instance_type = "${var.instanceType}"
  tags = {
    name = "${var.instanceName}-${count.index}"
  }
  ami      = "${var.ami}"
  key_name = "${var.keyName}"
}
