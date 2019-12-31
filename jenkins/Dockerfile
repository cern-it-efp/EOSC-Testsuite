#This is our custom jenkins-tslauncher image for CERN Openshift

FROM jenkins/jenkins

USER root

#1008220000 (openshift uses different UID per project)
#ARG UID=1005360000

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
    jsonschema
RUN pip3 install --upgrade requests

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

# ------------------ Permissions
RUN chgrp -R 0 /etc && chmod -R g=u /etc
RUN chmod g=u /etc/passwd

#RUN sed -i "s/jenkins:x:1000:1000/jenkins:x:$UID:$UID/" /etc/passwd

RUN chown -R jenkins:jenkins /usr/share/jenkins /etc/passwd

################ AFTER CONTAINER IS RUN ################ (Try to add the random UID to etc/passwd when the container is run)

ENTRYPOINT chown -R $UID:$UID /usr/share/jenkins /etc/passwd ; sed -i "s/jenkins:x:1000:1000/jenkins:x:$UID:$UID/" /etc/passwd
