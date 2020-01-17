FROM ubuntu:18.04

RUN apt-get update -y && apt-get install -y wget unzip libopenmpi-dev libmumps-dev \
libmumps-seq-dev libmumps-ptscotch-dev libmumps-scotch-dev libscotch-dev libmetis-dev liblapack-dev libscalapack-mpi-dev build-essential gfortran

#COPY makefile_mod fdmnes/prog/makefile
COPY script.sh script.sh

CMD [ "/bin/bash", "script.sh" ]
