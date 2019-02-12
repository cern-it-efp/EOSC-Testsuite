#!/bin/bash

install_ml()
{
  export SOURCE=$PWD

  wget https://dl.google.com/go/go1.11.4.linux-amd64.tar.gz
  tar -xvf go1.11.4.linux-amd64.tar.gz
  rm -f go1.11.4.linux-amd64.tar.gz
  export GOROOT=$PWD/go
  export GOPATH=$HOME/Projects/Proj1
  export PATH=$GOPATH/bin:$GOROOT/bin:$PATH

  yum install -y git #needed for the following cmd
  go get github.com/ksonnet/ksonnet
  cd $GOPATH/src/github.com/ksonnet/ksonnet
  make install

  export KUBEFLOW_SRC=$SOURCE"/KUBEFLOW_SRC"
  export KFAPP=KFAPP
  export KUBEFLOW_TAG=v0.3.5
  mkdir ${KUBEFLOW_SRC}
  cd ${KUBEFLOW_SRC}
  curl https://raw.githubusercontent.com/kubeflow/kubeflow/${KUBEFLOW_TAG}/scripts/download.sh | bash
  ${KUBEFLOW_SRC}/scripts/kfctl.sh init ${KFAPP} --platform none
  cd ${KFAPP}
  ${KUBEFLOW_SRC}/scripts/kfctl.sh generate k8s
  ${KUBEFLOW_SRC}/scripts/kfctl.sh apply k8s

  cd ks_app
  ks generate mpi-operator mpi-operator --gpusPerNode=1
  ks apply default -c mpi-operator
}

echo "Installing machine learning and MPI components..."
install_ml &> /dev/null &&
echo "Cluster ready for ML!"
