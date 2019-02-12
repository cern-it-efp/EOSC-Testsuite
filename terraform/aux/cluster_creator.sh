#!/bin/bash

DOCKER_VER=18.06.1.ce
K8S_VER=1.12.3
NVIDIA_VER=392-24

master="false"
latest="false"

while [[ "$1" != "" ]]; do
    case $1 in
        -m )                    master="true"
                                ;;
        -l )                    latest="true"
    esac
    shift
done

install_docker()
{
  echo ""
  echo "*******************************************"
  echo "DOCKER INSTALLATION on "$(hostname)
  echo "*******************************************"
  echo ""

  yum install -y yum-utils device-mapper-persistent-data lvm2
  yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

  if  [[ $latest = "true" ]]; then
  	echo "Last version of Docker will be installed"
    yum install -y docker-ce
  else
  	echo "Docker version $DOCKER_VER will be installed"
  	yum install -y docker-ce-$DOCKER_VER
  fi


  mkdir "/etc/docker"
  #cat > "/etc/docker/daemon.json" << "{\"exec-opts\": [\"native.cgroupdriver=systemd\"],\"log-driver\": \"json-file\",\"log-opts\": {\"max-size\": \"100m\"},\"storage-driver\": \"overlay2\",\"storage-opts\": [\"overlay2.override_kernel_check=true\"]}"
  echo "{\"exec-opts\": [\"native.cgroupdriver=systemd\"],\"log-driver\": \"json-file\",\"log-opts\": {\"max-size\": \"100m\"},\"storage-driver\": \"overlay2\",\"storage-opts\": [\"overlay2.override_kernel_check=true\"]}" > /etc/docker/daemon.json
  mkdir -p "/etc/systemd/system/docker.service.d"

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

  #cat > "/etc/yum.repos.d/kubernetes.repo" << "[kubernetes] \n name=Kubernetes \n baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64 \n enabled=1 \n gpgcheck=1 \n repo_gpgcheck=1 \n gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg \n exclude=kube* \n "
  #echo "[kubernetes] \n name=Kubernetes \n baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64 \n enabled=1 \n gpgcheck=1 \n repo_gpgcheck=1 \n gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg \n exclude=kube* \n " > /etc/yum.repos.d/kubernetes.repo

  echo "[kubernetes]" >> /etc/yum.repos.d/kubernetes.repo
  echo "name=Kubernetes" >> /etc/yum.repos.d/kubernetes.repo
  echo "baseurl=https://packages.cloud.google.com/yum/repos/kubernetes-el7-x86_64" >> /etc/yum.repos.d/kubernetes.repo
  echo "enabled=1" >> /etc/yum.repos.d/kubernetes.repo
  echo "gpgcheck=1" >> /etc/yum.repos.d/kubernetes.repo
  echo "repo_gpgcheck=1" >> /etc/yum.repos.d/kubernetes.repo
  echo "gpgkey=https://packages.cloud.google.com/yum/doc/yum-key.gpg https://packages.cloud.google.com/yum/doc/rpm-package-key.gpg" >> /etc/yum.repos.d/kubernetes.repo
  echo "exclude=kube*" >> /etc/yum.repos.d/kubernetes.repo

  # Set SELinux in permissive mode (effectively disabling it)
  setenforce 0
  sed -i 's/^SELINUX=enforcing$/SELINUX=permissive/' /etc/selinux/config

  if  [[ $latest = "true" ]]; then
  	echo "Last version of Kubernetes will be installed"
          yum install -y kubelet kubeadm kubectl --disableexcludes=kubernetes
  else
  	echo "Kubernetes version $K8S_VER will be installed"
  	yum install -y kubelet-$K8S_VER kubeadm-$K8S_VER kubectl-$K8S_VER --disableexcludes=kubernetes
  fi

  sed -i 's/cgroup-driver=systemd/cgroup-driver=cgroupfs/g' /etc/systemd/system/kubelet.service.d/10-kubeadm.conf

  systemctl enable kubelet
  systemctl start kubelet

  # Ensure correct traffic routing
  #cat > "/etc/sysctl.d/k8s.conf" << "net.bridge.bridge-nf-call-ip6tables = 1 \n net.bridge.bridge-nf-call-iptables = 1"
  echo "net.bridge.bridge-nf-call-ip6tables = 1" >> /etc/sysctl.d/k8s.conf
  echo "net.bridge.bridge-nf-call-iptables = 1" >> /etc/sysctl.d/k8s.conf
  sysctl --system

}

init_cluster()
{
  systemctl stop firewalld

	kubeadm init --apiserver-advertise-address=$(hostname -I | awk '{print $1}') --pod-network-cidr=10.244.0.0/16 --ignore-preflight-errors=SystemVerification

  mkdir -p $HOME/.kube
  rm $HOME/.kube/config -f
  sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
  sudo chown $(id -u):$(id -g) $HOME/.kube/config

  kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml

  kubectl taint nodes --all node-role.kubernetes.io/master- 

}

install_docker
install_kubernetes

if  [[ $master = "true" ]]; then
  init_cluster
fi
