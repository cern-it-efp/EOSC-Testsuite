# This is for VMs w/o nvidia drivers

cuda101deb(){
  # ubuntu cuda 10.1 # tensorflow's official docs (https://www.tensorflow.org/install/gpu) specify cuda 10.0 has to be installed
  wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-ubuntu1804.pin
  sudo mv cuda-ubuntu1804.pin /etc/apt/preferences.d/cuda-repository-pin-600
  wget http://developer.download.nvidia.com/compute/cuda/10.1/Prod/local_installers/cuda-repo-ubuntu1804-10-1-local-10.1.243-418.87.00_1.0-1_amd64.deb
  sudo dpkg -i cuda-repo-ubuntu1804-10-1-local-10.1.243-418.87.00_1.0-1_amd64.deb
  sudo apt-key add /var/cuda-repo-10-1-local-10.1.243-418.87.00/7fa2af80.pub
  sudo apt-get update
  sudo apt-get -y install cuda
}

cuda102deb(){
  wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-ubuntu1804.pin
  sudo mv cuda-ubuntu1804.pin /etc/apt/preferences.d/cuda-repository-pin-600
  wget http://developer.download.nvidia.com/compute/cuda/10.2/Prod/local_installers/cuda-repo-ubuntu1804-10-2-local-10.2.89-440.33.01_1.0-1_amd64.deb
  sudo dpkg -i cuda-repo-ubuntu1804-10-2-local-10.2.89-440.33.01_1.0-1_amd64.deb
  sudo apt-key add /var/cuda-repo-10-2-local-10.2.89-440.33.01/7fa2af80.pub
  sudo apt-get update
  sudo apt-get -y install cuda
}

cuda11deb(){
  wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1804/x86_64/cuda-ubuntu1804.pin
  sudo mv cuda-ubuntu1804.pin /etc/apt/preferences.d/cuda-repository-pin-600
  wget http://developer.download.nvidia.com/compute/cuda/11.0.2/local_installers/cuda-repo-ubuntu1804-11-0-local_11.0.2-450.51.05-1_amd64.deb
  sudo dpkg -i cuda-repo-ubuntu1804-11-0-local_11.0.2-450.51.05-1_amd64.deb
  sudo apt-key add /var/cuda-repo-ubuntu1804-11-0-local/7fa2af80.pub
  sudo apt-get update
  sudo apt-get -y install cuda
}

sudo apt-get update -y

sudo apt-get install -y \
      apt-transport-https \
      ca-certificates \
      curl \
      gnupg-agent \
      software-properties-common

# Initial update
apt update -y

# remove existing stuff
apt remove nvidia-driver-latest-dkms cuda cuda-drivers nvidia-container-toolkit -y

# kernel
sudo apt-get install linux-headers-$(uname -r) -y

# gcc
apt install -y gcc

#CUDA TOOLKIT
cuda101deb
cuda102deb
#cuda11deb
sudo apt -y install cuda-drivers

bash nvidia_docker.sh

echo "REBOOT NEEDED?"
echo ""
echo "deploy https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.6.0/nvidia-device-plugin.yml"
echo "install kubeflow"
echo "deploy MPI Operator"
echo "deploy https://raw.githubusercontent.com/kubeflow/mpi-operator/master/examples/v1alpha2/tensorflow-benchmarks.yaml to check MPI Operator deployment"
