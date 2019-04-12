This package contains:

- "fdmnes_win64.exe"   : executable of fdmnes for Windows 64 bits
- "fdmnes_win32.exe"   : executable of fdmnes for Windows 32 bits
- "fdmnes_linux64"     : executable of fdmnes for Linux 64 bits (Intel)
- "fdmnes_mac"         : executable of fdmnes for Mac OS

- run_fdmnes_command   : Command for Mac OS to execute fdmnes_mac.
                         When clicking on it, the working directory of fdmnes_mac is the current rirectory
                         and not the default user's home directory.

- "Sim/Test_stand/in"  : directory containing a set of examples of indata files for fdmnes
- "fdmfile.txt"        : fdmnes indata file  

- "Manuel.pdf"         : manual in French
- "Manuel_Eng.pdf"     : manual in English
- "Notes_SpectroX.pdf" : Notes on x-ray absorption spectroscopies in French
- "FDMNES_modifications.txt" : summary of the modifications and corrections in FDMNES

- "prog"               : directory containing the different fortran fdmnes routines for people who want to produce their own executable.
                         To compile with a fortran 90 / 95 compiler.
                         It contains also examples of makefile and a readme_prog important to read.
   
fdmfile.txt must be in the same directory than the executable when running.
On Mac and on Linux when clicking on the executable, if fdmfile.txt is not found anyway,
this means that the default working directory is not the current one where is the executable.
This problem is solved for Mac by clicking on the command "run_fdmnes_command" instad of directly on the executable.

When the example indata files are not working, especially under linux, open them, save and close them,
then try again.
