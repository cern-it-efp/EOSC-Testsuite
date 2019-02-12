#/bin/bash

docker rmi -f ipeluaga/s3_test_image
docker build -t ipeluaga/s3_test_image .
docker push ipeluaga/s3_test_image
docker images
