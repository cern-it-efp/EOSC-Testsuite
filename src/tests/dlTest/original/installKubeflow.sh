#!/bin/bash

export KFAPP=kfapp
export CONFIG="https://raw.githubusercontent.com/kubeflow/kubeflow/v0.6.1/bootstrap/config/kfctl_k8s_istio.yaml"

curl -s https://api.github.com/repos/kubeflow/kubeflow/releases/latest |\
    grep browser_download |\
    grep linux |\
    cut -d '"' -f 4 |\
    xargs curl -O -L && \
    tar -zvxf kfctl_*_linux.tar.gz

./kfctl init ${KFAPP} --config=${CONFIG} -V
cd ${KFAPP}
../kfctl generate all -V
../kfctl apply all -V

mkdir /mnt/pv1 /mnt/pv2 /mnt/pv3

# THIS SHOULD DO IT! but the mpi-operator pod keeps failing and restarting and even though the mpijob is deployed, no pods are created and no error is reported!!
yum install git -y
git clone https://github.com/kubeflow/mpi-operator.git
kubectl create -f mpi-operator/deploy/crd/crd-v1alpha1.yaml
kubectl create -f mpi-operator/deploy/ # shouldn't these pods run on the master node?
