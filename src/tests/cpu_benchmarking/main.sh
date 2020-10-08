#!/bin/bash

#################################### https://gitlab.cern.ch/hep-benchmarks/hep-benchmark-suite/blob/master/examples/docker/run_all_benchmarks_example.sh

DOCKSOCK=/var/run/docker.sock

sudo docker run -it --rm \
              --privileged \
              --net=host \
              -v $DOCKSOCK:$DOCKSOCK \
              gitlab-registry.cern.ch/hep-benchmarks/hep-benchmark-suite/hep-benchmark-suite-cc7:latest bash

####################################

hep-benchmark-suite \
        -o \
        -d \
        --benchmarks="hepscore,kv,DB12,hyper-benchmark" \
        --freetext="Run as part of the Cloud Provider Validation Test-Suite CERN" \
        --cloud="foobar"
#--hs06_path=/tmp  \
#--hs06_url=/tmp \
#--spec2017_path=/tmp \
#--spec2017_url=/tmp \

# hs06_32, hs06_64 and spec2017: paid license, unable to deploy
