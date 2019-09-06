#!/bin/bash

docker rmi -f ipeluaga/data_repatriation_test_image
docker build -t ipeluaga/data_repatriation_test_image .
docker push ipeluaga/data_repatriation_test_image
docker images
