#while true; do
  if kubectl get pods | grep "ImageInspectError"; then
    conflictPod=$(kubectl get pods | grep "ImageInspectError" | awk '{print $1}')

    conflictNode=$(kubectl get pods -o wide | grep "ImageInspectError" | awk '{print $7}')

    conflictNode_ip=$(kubectl describe node $conflictNode | grep InternalIP: | awk '{print $2}')

    ssh -o 'StrictHostKeyChecking no' root@$conflictNode_ip "docker rmi -f gitlab-registry.cern.ch/cloud-infrastructure/gpu-mpi-containers/mpi_learn" &> /dev/null

    kubectl delete pods --all
  fi
#done
