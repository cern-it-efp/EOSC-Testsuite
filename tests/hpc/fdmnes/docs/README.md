                                    FDMNES                            08/10/2018
                                    ======

This file contains information specific to the installation of FDMNES at the
ESRF:

1) general information on FDMNES;
2) the executable to select, and how to run it;
3) the use of a batch processing system to run FDMNES;
4) the input files needed;
5) a list of the files and directories provided.


1) General
----------

The installation contains the FDMNES version of 16/09/2018 with executables for
Windows (32 and 64 bit native and Cygwin/MinGW), Mac OS and LINUX (64 bit).

FDMNES calculates the spectra of different spectroscopies related to the real or
virtual absorption of x-rays in material. It was written by Yves Joly of the
"Institut Neel", CNRS Grenoble.

For more details on the program, see the the file "readme.txt" in the "Doc"
subdirectory, the manuals mentioned in this file and the web page
http://www.neel.cnrs.fr/fdmnes

The native Windows and the Mac OS executables are part of the FDMNES
distribution provided by Yves Joly at the web site mentioned above.

The Windows Cygwin/MinGW executable was compiled at the ESRF using the MinGW
version of the GNU Fortran 90 compiler "gfortran" version 4.8.3 (part of the GNU
Compiler Collection, see www.gnu.org/software/gcc). The compilation was done
under Cygwin version 1.7.33. but as the MinGW compiler was used, it is not
necessary to have Cygwin installed to run the executable.

Since the release 28/07/2015, FDMNES uses the MUMPS libraries, which resulted in
a considerable speedup of the execution. However, these libraries seem at
present not to be available for Cygwin/MinGW, thus the Gaussian solver is used
that is part of the FDMNES code.

The LINUX executable "fdmnes_linux64" is also part of the FDMNES distribution
provided by Yves Joly. It was compiled on a 64-bit computer with the Linux
Fortran 90 compiler "gfortran-mp-6".

The other LINUX versions of the program were compiled at the ESRF on a Debian 8
system using the Fortran 90 compiler "gfortran" version 4.9.2. The parallel
(MPI) versions were compiled with the compiler "mpif90" from OpenMPI version
2.0.2, this implements (most of) the MPI-2.1 functionality.

As OpenMPI version 2.0.2 is not the standard version of OpenMPI for Debian 8,
one has to provide the libraries of OpenMPI version 2.0.2 at runtime.

For questions concerning the FDMNES installation at the ESRF, contact R. Wilcke
(wilcke@esrf.fr, phone 2516).


2) Program Execution
--------------------

This version can use the "Message Passing Interface" (MPI) mechanism of parallel
computing. Therefore, there are two different executables for each computer
architecture where MPI is available: one without and the other with MPI. MPI is
(at present) only available on the NICE-Linux computers ("rnice" and the
high-performance cluster accessible through the resource manager OAR).

The names of the executables are "fdmnes" for the version without MPI and
"fdmnes_mpi" for the version with MPI (where available).

To execute the program, there are three possibilities:

1) on the NICE-Linux computers, add the location of the program to your PATH
   environment variable. The program is in a correspondingly named subdirectory
   of "bin" (see below "Directories and Files", subdirectory "bin");

2) use the script "fdmnes.sh" as an uniform interface to FDMNES. For more
   information, see below "Directories and Files".

3) copy the executable and the input files (see below "Input Files") into a
   directory of your choice and run it from there.

If you want to use one of the Windows native versions of FDMNES on your own
Windows PC, you can only use the third option.

You can also use the third option if you want to use the Cygwin/MinGW version
on your Windows PC. You can then execute FDMNES in the standard Windows manner
by double-clicking on it from the Windows explorer.

But with the Cygwin/MinGW version, you can also use option 2 if you have the
"bash" shell available on your PC. To do so, you need to copy the script
"fdmnes.sh" to your PC and change the variable FDMHOME to point to the directory
where you have installed the FDMNES executable.

If you want to execute FDMNES (with or without MPI) on your own Linux/Unix
computer (e.g. on a beamline), you can only use the second or third option. You
need to copy and modify "fdmnes.sh" as described above for Cygwin/MinGW.

If you want to use the MPI version of FDMNES, you can

- start it with the OpenMPI "mpirun" command. The standard version is in
  "/usr/bin", which should be in your normal execution PATH. However, the MPI
  version of FDMNES has been created with OpenMPI version 2.0.2, the standard
  version on "debian8" is 1.6.5, and the two are not compatible. Therefore you
  have to specifically request the "mpirun" command from OpenMPI 2.0.2, which is
  in "/sware/exp/openmpi/2.0.2/debian8/bin". The easiest way to do this is to
  add this directory to your PATH environment variable with the command:

     export PATH=/sware/exp/openmpi/2.0.2/debian8/bin:$PATH

  Also, Intel has a identically named command as part of its MPI installation.
  To avoid confusion, you might want to use the "orterun" command, which is an
  synonym for the OpenMPI "mpirun" command.

  Furthermore, when starting the MPI version of the FDMNES executable, it needs
  the OpenMPI 2.0.2 libraries, not the standard (1.6.5) version installed on
  "debian8". To do this, you should, before starting the executable, set the
  environment variable LD_LIBRARY_PATH with the command:

     export LD_LIBRARY_PATH=
       /sware/exp/openmpi/2.0.2/debian8/lib${LD_LIBRARY_PATH:+:}$LD_LIBRARY_PATH

     (Note: the whole command is typed on one line without any spaces around the
     equal sign ("="), it is broken up here on two lines only to make it easier
     to read.)

- or you can use the script "fdmnes.sh" (option 2 above) to run the MPI version
  of FDMNES as well. This script will then start FDMNES for you. To get some
  information on how to use it, type "fdmnes.sh -h".

  If you use this script, you do not need to worry about setting your PATH or
  LD_LIBRARY_PATH variables, as the script does this itself.

  Technical note: to avoid overloading the computers on which the MPI version
  runs, "fdmnes.sh" limits for interactive use the number of processes per
  computer to 2. To increase this number, change the variable NPERHOST in the
  script. When working with the OAR scheduler (see "Batch Program Processing"
  below), this limit is not used.

MPI needs two configuration files to run a parallel program:

- a password file, which must reside in your HOME directory and have the name
  ".mpd.conf" (note the leading dot ".");

- a host file, which contains the names of the computers on which the MPI
  program is to run. This file should reside in the directory where you start
  your job from and have the name "mpd.hosts", but that can be changed with the
  "-f" option of "mpirun". This file should contain the names of all "rnice"
  computers if you run on "rnice", etc.

Examples of the configuration files are provided (see section "Directories and
Files" below).

If the configuration files have been put into the default places, then a typical
way to start the MPI version of FDMNES (in this case with 8 processes) is

   orterun -np 8 fdmnes_mpi

or, if you use your own host file with the name "mpd.myhost"

   orterun -hostfile mpd.myhost -np 8 fdmnes_mpi

Using "fdmnes.sh" to start your MPI version of FDMNES, the equivalent commands
would be

   fdmnes.sh -np 8
or
   fdmnes.sh -np 8 -f mpd.myhost

For more details, type "orterun --help" or see the OpenMPI documentation on
"www.open-mpi.org" under "Open MPI Software -> Documentation".

The MPI system tries to distribute your job over several computers. This can
lead to some problems:

- MPI fails with "Permission denied" errors, as it cannot start jobs remotely;
- MPI fails with "No route to start" errors, as one of its target computers is
  unavailable;
- MPI warns that that the authenticity of the host it wants to connect to cannot
  be established, and/or it requests the user's password every time it connects
  to a computer.

These problems will be explained in detail in the following.

a) the MPI system must have the permission to start jobs remotely, otherwise it
   will fail with "Permission denied" errors. One way to grant this permission
   is to have all NICE-Linux computers listed in your own ".rhosts" file. See
   the example file "example.rhosts" and the "man" pages for "rhosts" for more
   information.

b) if one of the computers selected by the MPI system is unavailable (e.g.
   "rnice31" is down), you get the following error message:

      rnice31.esrf.fr: No route to start

   As such a situation may last a while, here is a general way how to get around
   the problem until the corresponding computer is back in operation:

   First verify that the computer is indeed down by trying to log into it.
   Note: getting a response from "ping" is not sufficient. It can happen that
   logon to a computer is no longer possible, but it still responds to "ping".
   Under those circumstances MPI will fail.

   If you can log into the computer but still get this error message, then there
   is a different problem. You will have to try to find out what is happening.

   If, however, the computer is down, then you need to remove it from the list
   of computers that the MPI system uses. This list is in the "host file" (one
   of the MPI configuration files mentioned above).

   If you want to exclude a computer from this list - e.g. "rnice31" in this
   case, as it is not operational - then you should edit the host file to remove
   the "rnice31" entry. Alternatively, you can create a new version of the host
   file under a different name, remove the offending computer there and start
   the MPI run with the appropriate option to use the new host file.

   For more details, see the "orterun" documentation.

c) MPI uses the "SSH" (Secure SHell) mechanism for the communication between the
   various processes that run on different computers for a given MPI job.

   SSH needs two keys, a public and a private one. It uses the private one to
   initiate the communication to the desired remote computer, where the
   encryption mechanism takes it and checks whether it is the correct private
   key for this user's public key.

   For this to work, SSH needs a file with the computers that it can use, and
   one file each for its public and its private key. These files are kept in the
   subdirectory ".ssh" of the user's home directory.

   The file "known_hosts" contains the computer names. If you do not have this
   file, or if the computers that you want to use are not contained in this
   file, you will get a message that the authenticity of the host MPI wants to
   connect to cannot be established. It then asks whether you want to continue.

   You should answer "yes" to that question, as often as it is asked (once for
   each new computer MPI connects to). This will automatically generate or
   update the file "known_hosts", thus when you run the program again, you
   should not be asked the question again, at least not for the same computers!

   Warning: the identification data in "known_hosts" can become outdated, in
   which case you get an error about an incorrect identity. If this happens, the
   easiest is to delete the file "known_hosts", and then have it recreated as
   described above.

   The public and the private key are stored in the files "id_rsa.pub" and
   "id_rsa", respectively. In addition, a third file "authorized_keys" is
   needed.

   If you do not have those files in your ".ssh" directory, then MPI will ask
   you for your password every time it starts a process on a new computer. As
   this is a bit tiring, you should create these files using "ssh-keygen".

   A simple way to get this done is as follows:

   c.1) type (in any directory) "ssh-keygen -t rsa"
   c.2) you get some output, then the following line:
          Enter file in which to save the key (/Your_Home_Dir/.ssh/id_rsa):
   c.3) hit the "Enter" key
   c.4) you get the line:
          Enter passphrase (empty for no passphrase):
   c.5) hit the "Enter" key
   c.6) you get the line:
          Enter same passphrase again:
   c.7) hit the "Enter" key
   c.8) the program runs and should tell you where your "identification" and
        your "public key" has been saved.

   You should now have in your ".ssh" directory the two new files "id_rsa" and
   "id_rsa.pub".

   The file "authorized_keys" is just a copy of the file "id_rsa.pub", thus copy   it over:

      cp id_rsa.pub authorized_keys

   For more details, see the manual pages for "ssh" and "ssh-keygen".


3) Batch Program Processing
---------------------------

Instead of starting the program manually and then waiting for it to finish while
looking at the output on the screen, the program can also be submitted to a
batch queue. The scheduler of the queue will then execute it, based on the
user's requirements. This is in particular recommended if long jobs are to be
run and/or if the user wants to have several (many) jobs to be processed, but
does not necessarily want them all to occupy the computer at the same time.

At the ESRF, we use the OAR batch scheduler for the computers with the Debian 8
operating system, in particular for the high-performance clusters "hpc" and
"hib".

When using the batch scheduler to submit MPI jobs, you do not need to specify a
host file for MPI nor set up the public and private keys for SSH (see section
"Program Execution" above), as the batch manager will take care of this. You
must, however, still supply the MPI password file.


Use of OAR
----------

The OAR scheduler is used at the ESRF for computers running the Debian 8
operating system, in particular the high-performance clusters "hpc" and "hib"
(see http://wikiserv.esrf.fr/software/index.php/Main_Page for details of the
ESRF's installation, or the documentation on the OAR home page
http://oar.imag.fr/users/user_documentation.html).

OAR is more than just a batch queue scheduler, it is a resource scheduler. In
particular, it is possible to reserve computing resources with OAR for
interactive computing. In fact, this is the only way to run interactive jobs on
the high-performance cluster, as no direct login is allowed on the "hpc" and
"hib" computers.

A side effect of OAR being a resource scheduler is that you must specify how
long (elapsed time) you want to use the resource. This is different from the way
some other schedulers work, where a job always runs to its end, no matter how
long that takes. OAR will terminate a job once the reserved length of time is
over.

As you cannot directly log into the ESRF's high-performance cluster, the "rnice"
computers serve as the front end. To use the high-performance cluster, you log
into one of those computers and use the OAR commands to request computing
resources on the high-performance cluster. OAR then schedules and grants these
requests and (in the case of a batch job) runs the corresponding jobs on the
high-performance cluster.

The OAR commands are in "/usr/bin", and the manual pages in "/usr/share/man".
For the normal user, there are essentially three commands that are useful:

- "oarsub"    to request a resource (submit a job to the batch queue);
- "oarstat"   to inquire about the status of the submitted jobs;
- "oardel"    to remove jobs from the batch queue.

For detailed information, see the corresponding manual pages.

The "oarstat" command, when used without any arguments, gives the status of all
jobs in the system. This is slow, and probably not what most people want. To get
only the status of your own jobs, use the "-u" option:

   oarstat -u dupont

gives only the status of the jobs submitted by user "dupont".

The "oarsub" command can be used to request resources for interactive computing,
or to submit a job to the batch queue. In both cases, you need to specify which
resources you need and for how long with the "-l" option.

This option allows to make quite specific requests (e.g. only for CPUs of a
certain manufacturer, or with at least a given amount of memory, or...).
However, the request most often used is likely to be for a number of cores.

To request a certain number of cores for a given time, the option takes the
following form:

   -l /core=ncore,walltime=nh:nm:ns

with
   ncore: the number of cores
   nh   : the number of hours to run
   nm   : the number of minutes to run
   ns   : the number of seconds to run

The default is one computer core for two hours.

Time for interactive processing can be requested with the "-I" option of
"oarsub". Examples:

   oarsub -I

requests interactive use of one core for two hours.

   oarsub -I -l /core=4,walltime=0:20:00

requests interactive use of four cores for 20 minutes.

When granting the request, OAR logs into one of the high-performance computers,
and the user obtains an interactive shell on that computer. This can now be used
for any task desired.

It is in particular possible to run the parallel version of FDMNES
interactively, using e.g. the "fdmnes.sh" script described above in the section
"Program Execution". In this case it is not necessary to specify the number of
parallel processes (i.e. the "-np" parameter) to "fdmnes.sh". The script tests
if it has been called from an OAR environment, and if so it sets the number of
processes accordingly.

Instead of running interactively, you can also submit a job to the batch handler
by specifying an executable in the "oarsub" command. OAR then runs the
executable using the resources and the time requested. Note that the submit
commands are issued on the front-end computers, but the jobs run on the
high-performance cluster.

Thus in order to run the parallel version of FDMNES with the "fdmnes.sh" script
on 5 cores for 1 hour and 30 minutes of elapsed time, the "oarsub" command on
"rnice" is:

   oarsub -l /core=5,walltime=1:30:0 /sware/exp/fdmnes/fdmnes.sh

Warning: the full path of the executable must be specified! As in the
interactive case, the number of parallel processes needs not to be given.

If only one job is to be run by the batch scheduler, the easiest is to submit it
from the directory where the FDMNES input file "fdmfile.txt" resides. If,
however, more than one job is to be submitted, matters get more complicated, as
FDMNES does not allow different names for its input file.

The solution is to have several data directories, one for each job. Each
directory contains its own "fdmfile.txt" and (if needed) the additional files
"xsect.dat" and "spacegroup.txt", as well as the input files for the
calculations to be performed (see below "Input Files").

In the "oarsub" command you then specify with the "-d" option for each job
separately the name of the directory where the job will be started. All input
and output for this particular job will refer to that directory, even if the
"oarsub" command was issued in a different directory.

The syntax of the "-d" option is

   -d name_of_directory

with "name_of_directory" the full name (with path) of the directory where the
corresponding job is to start.

In order to start two parallel FDMNES jobs on 5 cores for 1 hour each, the user
"johndoe" might set up the two subdirectories "example_1" and "example_2" and
then type the commands

   oarsub -d /users/johndoe/example_1 -l /core=5,walltime=1:30:0 
      /sware/exp/fdmnes/fdmnes.sh

   oarsub -d /users/johndoe/example_2 -l /core=5,walltime=1:30:0 
      /sware/exp/fdmnes/fdmnes.sh

(Each "oarsub" command is fully typed on one line, they are distributed over two
lines here only for better readability!)

To make the task of submitting jobs to the OAR batch queue easier, there is the
script "fdmnes_oar.sh" that can be used for this purpose. In this script, you
have to modify the provided examples to suit your needs, and then just execute
the script on "rnice". Thus the above "oarsub" command on "rnice" could be
replaced by simply typing:

   fdmnes_oar.sh

One advantage of using this script is that many jobs can be submitted with just
one "fdmnes_oar.sh" command. See the explanations in the script for more
details.


4) Input Files
--------------

To execute the example, copy the input files of the example (see below
"Directories and Files", files "fdmfile.txt", "spacegroup.txt", "xsect.dat" and
subdirectory "Sim") into your own directory.

Note: the input files have been created on a WINDOWS system and therefore have
the corresponding file properties. This means in particular that the "end of
line" is indicated by a <CR><NL>, instead of just a <NL> as on UNIX systems. If
you want to use the examples on WINDOWS, this is what you need. If you want to
use them on LINUX, this will also work, as LINUX knows how to handle both UNIX
and WINDOWS style files. However, if you want to use them on other UNIX systems,
you will have to convert the files to UNIX style by removing the additional
<CR>, otherwise you will get read errors during execution.

The concerned files are: "fdmfile.txt", "spacegroup.txt", "xsect.dat", and all
files in the subdirectory "Sim/Test_stand/in" (see below "Directories and
Files").


5) Directories and Files
------------------------
This directory contains the following subdirectories and files:

Readme_ESRF.txt  this file

fdmfile.txt      FDMNES general input data file (contains the number and names 
                 of the "indata" files, see "Sim" directory below)
xsect.dat        input file for resonant spectroscopy
spacegroup.txt   input file with all space groups

fdmnes_win32.exe FDMNES executable for Windows 32 bit
fdmnes_win64.exe FDMNES executable for Windows 64 bit

fdmnes_mac       FDMNES executable for Mac OS

fdmnes_linux64   FDMNES executable for 64-bit LINUX (gfortran)

fdmnes.sh        script to run the FDMNES program at the ESRF. It allows to run
                 the non-MPI or the MPI version of FDMNES and also to specify a
                 different name for the input file "fdmfile.txt".

                 Although set up for the ESRF central computers, this script can
                 easily be re-configured for a particular user environment on a
                 beamline or desktop computer and could thus provide an uniform
                 user interface for FDMNES in varying configurations.

                 For more information, see the description in the file.

fdmnes_intel.sh  as "fdmnes.sh", but runs the old versions of FDMNES that were
                 compiled with the Intel compiler and MPI libraries

mpd.password     the password file needed by MPI. Copy it to $HOME/.mpd.conf
                 Note: for security reasons, this file must have read- and
                 write-permissions only for the owner (permission code 600)!

mpd.hosts.debian8 the host files needed by MPI for 64-bit Linux. Copy it to
		  "mpd.hosts" in your working directory; or use the "-hostfile"
		  option of "orterun" (the "-f" option if using "fdmnes.sh").

example.rhosts   example of a ".rhosts" file needed to run the MPI version of
                 FDMNES. The username "wilcke" in this file must be replaced by
                 the username of the person starting the MPI executable.
                 Note: for security reasons, this file must have read- and
                 write-permissions only for the owner (permission code 600)!

                 For more information, see the "man" pages for "rhosts".

fdmnes_oar.sh    example of a script to submit FDMNES jobs (MPI and non-MPI) to
                 the OAR batch scheduler

fdmnes_oar_intel.sh  as "fdmnes_oar.sh", but for use with the script
                     "fdmnes_intel.sh" to run the old versions of FDMNES

bin              directory with the executables of FDMNES for Linux and Cygwin.
                 This directory contains the following subdirectories for the
                 different types of computer and operating system:

                 - mingw        32-bit Windows PCs, compiled with "gfortran"
                 - cygwin       same as "mingw"
                 - debian8      64-bit Linux systems with Debian version 8
                 - debian9      64-bit Linux systems with Debian version 9

Doc              directory with the documentation for FDMNES:
                 - readme.txt          general FDMNES information
                 - FDMNES_Modifications.txt
                                       list of corrections and modifications
                 - Manuel_Eng.pdf      FDMNES manual in English
                 - Manuel.pdf          FDMNES manual in French (more detailed
                                       than Manuel_Eng.pdf)
                 - Notes_SpectroX.pdf  notes on X-ray absorption spectroscopy
                                       (in French)

prog             directory with:
                 - readme_prog.txt  file with details about the source files
                 - *.f90            the FORTRAN source files
                 - include          directory with the header files for the
		                    dummy MPI and the MUMPS routines 
                 - Makefile         a (GNU) Makefile to create the executables
                                    for Linux and Cygwin/MinGW
		 - makefile_mumps   example makefile to compile FDMNES with the
		                    gfortran compiler and the MUMPS libraries
                 - makefile_gauss   example makefile to compile FDMNES with the
		                    gfortran compiler without external libraries

Sim/Test_stand   data directory for the input and output files for an example
                 application of FDMNES.

		 This directory contains the subdirectory "in" with the complete
		 input files for the different calculations specified in the
		 "fdmfile.txt" file of the FDMNES distribution.

                 For each calculation there is at least one input file with the
                 name "*_inp.txt". This is the "indata" (= input data) file
                 referred to in the description of "fdmfile.txt" above.

		 The output files will be created in the "Sim/Test_stand"
		 directory itself.

                 The 32 examples do different types of calculations. The input
                 and output files for the examples are therefore different as
                 well. For more information on these files, see the FDMNES
                 manuals mentioned above.
