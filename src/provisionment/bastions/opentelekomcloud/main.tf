variable "access_key" {
  default = ""
}
variable "secret_key" {
  default = ""
}
variable "keyPair" {
  default = "exo"
}
variable "flavorName" {
  default = "s2.medium.1"
}
variable "imageName" {
  default = "Standard_Ubuntu_18.04_latest"
}
variable "secGroups" {
  default = ["default"]
}
variable "configsPath" {
  default = "~/tsk.yml"
}
# ------------------------------------------------------------------------------
variable "domain_name" {
  default = "OTC-EU-DE-00000000001000046175"
}
variable "tenant_name" {
  default = "eu-de" # this is actually project
}

provider "opentelekomcloud" {
  access_key = yamldecode(file(var.configsPath))["accK"] # TODO: do this for all other vars instead of placeholder + replace()
  secret_key = yamldecode(file(var.configsPath))["secK"]
  domain_name = var.domain_name
  tenant_name = var.tenant_name
  auth_url    = "https://iam.eu-de.otc.t-systems.com/v3"
}

resource "opentelekomcloud_compute_instance_v2" "tslauncher" {
  name = "tslauncher"
  flavor_name = var.flavorName
  image_name = var.imageName
  key_pair = var.keyPair
  security_groups = var.secGroups
}
