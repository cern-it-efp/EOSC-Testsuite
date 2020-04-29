# -------------------------- General -------------------------------------------
variable "sshConnect" {
  default = "../../provisionment/ssh_connect.sh"
}
variable "sshcTimeout" {
  default = "2000"
}

# -------------------------- Common ones ---------------------------------------
variable "configsFile" {}
variable "customCount" {}
variable "flavor" {}
variable "instanceName" {}

variable "securityGroups" { default = "" } # this is optional in some providers (not even used for azure), then requires a default value
variable "storageCapacity" { default = "" }
variable "pathToKey" { default = "" }
variable "openUser" { default = "" }
variable "zone" { default = "" }
variable "region" { default = "" }
variable "keyPair" { default = "" }

# -------------------------- Stack versioning ----------------------------------
variable "dockerCE" { default = "DOCKER_CE_PH" }
variable "dockerEngine" { default = "DOCKER_EN_PH" }
variable "kubernetes" { default = "K8S_PH" }

############################ OPENSTACK #########################################
variable "availabilityZone" { default = "" } # region is above
variable "useDefaultNetwork" { default = true } # default uses existing network (if only 1, otherwise fails)

############################ AZURE #############################################
variable "clusterRandomID" { default = "" }
variable "vmSize" { default = "" } 
#variable "secGroupId" {
#  default = "SECGROUPID_PH"
#}
variable "publisher" { default = "" }
variable "offer" { default = "" }
variable "sku" { default = "" }
variable "imageVersion" { default = "" }

############################ GCP ###############################################
variable "gpuCount" { default = "" }
variable "gpuType" { default = "" }

# ~~~~~~~~~~~~~~~~~~~~~~~~~~ END OF VARS  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
