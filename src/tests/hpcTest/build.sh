#!/bin/bash

docker rmi -f cernefp/fdmnes
docker build -t cernefp/fdmnes .
docker push cernefp/fdmnes:latest
docker images
