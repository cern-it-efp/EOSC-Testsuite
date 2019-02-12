#!/usr/bin/env python
import sys, getopt
import os
import yaml
import datetime
import platform
import subprocess

only_test = False
FNULL = open(os.devnull, 'w')

try:
    opts, args = getopt.getopt(sys.argv,"",["--only-test"])
except getopt.GetoptError as err:
    print (err)
    sys.exit(2)
for arg in args[1:len(args)]:
    if arg == '--only-test':
        only_test = True
    else:
        print ("Unknown option " + arg)

if only_test==False:
    print ("")
    print ("#########################################################")
    print ("#                                                       #")
    print ("#       INFRASTRUCTURE CREATED => STARTING TESTS        #")
    print ("#                                                       #")
    print ("#########################################################")
    print ("")



with open('../terraform/aux/master_ip', 'r') as myfile:
    master_ip = myfile.read()
master_ip = master_ip.strip()

with open("../configs.yaml", 'r') as stream:
    try:
        configs = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)


#-----------------CREATE RESULTS FOLDER-----------------------------------------
res_dir = str(datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S"))
os.mkdir("../results/"+res_dir)

#---------------------RUN THE TESTS---------------------------------------------

if(configs["tests_catalog"]["s3_test"]["run"]==True):
    print ("")
    print ("=========================================================")
    print ("")
    print ("                        S3 TEST ")
    print ("")
    print ("=========================================================")

    with open('s3/raw/s3pod_raw.yaml', 'r') as myfile:
        s3pod = myfile.read()

    s3pod = str(s3pod).replace("ENDPOINT_PH",configs["tests_catalog"]["s3_test"]["endpoint"])

    s3pod = s3pod.replace("ACCESS_PH",configs["credentials"]["key"])
    s3pod = s3pod.replace("SECRET_PH",configs["credentials"]["secret"])

    with open("s3/s3pod.yaml", "w") as text_file:
        text_file.write(s3pod)

    os.system("kubectl create -f s3/s3pod.yaml")

    #WORKAROUND
    print ("Waiting for s3 results file...")
    while os.path.exists("../results/"+res_dir+"/s3_test.json") == False:
        subprocess.call(["kubectl","cp","s3pod:/home/s3_test.json","../results/"+res_dir+"/s3_test.json"], stdout=FNULL, stderr=subprocess.STDOUT)
    print ("s3 results file fetched!")

    #cleanup
    print ("Cluster cleanup...")
    os.system("kubectl delete pod s3pod")


if(configs["tests_catalog"]["ml_test"]["run"]==True):
    print ("")
    print ("=========================================================")
    print ("")
    print ("                        ML TEST ")
    print ("")
    print ("=========================================================")

    #########################################################################################
    #WORKAROUND TO DEAL WITH KEYS PRIVACY (use only until on-site s3 public bucket creation)
    #########################################################################################
    with open('ml/s3cfg-secret_raw.yaml', 'r') as myfile:
        secret_raw = myfile.read()
    secret_raw=str(secret_raw)
    with open('ml/s3cfg_raw', 'r') as myfile:
        s3cfg_raw = myfile.read()
    s3cfg=str(s3cfg_raw).replace("ACCESS_PH",configs["credentials"]["key"])
    s3cfg=s3cfg.replace("SECRET_PH",configs["credentials"]["secret"])
    with open("ml/s3cfg", "w") as text_file:
        text_file.write(s3cfg)
    os.system("echo $(cat ml/s3cfg | base64) > ml/base64")
    with open('ml/base64', 'r') as myfile:
        base64 = myfile.read()
    base64=str(base64).replace(" ","")
    secret = str(secret_raw).replace("BASE64_PH",str(base64))
    with open("ml/s3cfg-secret.yaml", "w") as text_file:
        text_file.write(secret)
    os.system("rm -f ml/base64")
    #########################################################################################
    #########################################################################################

    #1) Install the stuff needed for this test: device plugin yaml file (contains driver too) and ml_stack.sh for kubeflow and mpi

    if only_test==False:
        os.system("kubectl create -f ml/device_plugin.yaml")
        os.system("ssh -o 'StrictHostKeyChecking no' root@"+master_ip+" > /dev/null < ml/ml_stack.sh")

    #2) Deploy the required files (s3cfg-secret.yaml must be managed beforehand): sv's s3 on-site public bucket will be used
    os.system("kubectl create -f ml/s3cfg-secret.yaml")
    os.system("kubectl create -f ml/3dgan-datafile-lists-configmap.yaml")

    #number of replicas = number of slaves + 1
    with open('ml/train-mpi_3dGAN_raw.yaml', 'r') as inputfile:
        train = inputfile.read()
    train = str(train).replace("REP_PH",str(configs["general"]["slaves_amount"]+1))
    with open("ml/train-mpi_3dGAN.yaml", "w") as outfile:
        outfile.write(train)
    os.system("kubectl create -f ml/train-mpi_3dGAN.yaml")

    print ("Waiting for ML results file...")
    #WORKAROUND
    #while os.path.exists("../results/"+res_dir+"/bb_train_history.json") == False:
    while True:
        subprocess.call(["kubectl","cp","train-mpijob-worker-0:/mpi_learn/bb_train_history.json","../results/"+res_dir+"/bb_train_history.json"], stdout=FNULL, stderr=subprocess.STDOUT)
        if os.path.exists("../results/"+res_dir+"/bb_train_history.json") == True:
            break
    print ("ML results file fetched!")

    #cleanup
    print ("Cluster cleanup...")
    os.system("kubectl delete mpijob train-mpijob")
    os.system("kubectl delete secret s3cfg")
    os.system("kubectl delete configmap 3dgan-datafile-lists")


#if(configs["tests_catalog"]["docker_bench"]["run"]==True):
#    print ("")
#    print ("=========================================================")
#    print ("")
#    print ("                CERN DOCKER BENCHMARKING TEST ")
#    print ("")
#    print ("=========================================================")
#
#    os.system("export BMK_LOGDIR="+res_dir) #set the dir for the results
#    os.system("ssh -o 'StrictHostKeyChecking no' root@"+master_ip+" > /dev/null < containerBench/cern_bench_test.sh")
#
#    #cleanup
#    print ("Cluster cleanup...")


#if(configs["tests_catalog"]["perfsonar_test"]["run"]==True):
#    print ("")
#    print ("=========================================================")
#    print ("")
#    print ("                    PERFSONAR TEST ")
#    print ("")
#    print ("=========================================================")
#
#    pullImg_cmd = "docker pull perfsonar/testpoint"
#    runCont_cmd = "docker run --name perfsonar-cont --privileged -d -P --net=host -v \"/var/run\" perfsonar/testpoint"
#    runTests_cmd = "docker exec -i perfsonar-cont bash < perfsonar/ps_tests.sh"
#    os.system(pullImg_cmd+" && "+runCont_cmd+" && "+runTests_cmd)
#
#    os.system("docker cp perfsonar-cont:/file/path/within/container ../results/"+res_dir+"/perfsonar.json")
#
#    #cleanup
#    print ("Cluster cleanup...")
#    os.system("docker rm -f perfsonar-cont")
#    os.system("docker rmi -f perfsonar/testpoint")


#---------------------SHOW/MANAGE RESULTS---------------------------------------
#Push at this point all the .json results files to the sci shared (on-site) s3 bucket


print ("")
print ("#########################################################")
print ("#                                                       #")
print ("#        TESTING COMPLETED: results at /results         #")
print ("#                                                       #")
print ("#########################################################")
