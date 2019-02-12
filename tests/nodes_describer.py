#!/usr/bin/env python
import time
import os
#from kubernetes import client, config

#config.load_kube_config()

#v1 = client.CoreV1Api()

sleep=1.5
slaves=5

while True:
	print("")
	os.system("kubectl describe node kubenode-master")
	time.sleep(sleep)
	os.system('clear')
	for i in range(1,slaves):
		print("")
		os.system("kubectl describe node kubenode-slave"+str(i))
		time.sleep(sleep)
		os.system('clear')

