#!/bin/bash

# To run on master node

installKubeflow(){
  # SOURCE: https://www.kubeflow.org/docs/started/k8s/kfctl-k8s-istio/

  # 1) Download the kfctl v1.0.2 release
  wget https://github.com/kubeflow/kfctl/releases/download/v1.0.2/kfctl_v1.0.2-0-ga476281_linux.tar.gz

  # 2) Unpack the tar ball
  tar -xvf kfctl_v1.0.2-0-ga476281_linux.tar.gz

  # 3) Create environment variables to make the deployment process easier
  # export PATH=$PATH:"/root/kfctl" # useless
  cp kfctl /bin/ # worked

  export KF_NAME=KFDN
  export BASE_DIR=/opt/
  export KF_DIR=${BASE_DIR}/${KF_NAME}
  export CONFIG_URI="https://raw.githubusercontent.com/kubeflow/manifests/v1.0-branch/kfdef/kfctl_k8s_istio.v1.0.2.yaml"

  # 4) Set up and deploy Kubeflow
  mkdir -p ${KF_DIR}
  cd ${KF_DIR}
  kfctl apply -V -f ${CONFIG_URI} # TODO: this failed with 500 and periodical retries, fixed it with: https://github.com/kubeflow/kubeflow/issues/4762

  # 5) Check the resources deployed in namespace kubeflow
  kubectl -n kubeflow get all
}

deployMPIOperator(){
  # source https://github.com/kubeflow/mpi-operator
  git clone https://github.com/kubeflow/mpi-operator
  cd mpi-operator
  kubectl create -f deploy/v1alpha2/mpi-operator.yaml
}

installKubeflow
deployMPIOperator
