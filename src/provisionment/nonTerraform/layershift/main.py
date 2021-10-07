#!/usr/bin/env python3

import yaml
import requests
import os
import json
import jsonschema
import sys
import argparse


k8senv_raw_path = "k8s-full-raw"
k8senv_path = "k8s-full.yaml"
installURL = "https://app.j.layershift.co.uk/marketplace/jps/rest/install"
configsSchema = "/data/career/cern/repos/EOSC-Testsuite/src/schemas/configs_sch_layershift.yaml"
clusterDetails = "response.json"

def loadFile(loadThis, required=None):
    """ Loads a file. """

    with open(loadThis, 'r') as inputfile:
        if ".yaml" in loadThis:
            try:
                return yaml.load(inputfile, Loader=yaml.FullLoader)
            except AttributeError:
                try:
                    return yaml.load(inputfile)
                except:  # yaml.scanner.ScannerError:
                    print("Error loading yaml file " + loadThis)
                    sys.exit()
            except:  # yaml.scanner.ScannerError:
                print("Error loading yaml file " + loadThis)
                sys.exit()
        else:
            return inputfile.read().strip()

def createCluster():
    """ Create a cluster. """

    cmd = "curl --silent -X POST '%s' --data session=%s --data-urlencode jps@%s" % (installURL, token, k8senv_path)
    resp = os.popen(cmd).read().strip()
    print("Cluster create curl response: %s" % resp)

    clusterParams = {}
    clusterParams["apiEndpoint"] = json.loads(resp)["startPage"]
    clusterParams["accessToken"] = json.loads(resp)["successText"]
    clusterParams["environmentName"] = json.loads(resp)["startPage"].replace("https://","").replace(".j.layershift.co.uk/api/","")

    #Persist cluster details # TODO: if the previous curl fails, the cluster may be created but not the response.json file
    with open(clusterDetails, 'w') as outfile:
        json.dump(clusterParams, outfile, indent=4, sort_keys=True)

    return clusterParams


def configKubectl(clusterParams):
    """ Configure kubectl. """

    cmd = "kubectl config set-cluster jelastic --server=%s && " \
          "kubectl config set-context jelastic --cluster=jelastic && " \
          "kubectl config set-credentials user --token=%s && " \
          "kubectl config set-context jelastic --user=user && " \
          "kubectl config use-context jelastic &> /dev/null" % (clusterParams["apiEndpoint"], clusterParams["accessToken"])

    exitCode = os.system(cmd)
    while exitCode != 0:
        print("Failed to create kubeconfig, retrying in 5 seconds...")
        exitCode = os.system(cmd)


def clusterCleanup():
    """ Delete all resources from the cluster. """

    cmd = "kubectl delete service --all; " \
          "kubectl delete daemonset --all; " \
          "kubectl delete deployment --all; " \
          "kubectl delete service --all; " \
          "kubectl delete pods --all"
    return os.system(cmd)


def destroyCluster(envName, token):
    """ Destroy a given cluster. """

    cmd = "curl --silent -X POST 'https://app.j.layershift.co.uk/1.0/environment/" \
          "control/rest/deleteenv?envName=%s&session=%s'" % (envName, token)
    resp = os.popen(cmd).read().strip()
    return json.loads(resp)["result"]


# -----------------CMD OPTIONS--------------------------------------------------
parser = argparse.ArgumentParser(prog="./main.py",
                                 description='Layershift cluster provisionment script.',
                                 allow_abbrev=False)
parser.add_argument('-c',
                    required=True,
                    help='Path to configs.',
                    type=str,
                    dest="cfgPathCLI")
parser.add_argument('-d',
                    help='Destroy existing cluster.',
                    action='store_true',
                    dest="destroyFlag")
parser.add_argument('--cluster',
                    help='Cluster (environment) name.',
                    type=str,
                    dest="envName")

args = parser.parse_args()

configs_path = os.path.abspath(args.cfgPathCLI) # ../../../../examples/layershift/configs.yaml
# ------------------------------------------------------------------------------


######## Load configs
try:
    configs = loadFile(configs_path)
    jsonschema.validate(configs, loadFile(configsSchema))
    nodes = int(configs["nodes"]) - 1 # This will set the number of worker nodes, so -1 because the master also counts
    cores = configs["cores"]
except jsonschema.exceptions.ValidationError as ex:
    print("Error validating configs file: \n %s" % ex.message)
    sys.exit()

######## Load token
try:
    tokenPath = loadFile(configs["tokenPath"])
    token = tokenPath["token"]
except:
    print("Unable to correctly read token file")
    sys.exit()


if args.destroyFlag:
    if args.envName:
        if destroyCluster(args.envName, token) == 0:
            print("Cluster removed")
        else:
            print("Error removing cluster")
    elif os.path.isfile(clusterDetails) is True:
        envName = json.loads(loadFile(clusterDetails))["environmentName"]
        if destroyCluster(envName, token) == 0:
            os.remove(clusterDetails)
            print("Cluster removed")
        else:
            print("Error removing cluster")
    else:
        print("No cluster exists, nothing to do")
    sys.exit()
else:
    ######## Write the YAML defining the new environment
    with open(k8senv_path, 'w') as outfile:
        k8senv_raw_content = loadFile(k8senv_raw_path).replace(
                              "NODES_PH", str(nodes)).replace(
                              "CORES_PH", str(cores))
        outfile.write(k8senv_raw_content)

    if os.path.isfile(clusterDetails) is True:
        print("A cluster already exists.")
        sys.exit()

    print("#### Creating cluster... (takes around 10 minutes)")
    respCC = createCluster()

    print("#### Cluster created, configuring it...")
    configKubectl(respCC)

    print("#### Cluster cleanup...")
    clusterCleanup()

    print("#### DONE (manage ~/.kube/config)")
