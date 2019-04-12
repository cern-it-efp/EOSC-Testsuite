#!/usr/bin/env python3
import getopt
import random
import string
import os
import sys
try:
    import yaml
except:
    print("pyyaml module missing!")
    sys.exit(1)

sys.path.append('./aux/')
from aux_functions import logger, checker

logger("OCRE Cloud Benchmarking Validation Test Suite (CERN)", "#")

autoRetry = False
onlyTest = False
viaBackend = False
# TODO: use here the address:port of the production backend at CERN cloud
backend = "188.185.73.119:9000"
randomId = ''.join(random.SystemRandom().choice(
    string.ascii_uppercase + string.digits) for _ in range(4))
configs = ""
repo = "https://github.com/cern-it-efp/OCRE-Testsuite"


def setName(instance, isMaster):
    """Generates the name for a VM.

    Parameters:
        instance (str): Instance's raw name
        isMaster (bool): Indicates whether instance is k8s master

    Returns:
        str: Name for the instance

    """

    if "\"#NAME" not in instance:
        print("The placeholder comment for name at configs.yaml was not found!")
        sys.exit(1)
    elif isMaster is True:
        instance = instance.replace(
            "\"#NAME", "-master-" + str(randomId) + "\"")
    else:
        instance = instance.replace(
            "\"#NAME", "-slave${count.index+1}-" + str(randomId) + "\"")
    return instance


def initAndChecks():
    """Initial checks and initialization of variables.

    Returns:
        Integer: Number of tests selected.

    """

    # --------File check
    global configs
    selected = 0
    # delete join.sh file from previous run
    os.system("rm -f terraform/join.sh")
    if os.path.exists("configs.yaml") is False:
        print("Configuration file not found")
        sys.exit(1)
    with open("configs.yaml", 'r') as stream:
        try:
            configs = yaml.load(stream, Loader=yaml.FullLoader)
        except yaml.YAMLError:
            print("Error loading yaml file")
            sys.exit(1)
        except:
            try:
                configs = yaml.load(stream)
            except yaml.YAMLError:
                print("Error loading yaml file")
                sys.exit(1)

    # --------General config checks
    checker(configs, ['auth', 'useFile'])
    if configs['auth']['useFile'] is not True:
        checker(configs, ['auth', 'credentials'])
    checker(configs, ['general', 'clusterNodes'])
    checker(configs, ['general', 'providerName'])
    checker(configs, ['general', 'providerInstanceName'])
    checker(configs, ['general', 'pathToKey'])
    checker(configs, ['instanceDefinition'])

    # --------Tests config checks (only few tests have var besides 'run')
    tc = configs["testsCatalog"]
    if tc["s3Test"]["run"] and tc["s3Test"]["run"] is True:
        selected += 1
        checker(configs, ['testsCatalog', 's3Test', 'endpoint'])
        checker(configs, ['testsCatalog', 's3Test', 'accessKey'])
        checker(configs, ['testsCatalog', 's3Test', 'secretKey'])
    if tc["perfsonarTest"]["run"] and tc["perfsonarTest"]["run"] is True:
        selected += 1
        checker(configs, ['testsCatalog', 'perfsonarTest', 'endpoint'])
    if tc["mlTest"]["run"] and tc["mlTest"]["run"] is True:
        selected += 1
    if tc["dataRepatriationTest"]["run"] and tc["dataRepatriationTest"]["run"] is True:
        selected += 1
    if tc["cpuBenchmarking"]["run"] and tc["cpuBenchmarking"]["run"] is True:
        selected += 1
    if tc["hpcTest"]["run"] and tc["hpcTest"]["run"] is True:
        selected += 1

    return selected


def onlyTesting(selected):
    """Runs only tests section, no provisioning.

    Parameters:
        selected (integer): Number of tests selected.
    """

    print("(ONLY TEST EXECUTION)")

    if selected < 1:
        print("No tests selected, nothing to do!")
        exit()
    os.system("cd tests && chmod +x run_tests.py && ./run_tests.py --only-test")
    exit()


def getIPcaller(provider):
    """Get the Terraform function provided by the supplier to get an instance IP.

    Parameters:
        provider (str): Name of the provider being tested

    Returns:
        str: get IP function
    """

    provDict = {  # TODO: update this as more providers are tested
        'openstack': '${self.network.0.fixed_ip_v4}',
        'exoscale': '${self.ip_address}',
        'aws': '${self.public_ip}',
        'google': '${self.public_ip}',
        'opentelekomcloud': '${self.public_ip}',
        'cloudstack': '${self.public_ip}',
        'cloudscale': '${self.public_ip}',
        'azurestack': '${self.public_ip}',
        'ibm': '${self.ip_address}'
    }
    if provider not in provDict:
        print("Error with provider name '%s'! Quitting." % (provider))
        sys.exit(1)
    return provDict[provider]


def createMain():
    """Generate Terraform's main.tf file."""

    with open('./terraform/raw/main_raw.tf', 'r') as myfile:
        mainStr = myfile.read()
    if configs['auth']['useFile'] is not True:
        mainStr = mainStr.replace(
            "CREDENTIALS_PLACEHOLDER", str(configs["auth"]["credentials"]))
    else:
        mainStr = mainStr.replace("CREDENTIALS_PLACEHOLDER", "")

    mainStr = mainStr.replace("SLAVE_NODES", str(
        configs["general"]["clusterNodes"] - 1)).replace(
        "PROVIDER_NAME", str(configs["general"]["providerName"])).replace(
        "PROVIDER_INSTANCE_NAME", str(configs["general"]["providerInstanceName"])).replace(
        "PATH_TO_KEY_VALUE", str(configs["general"]["pathToKey"])).replace(
        "MASTER_DEFINITION_PLACEHOLDER", str(setName(configs["instanceDefinition"], True))).replace(
        "SLAVE_DEFINITION_PLACEHOLDER", str(setName(configs["instanceDefinition"], False))).replace(
        "NODE_IP_GETTER", getIPcaller(configs["general"]["providerName"]))

    # STACK VERSIONING
    if configs["general"]["dockerCE"]:
        mainStr = mainStr.replace(
            "DOCKER_CE_PH", str(configs["general"]["docker-ce"]))
    else:
        mainStr = mainStr.replace("DOCKER_CE_PH", "")
    if configs["general"]["dockerEngine"]:
        mainStr = mainStr.replace("DOCKER_EN_PH", str(
            configs["general"]["dockerEngine"]))
    else:
        mainStr = mainStr.replace("DOCKER_EN_PH", "")
    if configs["general"]["kubernetes"]:
        mainStr = mainStr.replace(
            "K8S_PH", str(configs["general"]["kubernetes"]))
    else:
        mainStr = mainStr.replace("K8S_PH", "")
    with open("./terraform/main.tf", 'w') as textFile:
        textFile.write(mainStr)


def backendRun(selected):
    """Runs the Test-Suite via the backend service. Used for tests results verification."""

    if selected < 1:
        print("No tests selected, nothing to do!")
        exit()
    if os.path.exists(os.environ['HOME'] + "/.kube/config") is False:
        print("File ~/.kube/config not found!")
        sys.exit(1)
    answer = input(
        "WARNING: backend verification run pushes results to bucket, continue? (yes/no)")
    if answer == "yes":
        print("Verification Run: Waiting for backend response...")
        os.system(
            "curl -F configs=@$HOME/.kube/config -F configs=@configs.yaml \"%s/run\"" % (backend))
        sys.exit(0)
    elif answer == "no":
        print("Quitting.")
        sys.exit(0)
    else:
        print("Unknown answer, quitting.")
        sys.exit(0)


# -----------------CMD OPTIONS---------------------------------------------------
try:
    opts, args = getopt.getopt(
        sys.argv, "ul", ["--only-test", "--via-backend"])
except getopt.GetoptError as err:
    print(err)
    sys.exit(1)
for arg in args[1:len(args)]:
    if arg == '--auto-retry':
        autoRetry = True
    elif arg == '--only-test':
        onlyTest = True
    elif arg == '--via-backend':
        viaBackend = True
    else:
        print("Unknown option '%s'. Refer to the documentation at %s for help/info" % (arg, repo))
        sys.exit(1)

# -----------------CHECKS AND PREPARATION----------------------------------------
selected = initAndChecks()
if viaBackend is True:
    backendRun(selected)
if onlyTest is True:
    onlyTesting(selected)
createMain()

# -----------------SCRIPT READY => RUN ------------------------------------------
output = os.system('cd terraform/ && terraform init && terraform apply')
if autoRetry is False:
    if output != 0:
        print(
            "ERRORS OCCURED! Fix them according to the shown message and rerun the test-suite.")
        sys.exit(1)
else:
    while output != 0:
        output = os.system("cd terraform/ && terraform apply")

if selected > 0:
    logger("INFRASTRUCTURE CREATED => STARTING TESTS", "#")
    os.system("cd tests/ && chmod +x run_tests.py && ./run_tests.py")
else:
    logger("No tests selected => Raw Kubernetes cluster created", "#")
