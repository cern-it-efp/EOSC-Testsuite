Example usage:

1. 16 hosts perform calculation in parallel, each taking his own energy value:
  ./mpirun_fdmnes -np 16

2. 20 MPI processes, which fdmnes divides into 5 groups of 4 processes in each. 
  One group calculates one energy value by parallel MUMPS solver with 4 parallel processes:
  HOST_NUM_FOR_MUMPS=4 ./mpirun_fdmnes -np 20

Use commmand
./mpirun_fdmnes -h
for getting help.