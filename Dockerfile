FROM ubuntu:18.04

# ------------------ General Stuff ----------------------------------------------------------
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install curl wget python awscli python-pip python3-pip nano python2.7 zip unzip git snapd net-tools -y
RUN pip3 install pyyaml kubernetes jsonschema
RUN pip3 install --upgrade requests

# ------------------ Install terraform ------------------------------------------------------
RUN wget https://releases.hashicorp.com/terraform/0.12.5/terraform_0.12.5_linux_amd64.zip
RUN unzip terraform_0.12.5_linux_amd64.zip
RUN mv terraform /bin

# ------------------ Install kubectl ------------------------------------------------------
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /bin

# ------------------ Create ssh key file ----------------------------------------------------
RUN mkdir ~/.ssh
RUN touch ~/.ssh/id_rsa
RUN chmod 600 ~/.ssh/id_rsa

# ------------------ Clone TS repo ----------------------------------------------------------
RUN git clone https://github.com/cern-it-efp/OCRE-Testsuite.git

RUN echo "alias clonepr='git clone https://gitlab.cern.ch/ipeluaga/test-suite-private.git && cd test-suite-private'" >> ~/.bashrc
RUN . ~/.bashrc

WORKDIR OCRE-Testsuite
