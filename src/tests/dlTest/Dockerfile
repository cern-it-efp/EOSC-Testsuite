# OG, mpi 3.0.0
#FROM uber/horovod:0.14.0-tf1.10.0-torch0.4.0-py3.5
#FROM uber/horovod:0.15.2-tf1.12.0-torch1.0.0-py3.5 # same error, mpi 3.1.2
#FROM horovod/horovod:0.20.0-tf2.3.0-torch1.6.0-mxnet1.6.0.post0-py3.7-cuda10.1

# mpi 4.0.0 # same error
FROM horovod/horovod:0.16.4-tf1.12.0-torch1.1.0-mxnet1.4.1-py3.5

RUN apt-get -y update

RUN pip3 install mpi4py psutil gpustat scikit-optimize h5py==2.7.0 && \
    ln -s /usr/bin/python3.5 /usr/bin/python3

RUN apt-get install -y awscli

# NNLO
RUN git clone "https://github.com/cern-it-efp/NNLO.git" "/nnlo"

# MPI_LEARN
RUN git clone "https://github.com/svalleco/mpi_learn.git" "/mpi_learn"
RUN sed -i 's/s3cmd get/aws s3 cp --no-sign-request --endpoint-url=https:\/\/s3.cern.ch/' /mpi_learn/mpi_learn/train/data.py

# sources:
#  https://github.com/kubeflow/mpi-operator/blob/master/examples/tensorflow-benchmarks/Dockerfile#L3-L7 / https://issueexplorer.com/issue/kubeflow/mpi-operator/424#:~:text=Note%20that%20the%20latest%20image%20has%20the%20following%20configuration
#  https://github.com/kubeflow/mpi-operator/blob/master/examples/tensorflow-benchmarks/Dockerfile
# mpi-operator mounts the .ssh folder from a Secret. For that to work, we need
# to disable UserKnownHostsFile to avoid write permissions.
RUN echo "    UserKnownHostsFile /dev/null" >> /etc/ssh/ssh_config

# Disabling StrictModes avoids directory and files read permission checks.
RUN sed -i 's/StrictModes yes/StrictModes no/' /etc/ssh/sshd_config

CMD ["/bin/bash"]
