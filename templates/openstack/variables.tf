variable "customCount" {
  default = NODES_PH
}
variable "clusterRandomID" {
  default = "RANDOMID_PH"
}
variable "pathToKey" {
  default = "PATH_TO_KEY_VALUE"
}
variable "kubeconfigDst" {
  #default = "KUBECONFIG_DST"
  default = "config"
}
variable "openUser" {
  default = "OPEN_USER_PH"
}
variable "instanceName" {
  default = "INSTANCE_NAME_PH" # main.py generates name: kubenode-provider-randomId
}
variable "flavor" {
  default = _PH
}
variable "imageName" {
  default = _PH
}
variable "keyPair" {
  default = _PH
}
variable "securityGroups" { # this is an array: ["default","allow_ping_ssh_rdp"]
  default = _PH
}
variable "region" { # neither CERN nor cf allow setting region (at least from the UI)
  default = _PH
}
variable "availabilityZone" { # cern os allows selecting Availability Zone / cf allows specifying it too but the only possible option in the dropdown is "nova"
  default = _PH
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
