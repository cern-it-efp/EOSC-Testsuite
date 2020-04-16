#!/usr/bin/env python3

import yaml
import json
import requests
import oci
from oci.config import validate_config
import os
import logging
import sys

# Enable debug logging
logging.getLogger('oci').setLevel(logging.DEBUG)

with open("/home/ipelu/Desktop/oracle.yaml","r") as infile:
    configs = yaml.load(infile, Loader=yaml.FullLoader)

compartment_ocid = configs["compartment_ocid"]
tenancy_ocid = configs["tenancy_ocid"]
user_ocid = configs["user_ocid"]

auth = {
    "user": user_ocid,
    "tenancy": tenancy_ocid,
    "key_file": configs["keyPath"],
    "fingerprint": configs["fingerprint"],
    "region": configs["region"],
#    "log_requests": True
}

networkClient = oci.core.VirtualNetworkClient(auth)
computeClient = oci.core.ComputeClient(auth)

launch_instance_details = oci.core.models.LaunchInstanceDetails(
    availability_domain = configs["availability_domain"],
    compartment_id = compartment_ocid, shape = configs["shape"],
    subnet_id = "ocid1.subnet.oc1.eu-frankfurt-1.aaaaaaaa5lskgeionwxevi3sln5p6vvg2o2b3s5kt7wilvew5hjylx6m2gra",
    image_id = "ocid1.image.oc1.eu-frankfurt-1.aaaaaaaawtnpiyjp36tyx7hkkymil2efkvitkrrnqi5qjpahcuoyvtcwhc5q")

create_vcn_details = {"cidrBlock": configs["cidr_block_vcn"],
                      "compartmentId": compartment_ocid,
                      "displayName": "vcnSDK"}

try: # Both throw the same error NotAuthorizedOrNotFound
    networkClient.create_vcn(create_vcn_details)
    #computeClient.launch_instance(launch_instance_details)
except BaseException as e:
    print(e)
sys.exit()

vcns = networkClient.list_vcns(compartment_ocid)

for vcn in vcns.data:
    print(vcn)
