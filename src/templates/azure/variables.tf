variable "customCount" {
  default = NODES_PH
}
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
  default = "INSTANCE_NAME_PH"
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

# ---------------------------------------- FOR DEBUGGING PURPOSES ----------------------------------------
variable "sshConnect" {
  default = "../../terraform/ssh_connect.sh"
}
variable "clusterCreator" {
  default = "../../terraform/cluster_creator.sh"
}
variable "sshcTimeout" {
  default = "2000"
}
# ------------------------------------------------------------------------------------------------------------------------

# ---------------------------------------- Optional ----------------------------------------
variable "dockerCeVer" {
  default = "DOCKER_CE_PH"
}
variable "dockerEnVer" {
  default = "DOCKER_EN_PH"
}
variable "k8sVer" {
  default = "K8S_PH"
}
# ------------------------------------------------------------------------------------------------------------------------
