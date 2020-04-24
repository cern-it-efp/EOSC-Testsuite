############################ COMMON ONES #######################################
variable "configsFile" {}
variable "customCount" {}
variable "flavor" {}
variable "instanceName" {}

variable "securityGroups" { # this is optional in some providers (not even used for azure), then requires a default value
  default = ""
}

variable "diskSize" {
  default = ""
}
variable "pathToKey" {
  default = ""
}
variable "openUser" {
  default = ""
}
variable "zone" {
  default = ""
}
variable "region" {
  default = ""
}
variable "keyPair" {
  default = ""
}

# -------------------------- General -------------------------------------------
variable "sshConnect" {
  default = "../../provisionment/ssh_connect.sh"
}
variable "sshcTimeout" {
  default = "2000"
}
# -------------------------- Stack versioning ----------------------------------
variable "dockerCeVer" {
  default = "DOCKER_CE_PH"
}
variable "dockerEnVer" {
  default = "DOCKER_EN_PH"
}
variable "k8sVer" {
  default = "K8S_PH"
}

############################ OPENSTACK #########################################
variable "availabilityZone" {
  default = ""
}

############################ AZURE #############################################
variable "clusterRandomID" {
  default = ""
}
variable "vmSize" { # TODO
  default = ""
}
#variable "secGroupId" {
#  default = "SECGROUPID_PH"
#}
variable "publisher" {
  default = ""
}
variable "offer" {
  default = ""
}
variable "sku" {
  default = ""
}
variable "imageVersion" {
  default = ""
}

############################ GCP ###############################################
variable "gpuCount" {
  default = ""
}
variable "gpuType" {
  default = ""
}

############################ AWS ###############################################
#variable "accessKey" {
#  default = "ACCESS_KEY_PH"
#}
#variable "secretKey" {
#  default = "SECRET_KEY_PH"
#}
#variable "instanceType" {
#  default = "INSTANCE_TYPE_PH"
#}
variable "volumeSize" {
  default = ""
}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~ END OF VARS  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
