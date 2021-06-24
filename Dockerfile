FROM ubuntu:18.04

# ------------------ Fix UnicodeEncodeError:
#ARG PYTHONIOENCODING=utf8
#ARG LC_ALL=C.UTF-8
ENV PYTHONIOENCODING utf8
ENV LC_ALL C.UTF-8

# ------------------ General Stuff
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update -y
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
    jq \
    iputils-ping

RUN pip3 install --upgrade\
    requests \
    pyyaml \
    kubernetes \
    jsonschema \
    boto3 \
    ansible

# ------------------ Install yq
RUN wget https://github.com/mikefarah/yq/releases/download/3.4.0/yq_linux_amd64 -O /usr/bin/yq && \
    chmod +x /usr/bin/yq

# ------------------ Install terraform
RUN TERRAFORM_VERSION=$(curl -s https://checkpoint-api.hashicorp.com/v1/check/terraform | jq -r .current_version) && \
    wget https://releases.hashicorp.com/terraform/$TERRAFORM_VERSION/terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip && \
    mv terraform /bin

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

# ------------------ Add useful aliases
RUN echo 'alias tfLogs="tail -f /EOSC-Testsuite/logs"' >> ~/.bashrc
RUN echo 'alias ansibleLogs="tail -f /EOSC-Testsuite/src/logging/ansibleLogs*"' >> ~/.bashrc
RUN echo 'alias gcd="git checkout development"' >> ~/.bashrc
RUN echo 'alias watchPods="watch kubectl get pods --kubeconfig /EOSC-Testsuite/src/tests/shared/config -owide"' >> ~/.bashrc

# ------------------ Clone TS repo and get bash
RUN echo cd /EOSC-Testsuite >> ~/.bashrc
ENTRYPOINT echo 'Cloning EOSC-Testsuite repository...' && \
           git clone -q https://github.com/cern-it-efp/EOSC-Testsuite.git && \
           cd EOSC-Testsuite ; bash

# ENTRYPOINT is not overriden by the cmd used in 'docker run': for that --entrypoint="" needs to be used to reset it
