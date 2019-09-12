FROM centos:7

RUN yum update -y && yum install -y git python-requests python-yaml

COPY data_repatriation_test.sh data_repatriation_test.sh

CMD [ "/bin/bash", "data_repatriation_test.sh" ]
