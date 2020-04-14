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
  instance_type = yamldecode(file(var.configsFile))["flavor"]
  ami      = yamldecode(file(var.configsFile))["ami"]
  key_name = yamldecode(file(var.configsFile))["keyName"]
}
