#!/usr/bin/env python3

import sys
import os
import json
import time
from myAnsible import *

# Needed files
playbookPath = "playbooks/bootstraper.yaml"
hostsFilePath = "hosts"

# TODO: take this from configs.yaml
provider = "exoscale"
provider = "aws"
provider = "google"
provider = "azurerm"
provider = "openstack"
provider = "cloudstack"

originalPath = os.getcwd()

# --------------- RUN TERRAFORM INSIDE 'vm'
os.chdir("vm")
os.system("terraform init ; terraform apply -auto-approve")

# --------------- CREATE hosts FILE WITH THE IPs
tfShow = os.popen("terraform show -json").read().strip()
os.chdir(originalPath)
resources = json.loads(tfShow)["values"]["root_module"]["resources"]
createHostsFile(resources, provider, destination) # TODO: 'hosts' file should be located where the terraform state files are placed (where terraform is run)

# --------------- RUN ANSIBLE
runPlaybook(playbookPath, hostsFilePath)
