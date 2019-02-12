#-------------provider
variable "provider_name" {
  default = "openstack"
}

variable "provider_resource" {
  default = "openstack_compute_instance_v2"
}

#-------------resources
variable "node-count" {
  default = "4"
}

variable "image-name" {
  default = "CC7 - x86_64 [2018-12-03]"
}

variable "image-flavor" {
  default = "m2.medium"
}

variable "security-groups" {
  default = "default"
}

variable "key-pair" {
  default = "tf-key"
}

#-------------authentication
variable "path_to_key" {
  default = "~/.ssh/id_rsa"
} #must be same key! tf-key.

variable "api_key" {
  default = "1ac0fb0095f3411581cf86aed9b9b22b"
}

variable "secret_key" {
  default = "3a8da6a013874774916b70a8a6674171"
}

variable "auth_url" {
  default = "https://openstack.cern.ch:8772"
}

variable "token" {
  default = "3a8da6a013874774916b70a8a6674171"
}
#---------------------
