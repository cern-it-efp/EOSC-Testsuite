# The original is https://github.com/svalleco/NNLO/blob/master/Dockerfile
# This custom image installs aws' CLI instead of s3cmd and modifies the code to use the public bucket at CERN S3

FROM uber/horovod:0.14.0-tf1.10.0-torch0.4.0-py3.5

RUN apt-get -y update
RUN apt-get install -y awscli

RUN pip3 install mpi4py psutil gpustat scikit-optimize h5py==2.7.0
    #&& ln -s /usr/bin/python3.5 /usr/bin/python3

RUN git clone "https://github.com/svalleco/NNLO.git" "/nnlo"

# Noter for this TrainingDriver.py's '--copy-command' can be used instead
RUN sed -i "s/,'cp /,'aws s3 cp --no-sign-request --endpoint-url=https:\/\/s3.cern.ch s3:\/\/gan-bucket\//" /nnlo/nnlo/train/data.py

WORKDIR "/nnlo"
