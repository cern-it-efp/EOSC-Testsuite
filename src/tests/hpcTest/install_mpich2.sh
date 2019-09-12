#!/bin/bash

wget http://www.mpich.org/static/downloads/3.3/mpich-3.3.tar.gz

tar -xzf mpich-3.3.tar.gz

cd mpich-3.3

yum install -y gcc gcc-gfortran gcc-c++

./configure

make

make install

mpiexec --version
