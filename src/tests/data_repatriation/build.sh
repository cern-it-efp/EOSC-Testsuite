#!/bin/bash

docker rmi -f cernefp/data_repatriation_test_image
docker build -t cernefp/data_repatriation_test_image .
docker push cernefp/data_repatriation_test_image
docker images
