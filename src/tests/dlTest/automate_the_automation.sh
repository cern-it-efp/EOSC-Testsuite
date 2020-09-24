#!/bin/bash

# TODO: at the end of the loop, when nodes == 1 it does not destroy the remaining VM

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

function deleteOneNode(){
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
}

runHeader $maxNodes

# normal run with the max number of nodes # TODO: check whether a cluster for dlTest exists and in that case use onlyTest instead of usePrivateIPs
#./test_suite -c $pathToCFG -t $pathToTC --usePrivateIPs
./test_suite -c $pathToCFG -t $pathToTC --onlyTest

if [[ $? != 0 ]] ; then # TODO: useless bc test_suite's exit code doesnt fully reflect the exit status of the run
  exit 1
fi

for (( var=$(($maxNodes-1)); var>=$minNodes; var-- )) do # -1 because the first run is already done

  # On completion, delete and destroy a node that is not the master
  deleteOneNode

  # Edit the testsCatalog.yaml (or create a new one from raw.yaml) to decrease nodes (replica) by 1:
  yq w -i $pathToTC dlTest.nodes $var

  # wait til pods are destroyed (in case there is still any...)
  kubectl get pods --kubeconfig $dlKubeConfig | grep STATUS &> /dev/null
  while [ $? == 0 ] ; do
    echo "Former pods are still there, waiting and retrying..."
    sleep 4
    kubectl get pods --kubeconfig $dlKubeConfig | grep STATUS &> /dev/null
  done
  sleep 4

  # run with onlyTest
  runHeader $var
  ./test_suite -c $pathToCFG -t $pathToTC --onlyTest

done

# Delete the remaining node
deleteOneNode # TODO: would fail bc the function only deletes no-master nodes but the last one is the master
