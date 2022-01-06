#!/bin/bash

installNvidiaDocker(){
	distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
	curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | apt-key add -
	curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | tee /etc/apt/sources.list.d/nvidia-docker.list
	rm -f /etc/docker/daemon.json
	apt-get update && apt-get install nvidia-docker2 -y
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

set -x
installNvidiaDocker
updateDockerDaemon
systemctl restart docker
