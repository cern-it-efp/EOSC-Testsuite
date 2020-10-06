#!/bin/bash

tf1_venv(){
  virtualenv --system-site-packages -p python3 /usr/local/ai_stack/tensorflow1.15.2
  source /usr/local/ai_stack/tensorflow1.15.2/bin/activate
}

add_venv_to_bashrc(){
  echo "virtualenv --system-site-packages -p python3 /usr/local/ai_stack/tensorflow1.15.2" >> ~/.bashrc
  echo "source /usr/local/ai_stack/tensorflow1.15.2/bin/activate" >> ~/.bashrc
}

progressive_growing_of_gans(){
  git clone https://github.com/tkarras/progressive_growing_of_gans
  mv progressive_growing_of_gans ~

  # Add PYTHONPATH to bashrc
  cp ~/.bashrc ~/.bashrc.bu ; echo export PYTHONPATH=/root/progressive_growing_of_gans >> ~/.bashrc

  #env:
  export PYTHONPATH=/root/progressive_growing_of_gans

  #Install requirements with pip
  pip install -r ~/progressive_growing_of_gans/requirements-pip.txt # TODO: skip tensorflow installation as OTC images have it already
}

example(){
  wget https://s3.cern.ch/swift/v1/engan/import_example.py
  wget https://s3.cern.ch/swift/v1/engan/karras2018iclr-celebahq-1024x1024.pkl
  python import_example.py
}

installJupyterAndDependencies(){
  pip3 install setuptools ; pip3 install notebook
  pip3 install torch
  pip3 install sklearn
  pip3 install git+https://github.com/fastai/fastai1.git # installs fastai v1. Has to be run outside the virtual environment
}

runJupyter(){
  # deal with virtual environment. This has to be run inside the virtual environment
  python -m ipykernel install --user --name=tensorflow1.15.2

  # Run jupyter notebook # to kill it https://github.com/jupyter/notebook/issues/2844
  nohup jupyter-notebook --allow-root --no-browser > /root/jupyterLogs 2>&1 &

  # Wait for the notebook to be ready...
  sleep 10

  # Get the notebook endpoint
  jupyter-notebook list
}

allowTcpFwd(){ # To avoid error: channel 3: open failed: administratively prohibited: open failed
  sed -i 's/AllowTcpForwarding no/AllowTcpForwarding yes/' /etc/ssh/sshd_config
  service ssh restart
}

jupyterInfo(){
  # if the run was successful and the notebook was properly started:
  echo -----------------------------------------------------------------------------------
  echo "jupyter notebook launched (logs on the VM at /root/jupyterLogs)"
  echo "To be able to access the Jupyter notebook on your machine run:"
  echo "ssh -i PATH_TO_SSHKEY -N -f -L 8888:localhost:8888 USER@IP"
  #echo "ssh -i $sshKey -N -f -L 8888:localhost:8888 $user@$ip"
  echo -----------------------------------------------------------------------------------
}

progressive_growing_of_gans
installJupyterAndDependencies

tf1_venv
add_venv_to_bashrc
#example

runJupyter
allowTcpFwd
jupyterInfo
