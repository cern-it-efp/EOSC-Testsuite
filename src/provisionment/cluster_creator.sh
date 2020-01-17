#!/bin/bash

master="false"

while [[ "$1" != "" ]]; do
  case $1 in
    -m )                    master="true"
      ;;
  esac
  shift
done

latest_docker()
{
  echo "Last version of Docker will be installed"
  yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
  yum install -y docker-ce
}

latest_k8s()
{
  echo "Latest version of Kubernetes will be installed"
  yum install -y kubelet kubeadm kubectl --disableexcludes=kubernetes
}

install_docker()
{
  echo ""
  echo "*******************************************"
  echo "DOCKER INSTALLATION on "$(hostname)
  echo "*******************************************"
  echo ""

  yum install -y yum-utils device-mapper-persistent-data lvm2

  if  [[ $DOCKER_CE_VER != "" ]]; then
    echo "Docker $DOCKER_CE_VER will be installed"
    rpm --import "https://sks-keyservers.net/pks/lookup?op=get&search=0xee6d536cf7dc86e2d7d56f59a178ac6c6238f52e"
    yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
    yum install -y $DOCKER_CE_VER || latest_docker || exit 1 #exits if installation problems exits

  elif [[ $DOCKER_EN_VER != "" ]]; then
    echo "Docker $DOCKER_EN_VER will be installed"
    rpm --import "https://sks-keyservers.net/pks/lookup?op=get&search=0xee6d536cf7dc86e2d7d56f59a178ac6c6238f52e"
    yum-config-manager --add-repo https://packages.docker.com/1.13/yum/repo/main/centos/7
    yum install -y $DOCKER_EN_VER || latest_docker || exit 1 #exits if installation problems exits

  else
    latest_docker || exit 1 #exits if installation problems exists
  fi

  mkdir "/etc/docker"
  cat > "/etc/docker/daemon.json" <<EOF
{
  "exec-opts": [
    "native.cgroupdriver=systemd"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m"
  },
  "storage-driver": "overlay2",
  "storage-opts": [
    "overlay2.override_kernel_check=true"
  ]
}
EOF

  systemctl enable docker
  systemctl daemon-reload
  systemctl start docker
}

install_kubernetes()
{
  echo ""
  echo "***********************************************"
  echo "KUBERNETES INSTALLATION on "$(hostname)
  echo "***********************************************"
  echo ""

  cat <<EOF > /etc/yum.repos.d/kubernetes.repo
[kubernetes]
name=Kubernetes
baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64
enabled=1
gpgcheck=1
repo_gpgcheck=1
gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg
exclude=kube*
EOF

  # Set SELinux in permissive mode (effectively disabling it)
  setenforce 0
  sed -i 's/^SELINUX=enforcing$/SELINUX=permissive/' /etc/selinux/config

  if  [[ $K8S_VER != "" ]]; then
    echo "Kubernetes $K8S_VER will be installed"
    yum install -y kubelet-$K8S_VER kubeadm-$K8S_VER kubectl-$K8S_VER --disableexcludes=kubernetes || latest_k8s || exit 1 #exits if installation problems exists
  else
    latest_k8s || exit 1 #exits if installation problems exists
  fi

  echo "KUBELET_EXTRA_ARGS=\"--image-pull-progress-deadline=30m\"" > /etc/sysconfig/kubelet

  systemctl enable kubelet && systemctl restart kubelet # stop and then start the specified unit. If the units is not running yet, it will be started

  # Ensure correct traffic routing
  cat <<EOF >  /etc/sysctl.d/k8s.conf
  net.bridge.bridge-nf-call-ip6tables = 1
  net.bridge.bridge-nf-call-iptables = 1
EOF
  sysctl --system

  echo 1 > /proc/sys/net/ipv4/ip_forward # fixes gcp cluster init error. Other providers do not need it

}

init_cluster()
{
  systemctl stop firewalld

  #https://github.com/kubeflow/pipelines/issues/741
  kubeadm init --apiserver-advertise-address=$(hostname -I | awk '{print $1}') --pod-network-cidr=10.244.0.0/16 --ignore-preflight-errors=SystemVerification,NumCPU

  mkdir -p $HOME/.kube
  rm $HOME/.kube/config -f
  cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  chown $(id -u):$(id -g) $HOME/.kube/config

  kubectl taint nodes --all node-role.kubernetes.io/master-

  kubectl create -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml

  kubectl config set-context --current --namespace=default # WA to fix namespace issues on jenkins runs

}

systemctl stop firewalld
install_docker
install_kubernetes

if  [[ $master = "true" ]]; then
  init_cluster
fi
