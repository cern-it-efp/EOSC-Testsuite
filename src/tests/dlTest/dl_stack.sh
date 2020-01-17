#!/bin/bash

install_dl()
{
  export SOURCE=$PWD

  yum install -y wget git #needed for following cmd's. 

  wget https://dl.google.com/go/go1.11.4.linux-amd64.tar.gz
  tar -xvf go1.11.4.linux-amd64.tar.gz
  rm -f go1.11.4.linux-amd64.tar.gz
  export GOROOT=$PWD/go
  export GOPATH=$HOME/Projects/Proj1
  export PATH=$GOPATH/bin:$GOROOT/bin:$PATH

  go get github.com/ksonnet/ksonnet
  cd $GOPATH/src/github.com/ksonnet/ksonnet
  make install

  export KUBEFLOW_SRC=$SOURCE"/KUBEFLOW_SRC"
  export KFAPP=KFAPP
  export KUBEFLOW_TAG=v0.5.1 # 0.4.1
  mkdir ${KUBEFLOW_SRC}
  cd ${KUBEFLOW_SRC}
  curl https://raw.githubusercontent.com/kubeflow/kubeflow/${KUBEFLOW_TAG}/scripts/download.sh | bash
  mkdir /mnt/pv1
  mkdir /mnt/pv2
  mkdir /mnt/pv3
  ${KUBEFLOW_SRC}/scripts/kfctl.sh init ${KFAPP} --platform none
  cd ${KFAPP}
  ${KUBEFLOW_SRC}/scripts/kfctl.sh generate k8s
  ${KUBEFLOW_SRC}/scripts/kfctl.sh apply k8s

  cd ks_app
  ks generate mpi-operator mpi-operator --gpusPerNode=1 || exit 1
  ks apply default -c mpi-operator || exit 1
}

install_dl || exit 1
