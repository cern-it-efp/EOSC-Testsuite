FROM ubuntu:18.04

# ------------------ Fix UnicodeEncodeError: 'export PYTHONIOENCODING=utf8'
ARG PYTHONIOENCODING=utf8

# ------------------ General Stuff
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y \
    curl \
    wget \
    python \
    awscli \
    python-pip \
    python3-pip \
    nano \
    vim \
    python2.7 \
    zip \
    unzip \
    git \
    snapd \
    net-tools \
    jq
RUN pip3 install \
    pyyaml \
    kubernetes \
    jsonschema \
    ansible
RUN pip3 install --upgrade requests

# ------------------ Install terraform
RUN TERRAFORM_VERSION=$(curl -s https://checkpoint-api.hashicorp.com/v1/check/terraform | jq -r .current_version) && \
    wget https://releases.hashicorp.com/terraform/$TERRAFORM_VERSION/terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    mv terraform /bin

# ------------------ Install ansible
RUN apt-get install -y software-properties-common; \
    apt-add-repository --yes --update ppa:ansible/ansible; \
    apt-get install -y ansible

# ------------------ Install kubectl
RUN KUBECTL_VERSION=$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt) && \
    curl -LO https://storage.googleapis.com/kubernetes-release/release/$KUBECTL_VERSION/bin/linux/amd64/kubectl && \
    chmod +x ./kubectl && \
    mv ./kubectl /bin

# ------------------ Install az CLI
RUN curl -sL https://aka.ms/InstallAzureCLIDeb | bash

# ------------------ Create ssh key file
RUN mkdir /root/.ssh && \
    touch /root/.ssh/id_rsa && \
    chmod 600 /root/.ssh/id_rsa

# ------------------ Clone TS repo and get bash
ENTRYPOINT git clone -q https://github.com/cern-it-efp/OCRE-Testsuite.git && \
           cd OCRE-Testsuite  && \
           bash
