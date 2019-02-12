FROM ubuntu:18.04

RUN apt-get update -y && apt-get install -y awscli

COPY s3test.sh s3test.sh

CMD [ "/bin/bash", "s3test.sh" ]
