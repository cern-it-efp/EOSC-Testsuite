provider "aws" {
  region                  = "${var.region}" # "us-east-2"
  shared_credentials_file = "${var.sharedCrdentialsFile}"
}

resource "aws_instance" "kubenode" {

  count         = "${var.customCount}"
  instance_type = "${var.instanceType}" # "t2.medium"
  tags = {
    name = "${var.instanceName}-${count.index}"
  }
  ami      = "${var.ami}"     # "ami-08ee2516c7709ea48"
  key_name = "${var.keyName}" # "exo"
  root_block_device {
    volume_size = var.volumeSize # 50
  }
}
