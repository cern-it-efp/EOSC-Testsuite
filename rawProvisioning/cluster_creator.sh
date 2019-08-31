#!/bin/bash

# Update this with master and slaves IPs
#################################################################
MASTER_IP=185.19.29.118
IP_ARR=(185.19.29.192 185.19.31.90)
#################################################################

DOCKER_VER=18.06.1.ce
K8S_VER=1.12.3
NVIDIA_VER=392-24

master="false"
uninstall="false"
latest="false"
gpu="false"

while [[ "$1" != "" ]]; do
    case $1 in
        -m )                    master="true"
                                ;;
        -u )                    uninstall="true"
                                ;;
        -l )                    latest="true"
                                ;;
        --gpu )                 gpu="true"
    esac
    shift
done

#Change this, use && instead
if [[ $master = "true" ]]; then
	if [[ -e $HOME/.ssh/id_rsa ]]; then
		echo "Private key found..."
	else
		echo "PRIVATE KEY NOT FOUND!"
		exit 0
	fi
fi

uninstall_stack()
{
  echo ""
	echo "**************************************************************"
	echo "Uninstalling former stack if existing on "$(hostname)
	echo "**************************************************************"
	echo ""
	systemctl stop kubelet
	systemctl stop docker
	ifconfig cni0 down
	ifconfig flannel.1 down
	ifconfig docker0 down
	kubeadm reset -f
	yum remove kubectl kubeadm kubelet -y
	rm -rf /etc/kubernetes
	yum remove docker \
		docker-client \
		docker-client-latest \
		docker-common \
		docker-latest \
		docker-latest-logrotate \
		docker-logrotate \
		docker-selinux \
		docker-engine-selinux \
		docker-engine \
		docker-ce \
		docker-cli \
		docker-ce-cli \
		docker.io -y
	rm -rf /var/lib/docker
	rm -rf /etc/docker
	rm -rf /bin/docker
	rm -rf /bin/dockerd
	rm -rf /usr/bin/docker
	rm -rf /var/lib/cni/
	rm -rf /var/lib/kubelet/*
	rm -rf /etc/cni/
}

install_docker()
{
  echo ""
  echo "*******************************************"
  echo "DOCKER INSTALLATION on "$(hostname)
  echo "*******************************************"
  echo ""

  yum install -y yum-utils device-mapper-persistent-data lvm2
  yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
  yum install -y docker-ce-$DOCKER_VER
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

  systemctl enable kubelet
  systemctl start kubelet

  # Ensure correct traffic routing
  #cat > "/etc/sysctl.d/k8s.conf" << "net.bridge.bridge-nf-call-ip6tables = 1 \n net.bridge.bridge-nf-call-iptables = 1"
  echo "net.bridge.bridge-nf-call-ip6tables = 1" >> /etc/sysctl.d/k8s.conf
  echo "net.bridge.bridge-nf-call-iptables = 1" >> /etc/sysctl.d/k8s.conf
  sysctl --system

}

gpu_components()
{
  echo ""
	echo "***********************************************"
	echo "NVIDIA COMPONENTS INSTALLATION on "$(hostname)
	echo "***********************************************"
	echo ""

	./gpu/nvidia_docker_installer.sh
	./gpu/cuda_install_cc7_392-24.sh
}

init_and_join()
{
  echo "This is the master node! init cluster..."

        systemctl stop firewalld

	echo "Issue init command..."
	kubeadm init --apiserver-advertise-address=$MASTER_IP --pod-network-cidr=10.244.0.0/16 --ignore-preflight-errors=SystemVerification

        mkdir -p $HOME/.kube
        rm $HOME/.kube/config -f
        sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
        sudo chown $(id -u):$(id -g) $HOME/.kube/config

        kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml

	JOIN_COMMAND=$(kubeadm token create --print-join-command)" --ignore-preflight-errors=SystemVerification"

	for IP in ${IP_ARR[*]};
	do
		scp -o "StrictHostKeyChecking no" $(pwd)/cluster_creator.sh root@$IP:
		if [[ $gpu = "true" ]]; then
			scp -o "StrictHostKeyChecking no" $(pwd)/gpu/cuda_install_cc7_392-24.sh root@$IP:
                        scp -o "StrictHostKeyChecking no" $(pwd)/gpu/nvidia_docker_installer.sh root@$IP:
			ssh -o "StrictHostKeyChecking no" root@$IP "hostname ; systemctl stop firewalld ; mkdir gpu ; mv cuda_install_cc7_392-24.sh gpu/ ; mv nvidia_docker_installer.sh gpu/ ; ./cluster_creator.sh -u -w --gpu ; $JOIN_COMMAND" &
		else
	          	ssh -o "StrictHostKeyChecking no" root@$IP "hostname ; systemctl stop firewalld ; ./cluster_creator.sh -u ; $JOIN_COMMAND" &
		fi
	done

	if [[ $gpu = "true" ]]; then
		kubectl create -f gpu/device_plugin.yaml
	fi

	while "true"; do kubectl get nodes; sleep .3; done
}

if [[ $uninstall = "true" ]]; then
  uninstall_stack
fi
install_docker
install_kubernetes
if [[ $gpu = "true" ]]; then
  gpu_components
fi
if  [[ $master = "true" ]]; then
  init_and_join
fi
