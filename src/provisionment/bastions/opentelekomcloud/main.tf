provider "opentelekomcloud" { # TODO: for auth use token or aksk ? maybe just token and provide it as var. Possible to load a var from a file? or use file() directly on token and ask the user to create such file and provide its path?
  access_key  = "${var.access_key}"
  secret_key  = "${var.secret_key}"
  token       = "${var.token}"
  domain_name = "${var.domain_name}"
  tenant_name = "${var.tenant_name}"
  auth_url    = "https://iam.eu-de.otc.t-systems.com/v3"
}

resource "opentelekomcloud_compute_instance_v2" "tslauncher" {
  flavor_name           = "eo1.medium"
  name                  = "tslauncher"
  image_name = "CentOS 7"
  key_pair = "mykey"
  security_groups = ["default","allow_ping_ssh_rdp"]
}
