############################ COMMON ONES #######################################
variable "customCount" {
  default = NODES_PH
}
variable "pathToKey" {
  default = "PATH_TO_KEY_VALUE"
}
variable "kubeconfigDst" {
  default = "KUBECONFIG_DST"
}
variable "openUser" {
  default = "OPEN_USER_PH"
}
variable "instanceName" {
  default = "NAME_PH"
}
# -------------------------- General -------------------------------------------
variable "sshConnect" {
  default = "../../terraform/ssh_connect.sh"
}
variable "clusterCreator" {
  default = "../../terraform/cluster_creator.sh"
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
# TODO: check which ones are optional from the following ones (for cern os had enough with: flavor_name, name, image_name, key_pair)
variable "flavor" {
  default = "FLAVOR_PH"
}
variable "imageName" {
  default = "IMAGE_PH"
}
variable "keyPair" {
  default = "KEY_PAIR_PH"
}
variable "securityGroups" { # this is an array: ["default","allow_ping_ssh_rdp"]
  default = "SEC_GROUPS_PH"
}
# Optional
variable "regionOS" { # neither CERN nor cf allow setting region (at least from the UI)
  default = "REGION_OS_PH"
}
variable "availabilityZone" { # cern os allows selecting Availability Zone / cf allows specifying it too but the only possible option in the dropdown is "nova"
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
variable "zone" {
  default = "ZONE_PH"
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
variable "regionAWS" {
  default = "REGION_AWS_PH"
}
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
variable "sharedCrdentialsFile" {
  default = "SHARED_CREDENTIALS_FILE_PH"
}
