#!/bin/bash

# First run: results/opentelekomcloud/22-09-2020_10-03-42 (10 nodes type p2.4xlarge.8)

pathToTC="/t.yaml"
pathToCFG="/c.yaml"

dlKubeConfig="/EOSC-Testsuite/src/tests/dlTest/config"

maxNodes=$(yq r $pathToTC dlTest.nodes)

echo ""
echo \##################################
echo RUN WITH $maxNodes NODES...
echo \##################################
echo ""
# normal run with the max number of nodes
./test_suite -c $pathToCFG -t $pathToTC --usePrivateIPs &&

# wait til pods are destroyed
#kubectl get pods --kubeconfig $dlKubeConfig | grep -i "No resources found in default namespace"
kubectl get pods --kubeconfig $dlKubeConfig | grep STATUS &> /dev/null
while [ $? == 0 ] ; do
  echo "Former pods are still there, waiting and retrying..."
  sleep 4
  kubectl get pods --kubeconfig $dlKubeConfig | grep STATUS &> /dev/null
done
sleep 4

# reduce by 1 because the first run is already done
for (( var=$(($maxNodes-1)); var>=1; var-- )) do  # Repeat until 1 replica (only master node remaining)

  # On completion, delete and destroy a node that is not the master
  NODE_2_DELETE=$(kubectl get nodes --kubeconfig $dlKubeConfig | grep -v master | awk '{print $1}' | sed -n 2p)
  kubectl --kubeconfig $dlKubeConfig delete node $NODE_2_DELETE
  echo ""; echo Destroy node $NODE_2_DELETE; echo "" ; echo $NODE_2_DELETE >> /tmp/deleteThese

  #cd src/tests/dlTest
  #indexToDestroy=$(terraform show -json)
  #terraform destroy -target=opentelekomcloud_compute_instance_v2.kubenode_defaultNetwork[$indexToDestroy] -auto-approve
  #cd ../../..

  # Edit the testsCatalog.yaml (or create a new one from raw.yaml) to decrease nodes (replica) by 1: use
  yq w -i $pathToTC dlTest.nodes $var

  echo ""
  echo \##################################
  echo RUN WITH $var NODES...
  echo \##################################
  echo ""
  # run with onlyTest
  ./test_suite -c $pathToCFG -t $pathToTC --onlyTest

done
