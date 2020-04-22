############################ COMMON ONES #######################################
variable "configsFile" {}
variable "customCount" {}
variable "flavor" {}
variable "instanceName" {}
variable "securityGroups" {}

variable "diskSize" {
  # TODO: for exoscale, this is the only var that does not have a value at terraform.tfvars.json. Since it is required on exoscale it is directly taken from configs.yaml like template or zone
  # Therefore, terraform asks for a value for it if it's defined like the other vars on the top here. Setting a default avoids that behaviour
  # Also could be removed but it is required for oci and cloudstack: it is optional on them so it will be taken from terraform.tfvars.json and not from configs.yaml directly (null in case it is not set at configs.yaml)
  default = ""
}
variable "pathToKey" {
  default = "PATH_TO_KEY_VALUE"
}
variable "openUser" {
  default = "OPEN_USER_PH"
}
variable "zone" {
  default = "ZONE_PH"
}
variable "region" {
  default = "REGION_PH"
}
variable "keyPair" {
  default = "KEY_PAIR_PH"
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
variable "imageName" {
  default = "IMAGE_PH"
}
variable "availabilityZone" {
  default = "AV_ZONE_PH"
}

############################ AZURE #############################################
variable "location" {
  default = "LOCATION_PH"
}
variable "resourceGroupName" {
  default = "RGROUP_PH"
}
variable "pubSSH" {
  default = "PUB_SSH_PH"
}
variable "clusterRandomID" {
  default = "RANDOMID_PH"
}
variable "vmSize" {
  default = "VM_SIZE_PH"
}
variable "secGroupId" {
  default = "SECGROUPID_PH"
}
variable "subscriptionId" {
  default = "SUBSCRIPTION_PH"
}
variable "subnetId" {
  default = "SUBNETID_PH"
}
# Optional
variable "publisher" {
  default = "PUBLISHER_PH"
}
variable "offer" {
  default = "OFFER_PH"
}
variable "sku" {
  default = "SKU_PH"
}
variable "imageVersion" {
  default = "VERSION_PH"
}

############################ GCP ###############################################
variable "credentials" {
  default = "CREDENTIALS_PATH_PH"
}
variable "project" {
  default = "PROJECT_PH"
}
variable "machineType" {
  default = "MACHINE_TYPE_PH"
}
variable "image" {
  default = "IMAGE_PH"
}
variable "gpuCount" {
  default = "GPU_COUNT_PH"
}
variable "gpuType" {
  default = "GPU_TYPE_PH"
}

############################ AWS ###############################################
variable "accessKey" {
  default = "ACCESS_KEY_PH"
}
variable "secretKey" {
  default = "SECRET_KEY_PH"
}
variable "instanceType" {
  default = "INSTANCE_TYPE_PH"
}
variable "ami" {
  default = "AMI_PH"
}
variable "keyName" {
  default = "NAME_KEY_PH"
}
variable "volumeSize" {
  default = "VOLUME_SIZE_PH"
}
variable "sharedCredentialsFile" {
  default = "SHARED_CREDENTIALS_FILE_PH"
}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~ END OF VARS  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
