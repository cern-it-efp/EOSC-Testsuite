#!/usr/bin/env python3

import sys
try:
    import yaml
    import json
    import getopt
    import jsonschema
    import os
    import subprocess

except ModuleNotFoundError as ex:
    print(ex)
    sys.exit(1)


def runCMD(cmd, hideLogs=None, read=None):
    """ Run the command.

    Parameters:
        cmd (str): Command to be run
        hideLogs (bool): Indicates whether cmd logs should be hidden
        read (bool): Indicates whether logs of the command should be returned

    Returns:
        int or str: Command's exit code. Logs of the command if read=True
    """

    if read is True:
        return os.popen(cmd).read().strip()
    if hideLogs is True:
        return subprocess.call(
            cmd, shell=True, stdout=open(
                os.devnull, 'w'), stderr=subprocess.STDOUT)
    else:
        return os.system(cmd)


def loadFile(loadThis, required=None):
    """ Loads a file

    Parameters:
        loadThis (str): Path to the file to load
        required (bool): Indicates whether the file is required

    Returns:
        str or yaml: The loaded file or empty string if the file was not found
                     and required is not True. Exits with code 1 otherwise.
    """

    if os.path.exists(loadThis) is False:
        if required is True:
            print(loadThis + " file not found")
            sys.exit(1)
        else:
            return ""
    with open(loadThis, 'r') as inputfile:
        if ".yaml" in loadThis:
            try:
                return yaml.load(inputfile, Loader=yaml.FullLoader)
            except AttributeError:
                try:
                    return yaml.load(inputfile)
                except:  # yaml.scanner.ScannerError:
                    print("Error loading yaml file " + loadThis)
                    sys.exit(1)
            except:  # yaml.scanner.ScannerError:
                print("Error loading yaml file " + loadThis)
                sys.exit(1)
        else:
            return inputfile.read().strip()


def validateConfigs(configs):
    """ Validates configs.yaml against schemas.

    Parameters:
        configs (dict): Object containing configs.yaml's configurations.
    """

    try:
        jsonschema.validate(configs, loadFile("resources/configs_sch.yaml"))
    except jsonschema.exceptions.ValidationError as ex:
        print("Error validating configs file: \n %s" % ex.message)
        sys.exit(1)


def destroyF():
    if runCMD("terraform destroy -var 'configsPath=%s' -auto-approve" % cfgPath) != 0:
        sys.exit(1)
    else:
        sys.exit(0)


cfgPath = None
destroy = False

# -----------------CMD OPTIONS--------------------------------------------
try:
    options, values = getopt.getopt(
        sys.argv[1:],
        "c:",
        ["destroy"])
except getopt.GetoptError as err:
    print(err)
    sys.exit(1)
for currentOption, currentValue in options:
    if currentOption in ['-c']:
        cfgPath = currentValue
    elif currentOption in ['--destroy']:
        destroy = True

if cfgPath is None:
    cfgPath = "configs.yaml"

configs = loadFile(cfgPath, required=True)
validateConfigs(configs)

if destroy is True:
    destroyF()

# ~~~~~~~~~~~~~~~ CHECK KEY PERMS. ARE 600 ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ #
if "600" not in oct(os.stat(configs["sshKey"]).st_mode & 0o777) and \
   "400" not in oct(os.stat(configs["sshKey"]).st_mode & 0o777):
    print("Key permissions too open, must be set to 600 or 400")
    sys.exit(1)


if runCMD("terraform init && terraform apply -var 'configsPath=%s' -auto-approve" % cfgPath) != 0:
    print("ERROR: failed to provision machine.")
    sys.exit(1)
