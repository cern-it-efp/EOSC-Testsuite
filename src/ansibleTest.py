#!/usr/bin/env python3

import sys
import os
import json
import time
from provisionment import *

# Needed files
playbookPath = "provisionment/playbooks/bootstraper.yaml"
pathToTFfiles = "tests/sharedCluster_ansibleTests"
hostsFilePath = "tests/sharedCluster_ansibleTests/hosts"

# TODO: take this from configs.yaml
provider = "aws"
provider = "google"
provider = "azurerm"
provider = "openstack"
provider = "cloudstack"
provider = "exoscale"

originalPath = os.getcwd()

# --------------- RUN TERRAFORM
os.chdir(pathToTFfiles)
os.system("terraform init ; terraform apply -auto-approve")

# --------------- CREATE hosts FILE WITH THE IPs
tfShow = os.popen("terraform show -json").read().strip()
os.chdir(originalPath)
resources = json.loads(tfShow)["values"]["root_module"]["resources"]
createHostsFile(resources, provider, hostsFilePath) # TODO: 'hosts' file should be located where the terraform state files are placed (where terraform is run)

# --------------- RUN ANSIBLE
runPlaybook(playbookPath, hostsFilePath)
