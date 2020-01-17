#!/bin/bash

docker rmi -f cernefp/s3_test_image
docker build -t cernefp/s3_test_image .
docker push cernefp/s3_test_image
docker images
