#!/usr/bin/env python

import string
import random
import os
import yaml
import sys, getopt
import re

print ("")
print ("#########################################################")
print ("#                                                       #")
print ("#        TEST SUITE - CLOUD BENCHMARKING (CERN)         #")
print ("#                                                       #")
print ("#########################################################")
print ("")


with open('./terraform/raw/main_raw.tf', 'r') as myfile:
    main_str = myfile.read()

latest = ""
uninstall = ""

def onlyTest():
    print ("-------------------ONLY TEST EXECUTION-------------------")
    os.system("cd tests && chmod +x run_tests.py && ./run_tests.py --only-test")
    exit()

try:
    opts, args = getopt.getopt(sys.argv,"ul",["--only-test"])
except getopt.GetoptError as err:
    print (err)
    sys.exit(2)
for arg in args[1:len(args)]:
    if arg == '-l':
        latest = True
    elif arg == '-u':
        uninstall = True
    elif arg == '--only-test':
        onlyTest()
    else:
        print ("Unknown option " + arg +". Refer to the documentation at https://gitlab.cern.ch/ipeluaga/test-suite for help/info")
        sys.exit(2)

if os.path.exists("configs.yaml") == False:
    print("Configuration file not found")
    sys.exit(2)

with open("configs.yaml", 'r') as stream:
    try:
        configs = yaml.load(stream)
    except yaml.YAMLError as exc:
        print("Error loading yaml file")
        sys.exit(2)

random_id = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(4))
def setName(instance, isMaster):
    if "\"#NAME" not in instance:
        print ("The placeholder comment for name at configs.yaml was not found!")
        sys.exit(2)
    elif isMaster==True:
        instance = instance.replace("\"#NAME", "-master-"+str(random_id)+"\"")
    else:
        instance = instance.replace("\"#NAME", "-slave${count.index+1}-"+str(random_id)+"\"")
    return instance

def yaml2str(yaml):
    res = str(yaml).replace(':','=').replace('\'secret\'','secret').replace('\'key\'','key').replace('\'','\"')
    return re.sub('[{},]','',res)

main_str = main_str.replace("CREDENTIALS_PLACEHOLDER",str(yaml2str(configs["credentials"])))
main_str = main_str.replace("SLAVES_AMOUNT",str(configs["general"]["slaves_amount"]))
main_str = main_str.replace("PROVIDER_NAME",str(configs["general"]["provider_name"]))
main_str = main_str.replace("PROVIDER_INSTANCE_NAME",str(configs["general"]["provider_instance_name"]))
main_str = main_str.replace("PATH_TO_KEY_VALUE",str(configs["general"]["path_to_key"]))
main_str = main_str.replace("MASTER_DEFINITION_PLACEHOLDER",str(setName(configs["instance_definition"], True)))
main_str = main_str.replace("SLAVE_DEFINITION_PLACEHOLDER",str(setName(configs["instance_definition"], False)))

with open("./terraform/main.tf", "w") as text_file:
    text_file.write(main_str)

os.system("cd terraform/ && terraform init && terraform apply && cd ../tests/ && chmod +x run_tests.py && ./run_tests.py")
