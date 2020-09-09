#!/bin/bash

installNvidiaDocker(){
	distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
	curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
	curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | tee /etc/apt/sources.list.d/nvidia-docker.list
	apt-get update && apt-get install -y nvidia-docker2
	#systemctl restart docker
}

updateDockerDaemon(){
  cp /etc/docker/daemon.json /etc/docker/original_daemon
  cat <<EOF > /etc/docker/daemon.json
{
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "path": "/usr/bin/nvidia-container-runtime",
            "runtimeArgs": []
        }
    }
}
EOF
}

installNvidiaDocker
updateDockerDaemon
systemctl restart docker
