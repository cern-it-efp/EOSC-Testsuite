#!/usr/bin/env python3

import sys
try:
    import yaml
    import getopt
    import json
    import os
    import datetime
    import time
    import subprocess
    import jsonschema
    import shutil
    from configparser import ConfigParser

except ModuleNotFoundError as ex:
    print(ex)
    sys.exit(1)

tfPath = None
user = None
ip = None
onlySsh = False

# TODO: take here the openUser, the key and other vars needed at the .tf script

try:
    options, values = getopt.getopt(
        sys.argv[1:],
        "",
        ["onlySsh","user=","ip=","tfPath="])
except getopt.GetoptError as err:
    print(err)
    sys.exit(1)
for currentOption, currentValue in options:
    if currentOption in ['--onlySsh']:
        onlySsh = True
    elif currentOption in ['--tfPath']:
        tfPath = currentValue
    elif currentOption in ['--user']:
        user = currentValue
    elif currentOption in ['--ip']:
        ip = currentValue

if tfPath is None:
    print("tfPath is a required option")
    sys.exit(1)
if user is None:
    print("user is a required option")
    sys.exit(1)

# TODO: check, if there are no .tf files at tfPath -> exit

def runCMD(cmd, hideLogs=None, read=None):
    if read is True:
        return os.popen(cmd).read().strip()
    if hideLogs is True:
        return subprocess.call(
            cmd, shell=True, stdout=open(
                os.devnull, 'w'), stderr=subprocess.STDOUT)
    else:
        return os.system(cmd)

def getIP():

    try:
        resources = json.loads(runCMD("terraform show -json | jq .values.root_module.resources",read=True).strip())
        for res in resources:
            if provider == "azurerm":
                if res["type"] == "azurerm_public_ip":
                    return res["values"]["ip_address"]

            elif provider == "oci":
                if res["type"] == "oci_core_instance":
                    return res["values"]["private_ip"]

            elif provider == "aws":
                if res["type"] == "aws_instance":
                    return resource["values"]["public_ip"]

            elif provider == "cloudstack":
                if res["type"] == "cloudstack_instance":
                    return resource["values"]["ip_address"]

            # TODO: do this for all supported providers

            elif provider == "openstack":
                if res["type"] == "":
                    return resource["values"]["network"][0]["fixed_ip_v4"]

            elif provider == "google":
                if res["type"] == "":
                    return resource["values"]["network_interface"][0]["network_ip"]

            elif provider == "opentelekomcloud":
                if res["type"] == "":
                    return resource["values"]["access_ip_v4"]

    except:
        print("Does the VM exist?")
        sys.exit()

# start

baseCWD = os.getcwd()

if tfPath is ".":
    provider = os.path.basename(os.path.normpath(os.getcwd()))
else:
    provider = os.path.basename(os.path.normpath(tfPath))

os.chdir(tfPath)

if onlySsh is not True:
    if provider == "azurerm": # TODO: in azurerm, w/o this the public ip is not initialized

#    resource "azurerm_virtual_network" "myterraformnetwork
#    resource "azurerm_subnet" "myterraformsubnet
#resource "azurerm_network_security_group" "myterraformnsg
#    resource "azurerm_public_ip" "myterraformpublicip
#    resource "azurerm_network_interface" "terraformnic
#resource "azurerm_virtual_machine" "main
#resource "null_resource" "docker"

        cmd = "terraform init ; terraform apply -target=azurerm_virtual_machine.main -auto-approve ; terraform apply -refresh=true -auto-approve"
    else:
        cmd = "terraform init ; terraform apply -auto-approve"

    if runCMD(cmd) is not 0:
        print("terraform failed")
        sys.exit(1)

ip = getIP()

os.chdir(baseCWD)

runCMD("ssh -o StrictHostKeyChecking=no %s@%s" % (user,ip))
