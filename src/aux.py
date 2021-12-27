#!/usr/bin/env python3

import sys
try:
    import yaml
    import json
    import os
    import datetime
    import time
    import subprocess
    import jsonschema
    import shutil
    import random
    import string
    import glob
    from configparser import ConfigParser

except ModuleNotFoundError as ex:
    print(ex)
    sys.exit(1)

yaml.warnings({'YAMLLoadWarning': False}) # https://github.com/yaml/pyyaml/wiki/PyYAML-yaml.load(input)-Deprecation


def checkFormerInfraFiles():
    """ Checks if there are Terraform state files from a previous run. """

    if len(glob.glob("src/tests/*/terraform.tfstate")) == 0:
        return True
    return False

def getRandomID():
    """ Returns a random ID """

    choices = string.ascii_lowercase + string.digits
    randomId = ''.join(random.SystemRandom().choice(choices) for _ in range(4))
    return str(randomId)


def getMasterIP(hosts):
    """ Given the path to an ansible hosts file, returns the IP specified
        under the master section of the file.

    Parameters:
        hosts (str): Path to an ansible hosts file.

    Returns:
        str: IP of the master node.
    """

    config = ConfigParser(allow_no_value=True)
    config.read(hosts)
    return config.items('master')[0][0]


def runCMD(cmd, hideLogs=None, read=None):
    """ Run the command.

    Parameters:
        cmd (str): Command to be run.
        hideLogs (bool): Indicates whether cmd logs should be hidden.
        read (bool): Indicates whether logs of the command should be returned.

    Returns:
        int or str: Command's exit code. Logs of the command if read=True
    """

    #print(cmd)

    if read is True:
        return os.popen(cmd).read().strip()
    if hideLogs is True:
        return subprocess.call(
            cmd, shell=True, stdout=open(
                os.devnull, 'w'), stderr=subprocess.STDOUT)
    else:
        return os.system(cmd)


def stop(code):
    """ Stops the TS run exiting using the provided status code

    Parameters:
        code (int): Exit code to be used
    """

    time.sleep(2)
    sys.exit(code)


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
            stop(1)
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
                    stop(1)
            except:  # yaml.scanner.ScannerError:
                print("Error loading yaml file " + loadThis)
                stop(1)
        else:
            return inputfile.read().strip()


def loadYAML(loadThis, required=None):
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
            stop(1)
        else:
            return ""
    with open(loadThis, 'r') as inputfile:
        try:
            return yaml.load(inputfile, Loader=yaml.FullLoader)
        except AttributeError:
            try:
                return yaml.load(inputfile)
            except:  # yaml.scanner.ScannerError:
                print("Error loading yaml file " + loadThis)
                stop(1)
        except:  # yaml.scanner.ScannerError:
            print("Error loading yaml file " + loadThis)
            stop(1)


def writeToFile(filePath, content, append):
    """ Writes stuff to a file.

    Parameters:
        filePath (str): Path to the file to load
        content (str): Content to write to the file
        append (bool): If true, the content has to be appended.
                       False overrides the file or creates if not existing
    """

    mode = 'w'
    if append is True:
        mode = 'a'
    with open(filePath, mode) as outfile:
        outfile.write(content + '\n')


def writeFail(resDir, file, msg, toLog):
    """ Writes results file in case of errors.

    Parameters:
        resDir (str): Path to the results folder.
        file (str): Name of the results file.
        msg (str): Message to write to results file.
        toLog (str): File to which write the log msg.
    """

    writeToFile(toLog, msg, True)
    with open(resDir + "/" + file, 'w') as outfile:
        json.dump({"info": msg, "result": "fail"},
                  outfile, indent=4, sort_keys=True)


def logger(text, sym, file, override=None):
    """ Logs in a fancy way.

    Parameters:
        text (str): Text to log
        sym (str): Symbol to use to create boxes and separation lines
        file (str): File the logs should be sent to
        override (bool): Override the file or not.
    """

    size = 74  # longest msg on code (was 61)
    frame = sym * (size + 6)
    blank = sym + "  " + " " * size + "  " + sym
    toPrint = frame + "\n" + blank
    if isinstance(text, list):
        for i in text:
            textLine = i.rstrip()  # strip()
            toPrint += "\n" + sym + "  " + textLine + \
                " " * (size - len(textLine)) + "  " + sym
    else:
        text = text.rstrip()  # strip()
        toPrint += "\n" + sym + "  " + text + \
            " " * (size - len(text)) + "  " + sym
    toPrint += "\n" + blank + "\n" + frame
    if file and override is True:
        runCMD("echo \"%s\" > %s" % (toPrint, file))
    elif file and override is not True:
        runCMD("echo \"%s\" >> %s" % (toPrint, file))
    else:
        print(toPrint)


def tryTakeFromYaml(dict, key, defaultValue, msgExcept=None):
    """ Tries to return the dict's value for key 'key'. If KeyError
        exception is thrown, returns the specified default value.

    Parameters:
        dict (dict): Dict object loaded from a yaml file.
        key (object): Key whose value should be returned if existing.
        defaultValue (object): value to return in case of KeyError exception.
        msgExcept (str): Message to show in case of exception.

    Returns
        Object taken from the yaml file (dict) or default one.
    """

    try:
        if '.' in key:
            key1,key2 = key.split('.')
            return dict[key1][key2]
        else:
            return dict[key]
    except KeyError:
        if msgExcept is not None:
            print(msgExcept)
        return defaultValue


def validateConfigs(cfgPath, tcPath, noTerraform, extraSupportedClouds, allTests):
    """ Validates configs.yaml and testsCatalog.yaml file against schemas.

    Parameters:
        cfgPath (str): Path to configs YAML file.
        tcPath (str): Path to testsCatalog YAML file.
        noTerraform (bool): Specifies whether current run uses terraform.
        extraSupportedClouds (dict): Extra supported clouds.
        allTests (array): Contains all test names.
    """

    configs = loadFile(cfgPath, required=True)
    testsCatalog = loadFile(tcPath, required=True)

    if noTerraform is False:
        try:
            configsSchema = "src/schemas/configs_sch_%s.yaml" % \
            configs["providerName"] if configs["providerName"] \
                in extraSupportedClouds else "src/schemas/configs_sch_general.yaml"
            testsCatalogSchema = "src/schemas/testsCatalog_sch.yaml"
        except KeyError:
            print("Error validating configs file: missing 'providerName'")
            stop(1)
    else:
        configsSchema = "src/schemas/configs_sch_noTerraform.yaml"
        testsCatalogSchema = "src/schemas/testsCatalog_sch_noTerraform.yaml"

    # ------ configs.yaml
    try:
        jsonschema.validate(configs, loadFile(configsSchema))
    except jsonschema.exceptions.ValidationError as ex:
        print("Error validating configs file: \n %s" % ex.message)
        stop(1)
    # ------------------

    # ------ testsCatalog.yaml
    try:
        jsonschema.validate(testsCatalog, loadFile(testsCatalogSchema))
    except jsonschema.exceptions.ValidationError as ex:
        print("Error validating testsCatalog file: \n %s" % ex.message)
        stop(1)

    for test in allTests:
        try:
            testsCatalog[test]
        except KeyError:
            testsCatalog[test] = {"run":False}
    # ------------------

    return configs, testsCatalog


def validateAuth(authFile, schema):
    """ Validates authFile schemas.

    Parameters:
        authFile (dict): Content of the authentication file.
        schema (dict): Validation schema.
    """

    # ------ configs.yaml
    try:
        jsonschema.validate(authFile, schema)
    except jsonschema.exceptions.ValidationError as ex:
        print("Error validating authFile file: \n %s" % ex.message)
        stop(1)
    # ------------------


def getNodeName(configs, test, randomId):
    """ Generates a node name containing the provider name, test and a unique
        identifier.

    Parameters:
        dict (dict): Dict object loaded from a yaml file.
        key (object): Key whose value should be returned if existing.
        defaultValue (object): value to return in case of KeyError exception.

    Returns
        Object taken from the yaml file (dict) or default one.
    """

    nodeName = "kubenode-%s-%s-%s" % (configs["providerName"],test,randomId)
    return nodeName.lower()


def subprocPrint(test):
    """ Runs on a child process. Reads the ansible log file, adds clusterID
        to each line and prints it.

    Parameters:
        test (str): Cluster identification.
    """

    line = None
    with open(ansibleLogs % test, 'r') as f:
        while True:
            line = f.readline()
            if len(line) > 0 and line != '\n':
                print("[ %s ] %s" % (test, line.replace('\n', '')))


def getIP(resource, configs, public=False):
    """ Given a terraform resource json description, returns the resource's
        IP address if such exists

    Parameters:
        resource (object): Terraform resource definition.
        configs (str): Configurations (from YAML).
        public (bool): If True, get the public IP.

    Returns:
        str: Resource's IP address.
    """

    provider = configs["providerName"]

    try:
        if provider == "aws":
            if public is True:
                return resource["values"]["public_ip"]
            return resource["values"]["private_ip"]

        elif provider == "google":
            if public is True:
                return resource["values"]["network_interface"][0]["access_config"][0]["nat_ip"]
            return resource["values"]["network_interface"][0]["network_ip"]

        elif provider == "openstack":
            openstackVendor = tryTakeFromYaml(configs, "vendor", None)
            if public is not True or openstackVendor == "ovh":
                return resource["values"]["network"][0]["fixed_ip_v4"]
            else:
                return resource["values"]["floating_ip"] # type: openstack_compute_floatingip_associate_v2

        elif provider == "opentelekomcloud" or provider == "flexibleengine":
            if public is True:
                return resource["values"]["floating_ip"] # type: opentelekomcloud_compute_floatingip_associate_v2 / flexibleengine_compute_floatingip_associate_v2
            return resource["values"]["access_ip_v4"]

        elif provider == "azurerm":
            if public is True:
                return resource["values"]["ip_address"] # type: azurerm_public_ip
            return resource["values"]["private_ip_address"]

        elif provider == "yandex":
            if public is True:
                return resource["values"]["network_interface"][0]["nat_ip_address"] # type: yandex_compute_instance
            return resource["values"]["network_interface"][0]["ip_address"]

        elif provider == "ibm":
            useClassic = configs["useClassic"]
            if public is True:
                if useClassic is True:
                    return resource["values"]["ipv4_address"] # Classic Infrastructure
                return resource["values"]["address"] # VPC Infrastructure
            if useClassic is True:
                return resource["values"]["ipv4_address_private"] # Classic Infrastructure
            return resource["values"]["primary_network_interface"][0]["primary_ipv4_address"] # VPC Infrastructure

        elif provider == "oci":
            if public is True:
                return resource["values"]["public_ip"]
            return resource["values"]["private_ip"]

        # --- The following ones offer public IPs w/o NAT

        elif provider == "exoscale":
            return resource["values"]["ip_address"]

        elif provider == "ionoscloud":
            return resource["values"]["primary_ip"] # type: ionoscloud_server

        elif provider == "cloudsigma":
            return resource["values"]["ipv4_address"] # type: cloudsigma_server

    except KeyError:
        return None # no IP was found for the given resource


def groupReplace(input,substitution,output):
    """ Given an input file, applies to it the provided substitution.

    Parameters:
        input (str): Input text.
        substitution (dict): Substitution to be done.
        output (str): Output text.
    """

    with open(input, 'r') as infile:
        infile = infile.read()
        for sub in substitution:
            infile = infile.replace(sub["before"], sub["after"])
        with open(output, 'w') as outfile:
            outfile.write(infile)
