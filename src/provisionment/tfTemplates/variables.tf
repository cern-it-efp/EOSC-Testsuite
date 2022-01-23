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
variable "staticIPs" { default = "" }
variable "useStaticIPs" { default = false }

# -------------------------- Stack versioning ----------------------------------
variable "dockerCE" { default = "" }
variable "dockerEngine" { default = "" }
variable "kubernetes" { default = "" }

############################ OPENSTACK #########################################
variable "availabilityZone" { default = "" } # region is above
variable "useDefaultNetwork" { default = true } # default uses existing network (if only 1, otherwise fails)
variable "authUrl" { default = "" }

############################ GCP ###############################################
variable "gpuCount" { default = "" }
variable "gpuType" { default = "" }
variable "gcp_keyAsMetadata" { default = "" }

############################ OCI ###############################################
variable "useFlexShape" { default = "" }

############################ AZURE #############################################
variable "isGPUcluster" { default = false }

# ~~~~~~~~~~~~~~~~~~~~~~~~~~ END OF VARS  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
