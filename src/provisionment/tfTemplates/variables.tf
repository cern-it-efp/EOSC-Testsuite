# -------------------------- Common ones ---------------------------------------
variable "configsFile" {}
variable "customCount" {}
variable "flavor" {}
variable "instanceName" {}

variable "securityGroups" { default = "" } # this is optional in some providers (not even used for azure), then requires a default value
variable "storageCapacity" { default = "" }
variable "pathToKey" { default = "" }
variable "pathToPubKey" { default = "" }
variable "openUser" { default = "" }
variable "zone" { default = "" }
variable "region" { default = "" }
variable "keyPair" { default = "" }

# -------------------------- Stack versioning ----------------------------------
variable "dockerCE" { default = "" }
variable "dockerEngine" { default = "" }
variable "kubernetes" { default = "" }

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
variable "usePrivateIPs" { default = "" }
variable "offer" { default = "" }
variable "sku" { default = "" }
variable "imageVersion" { default = "" }

############################ GCP ###############################################
variable "gpuCount" { default = "" }
variable "gpuType" { default = "" }
variable "gcp_keyAsMetadata" { default = "" }

############################ CLOUDSIGMA ########################################
variable "staticIPs" { default = "" }

# ~~~~~~~~~~~~~~~~~~~~~~~~~~ END OF VARS  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
