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

user = "ubuntu"
onlySsh = False

try:
    options, values = getopt.getopt(
        sys.argv[1:],
        "",
        ["onlySsh"])
except getopt.GetoptError as err:
    print(err)
    stop(1)
for currentOption, currentValue in options:
    if currentOption in ['--onlySsh']:
        onlySsh = True


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
    resources = json.loads(runCMD("terraform show -json | jq .values.root_module.resources",read=True).strip())
    try:
        for res in resources:
            if res["type"] == "oci_core_instance":
                return res["values"]["public_ip"]
    except:
        print("Does the VM exist?")
        sys.exit()

if onlySsh is not True:
    if runCMD("terraform apply -auto-approve") is not 0:
        print("fail terraform apply -auto-approve")
        sys.exit(1)

runCMD("ssh -o StrictHostKeyChecking=no %s@%s" % (user,getIP()))
