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
if ip is None:
    print("ip is a required option")
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

    # TODO: do this for all supported providers
    try:
        #resources = json.loads(runCMD("terraform show -json | jq .values.root_module.resources",read=True).strip()) # this is for AWS
        #for res in resources:
        #    if res["type"] == "oci_core_instance":
                if provider == "cloudstack":
                    return resource["values"]["ip_address"]
                elif provider == "aws":
                    return resource["values"]["public_ip"]
                elif provider == "azurerm":
                    return resource["values"]["private_ip_address"]
                elif provider == "openstack":
                    return resource["values"]["network"][0]["fixed_ip_v4"]
                elif provider == "google":
                    return resource["values"]["network_interface"][0]["network_ip"]
                elif provider == "opentelekomcloud":
                    return resource["values"]["access_ip_v4"]
                elif provider == "oci":
                    return resource["values"]["private_ip"]

    except:
        print("Does the VM exist?")
        sys.exit()

# start

baseCWD = os.getcwd()

os.chdir(tfPath)

if onlySsh is not True:
    if runCMD("terraform apply -auto-approve") is not 0:
        print("fail terraform apply -auto-approve")
        sys.exit(1)

#ip = getIP()

os.chdir(baseCWD)

#runCMD("ssh -o StrictHostKeyChecking=no %s@%s" % (user,getIP()))
runCMD("ssh -o StrictHostKeyChecking=no %s@%s" % (user,ip))
