FROM ubuntu:18.04

RUN apt-get update -y && apt-get install -y awscli

COPY s3_test.sh s3_test.sh

CMD [ "/bin/bash", "s3_test.sh" ]
