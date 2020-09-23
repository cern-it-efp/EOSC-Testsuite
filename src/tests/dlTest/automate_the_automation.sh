#!/bin/bash

# First run: results/opentelekomcloud/22-09-2020_10-03-42 (10 nodes type p2.4xlarge.8)

pathToTC="/t.yaml"
pathToCFG="/c.yaml"

dlKubeConfig="/EOSC-Testsuite/src/tests/dlTest/config"

maxNodes=$(yq r $pathToTC dlTest.nodes)

minNodes=1 # Repeat until 1 replica (only master node remaining).

function runHeader(){
  echo ""
  echo \##################################
  echo RUN WITH $1 NODES...
  echo \##################################
  echo ""
}

runHeader $maxNodes

# normal run with the max number of nodes
#./test_suite -c $pathToCFG -t $pathToTC --usePrivateIPs &&
./test_suite -c $pathToCFG -t $pathToTC --onlyTest &&

for (( var=$(($maxNodes-1)); var>=$minNodes; var-- )) do # -1 because the first run is already done

  # wait til pods are destroyed
  #kubectl get pods --kubeconfig $dlKubeConfig | grep -i "No resources found in default namespace"
  kubectl get pods --kubeconfig $dlKubeConfig | grep STATUS &> /dev/null
  while [ $? == 0 ] ; do
    echo "Former pods are still there, waiting and retrying..."
    sleep 4
    kubectl get pods --kubeconfig $dlKubeConfig | grep STATUS &> /dev/null
  done
  sleep 4

  # On completion, delete and destroy a node that is not the master
  NODE_2_DELETE=$(kubectl get nodes --kubeconfig $dlKubeConfig | grep -v master | awk '{print $1}' | sed -n 2p)
  kubectl --kubeconfig $dlKubeConfig delete node $NODE_2_DELETE
  echo ""; echo Destroy node $NODE_2_DELETE; echo "" ; echo $NODE_2_DELETE >> /tmp/deleteThese

  cd src/tests/dlTest
  indexToDestroy=$(python -c """
import json
import os

tfShow = json.loads(os.popen('terraform show -json | jq .values.root_module.resources').read().strip())

for obj in tfShow:

    type = obj['type']
    name = obj['values']['name']

    if type == 'opentelekomcloud_compute_instance_v2' and name == '$NODE_2_DELETE':
      print(obj['index'])
  """)
  terraform destroy -target=opentelekomcloud_compute_instance_v2.kubenode_defaultNetwork[$indexToDestroy] -auto-approve
  cd ../../..

  # Edit the testsCatalog.yaml (or create a new one from raw.yaml) to decrease nodes (replica) by 1: use
  yq w -i $pathToTC dlTest.nodes $var

  runHeader $var
  # run with onlyTest
  ./test_suite -c $pathToCFG -t $pathToTC --onlyTest

done
