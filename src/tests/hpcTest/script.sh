#!/bin/bash

wget http://neel.cnrs.fr/IMG/zip/fdmnes_2019_04_15.zip

unzip fdmnes_2019_04_15.zip
mv fdmnes /tmp

cd /tmp/fdmnes/prog

echo "FC = mpif90" > makefile
echo "OPTLVL = 3" >> makefile
echo "EXEC = ../fdmnes" >> makefile
echo "BIBDIR = /usr/lib" >> makefile
echo "INCDIR = /usr/include" >> makefile
echo "FFLAGS = -c  -O\$(OPTLVL) -I\$(INCDIR)" >> makefile
echo "OBJ = main.o clemf0.o coabs.o convolution.o diffraction.o dirac.o fdm.o fdmx.o fprime.o fprime_data.o general.o lecture.o mat.o metric.o minim.o optic.o potential.o selec.o scf.o spgroup.o sphere.o tab_data.o tddft.o tensor.o mat_solve_mumps.o" >> makefile
echo "all: \$(EXEC)" >> makefile
echo "\$(EXEC): \$(OBJ)" >> makefile
echo "	\$(FC) -o \$@ \$^  -L\$(BIBDIR) -ldmumps -lzmumps -lmumps_common -lesmumps -lmetis -lpord -lscotch -lscotcherr -lpthread -llapack -lblas" >> makefile
echo "%.o: %.f90" >> makefile
echo "	\$(FC) -o  \$@ \$(FFLAGS) \$?" >> makefile
echo "clean:" >> makefile
echo "	rm -f *.o \$(EXEC)" >> makefile
echo "	rm -f *.mod" >> makefile

make

#the file to harvest is (from /fdmnes): Sim/Test_stand/Cu_bav.txt
