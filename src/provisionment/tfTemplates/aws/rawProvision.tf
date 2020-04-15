provider "aws" {
  region                  = yamldecode(file(var.configsFile))["region"]
  shared_credentials_file = yamldecode(file(var.configsFile))["sharedCredentialsFile"]
}

resource "aws_instance" "kubenode" {
  count         = var.customCount
  tags = {
    Name = "${var.instanceName}-${count.index}"
  }
  security_groups = var.securityGroups
  instance_type = var.flavor
  ami      = yamldecode(file(var.configsFile))["ami"]
  key_name = yamldecode(file(var.configsFile))["keyName"]
  root_block_device {
    volume_size = var.volumeSize
  }
}
