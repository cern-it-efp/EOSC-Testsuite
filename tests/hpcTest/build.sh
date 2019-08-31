#!/bin/bash

docker rmi -f ipeluaga/fdmnes
docker build -t ipeluaga/fdmnes .
docker push ipeluaga/fdmnes:latest
docker images
