#!/usr/bin/env python
#
# Copyright (C) 2003-2014 Intel Corporation.  All Rights Reserved.
# 
# The source code contained or described herein and all documents
# related to the source code ("Material") are owned by Intel Corporation
# or its suppliers or licensors.  Title to the Material remains with
# Intel Corporation or its suppliers and licensors.  The Material is
# protected by worldwide copyright and trade secret laws and treaty
# provisions.  No part of the Material may be used, copied, reproduced,
# modified, published, uploaded, posted, transmitted, distributed, or
# disclosed in any way without Intel's prior express written permission.
# 
# No license under any patent, copyright, trade secret or other
# intellectual property right is granted to or conferred upon you by
# disclosure or delivery of the Materials, either expressly, by
# implication, inducement, estoppel or otherwise.  Any license under
# such intellectual property rights must be express and approved by
# Intel in writing.
#
#   (C) 2001 by Argonne National Laboratory.
# 
# 				  MPICH2 COPYRIGHT
# 
# The following is a notice of limited availability of the code, and disclaimer
# which must be included in the prologue of the code and in all source listings
# of the code.
# 
# Copyright Notice
#  + 2002 University of Chicago
# 
# Permission is hereby granted to use, reproduce, prepare derivative works, and
# to redistribute to others.  This software was authored by:
# 
# Mathematics and Computer Science Division
# Argonne National Laboratory, Argonne IL 60439
# 
# (and)
# 
# Department of Computer Science
# University of Illinois at Urbana-Champaign
# 
# 
# 			      GOVERNMENT LICENSE
# 
# Portions of this material resulted from work developed under a U.S.
# Government Contract and are subject to the following license: the Government
# is granted for itself and others acting on its behalf a paid-up, nonexclusive,
# irrevocable worldwide license in this computer software to reproduce, prepare
# derivative works, and perform publicly and display publicly.
# 
# 				  DISCLAIMER
# 
# This computer code material was prepared, in part, as an account of work
# sponsored by an agency of the United States Government.  Neither the United
# States, nor the University of Chicago, nor any of their employees, makes any
# warranty express or implied, or assumes any legal liability or responsibility
# for the accuracy, completeness, or usefulness of any information, apparatus,
# product, or process disclosed, or represents that its use would not infringe
# privately owned rights.
# 
# Portions of this code were written by Microsoft. Those portions are
# Copyright (c) 2007 Microsoft Corporation. Microsoft grants permission to
# use, reproduce, prepare derivative works, and to redistribute to
# others. The code is licensed "as is." The User bears the risk of using
# it. Microsoft gives no express warranties, guarantees or
# conditions. To the extent permitted by law, Microsoft excludes the
# implied warranties of merchantability, fitness for a particular
# purpose and non-infringement.
# 
# 
#
#       
#

"""
usage:
mpiexec [-h or -help or --help]    # get this message
mpiexec [-V or -version or --version] # prints version information
mpiexec -file filename             # (or -f) filename contains XML job description
mpiexec [global args] [local args] executable [args]
   where global args may be
      -l                           # line labels by MPI rank
      -bnr                         # MPICH1 compatibility mode
      -machinefile                 # file mapping procs to machines
      -nolocal                     # do not start on local system
      -perhost <n>                 # place consecutive <n> processes on each host
      -ppn <n>                     # stand for "process per node"; an alias to -perhost <n>
      -grr <n>                     # stand for "group round robin"; an alias to -perhost <n>
      -rr                          # involve "round robin" startup scheme
      -s <spec>                    # direct stdin to "all" or 1,2 or 2-4,6
      -1                           # override default of trying 1st proc locally
      -ifhn                        # network interface to use locally
      -tv                          # run procs under totalview (must be installed)
      -tvsu                        # totalview startup only
      -gdb                         # run procs under gdb
      -idb                         # run procs under idb
      -m                           # merge output lines (default with gdb)
      -a                           # means assign this alias to the job
      -ecfn                        # output_xml_exit_codes_filename
      -recvtimeout <integer_val>   # timeout for recvs to fail (e.g. from mpd daemon)
      -g<local arg name>           # global version of local arg (below)
      -trace [<libraryname>]       # trace the application using <libraryname> profiling library;
                                   # default is libVT.so
      -check_mpi [<libraryname>]   # check the application using <libraryname> checking library;
                                   # default is libVTmc.so
      -ilp64                       # Preload ilp64 wrapper library for support default size of 
                                   # integer 8 bytes
      -tune [<confname>]           # apply the tuned data produced by the MPI Tuner utility
      -noconf                      # do not use any mpiexec's configuration files
    and local args may be
      -n <n> or -np <n>            # number of processes to start
      -wdir <dirname>              # working directory to start in
      -umask <umask>               # umask for remote process
      -path <dirname>              # place to look for executables
      -host <hostname>             # host to start on
      -soft <spec>                 # modifier of -n value
      -arch <arch>                 # arch type to start on (not implemented)
      -envall                      # pass all env vars in current environment
      -envnone                     # pass no env vars
      -envlist <list of env var names> # pass current values of these vars
      -envexcl <list of env var names> # do not pass the env vars listed
      -envuser                     # pass all env vars except the hardware, system ones
      -env <name> <value>          # pass this value of this env var
mpiexec [global args] [local args] executable args : [local args] executable...
mpiexec -gdba jobid                # gdb-attach to existing jobid
mpiexec -idba jobid                # idb-attach to existing jobid
mpiexec -configfile filename       # filename contains cmd line segs as lines
  (See Reference Manual for more details)

Examples:
   mpiexec -l -n 10 cpi 100
   mpiexec -genv QPL_LICENSE 4705 -n 3 a.out

   mpiexec -n 1 -host foo master : -n 4 -host mysmp slave

Copyright (C) 2003-2014 Intel Corporation.  All rights reserved.
"""
from time import ctime, sleep
__author__ = "Ralph Butler and Rusty Lusk"
__date__ = ctime()
__version__ = "$Revision: 9833 $"
__credits__ = ""

import signal
if hasattr(signal,'SIGTTIN'):
    signal.signal(signal.SIGTTIN,signal.SIG_IGN)    # asap

import sys, os, socket, re, errno


from sys import version
if version[0] == '2' and version[1] == '.' and version[2] > '4':
    import warnings
    warnings.filterwarnings("ignore", "", DeprecationWarning)
use_subprocess=0
if os.environ.has_key('I_MPI_PYTHON_MODULES'):
    modules = os.environ['I_MPI_PYTHON_MODULES']
    if modules == 'popen2':
        use_subprocess = 0
    elif modules == 'subprocess':
        use_subprocess = 1
if use_subprocess:
    try:
        import subprocess
        subprocess_module_available = 1
    except:
        import popen2
        subprocess_module_available = 0
else:
    try:
        import popen2
        subprocess_module_available = 0
    except:
        import subprocess
        subprocess_module_available = 1



from  urllib import quote
from  time   import time
from  urllib import unquote
from  string import printable

try:
    import mpdlib
except EOFError, e:
    import mpdlib

try:
    import pwd
    pwd_module_available = 1
except:
    pwd_module_available = 0

global parmdb, nextRange, appnum, recvTimeout
global numDoneWithIO, myExitStatus, sigOccurred, outXmlDoc, outECs

recvTimeoutDefault = 20  # const
recvTimeout = recvTimeoutDefault

def mpiexec():
    global parmdb, nextRange, appnum, recvTimeout
    global numDoneWithIO, myExitStatus, sigOccurred, outXmlDoc, outECs

    import sys  # for sys.excepthook on next line
    sys.excepthook = mpdlib.mpd_uncaught_except_tb

    myExitStatus = 0
    if len(sys.argv) < 2  or  sys.argv[1] == '-h'  \
    or  sys.argv[1] == '-help'  or  sys.argv[1] == '--help':
        usage()

    for i in xrange(1, len(sys.argv)):
        if sys.argv[i] == '-V' or sys.argv[i] == '-version' or sys.argv[i] == '--version':
            vers = 'Version 4.1.3  Build 20140226'
            print 'Intel(R) MPI Library for Linux* OS, 32-bit applications,',vers
            print 'Copyright (C) 2003-2014 Intel Corporation.  All rights reserved.\n'
            if len(sys.argv) < 3:
                sys.exit(0)

    myHost = socket.gethostname()
    mpdlib.mpd_set_my_id(myid='mpiexec_%s' % (myHost) )
    try:
        hostinfo = socket.gethostbyname_ex(myHost)
        myIP = hostinfo[2][0]

    except Exception, errmsg:
        #print 'mpiexec failed: gethostbyname_ex failed for %s: %s' % (myHost,errmsg)
        myIP = myHost

        #sys.exit(-1)
    
    # Needed to avoid bad system configuration
    # hostname localhost 127.0.0.1

    if myIP.startswith('127.0.0'):

       myIP = myHost
    

    

# Unset I_MPI_DEVICE if I_MPI_FABRICS was exported.
    if os.environ.has_key('I_MPI_FABRICS'):
        if os.environ.has_key('I_MPI_DEVICE'):
            del os.environ['I_MPI_DEVICE']

    sysfullDirName = os.path.abspath(os.path.split(sys.argv[0])[0])  # normalize for platform also
    sysfullDirName = os.path.abspath(os.path.split(sysfullDirName)[0])
    sysconfFileName = os.path.join(sysfullDirName,'etc/mpiexec.conf')

#    systempargv = [] # Contains arguments from $HOME/.mpiexec.conf and $PWD/mpiexec.conf
    systempargv = [] # Contains arguments from $PWD/mpiexec.conf
    syshometempargv = [] # Contains arguments from $HOME/.mpiexec.conf


    sysroottempargv = [] # Contains arguments from the <mpiinstalldir>/etc/mpiexec.conf file

    try:
        sysconfigFileFD = os.open(sysconfFileName, os.O_RDONLY)
    except:
        pass
    else:
        sysconfigFile = os.fdopen(sysconfigFileFD,'r',0)
        sysconfigLines = sysconfigFile.readlines()
        sysconfigLines = [ x.strip()  for x in sysconfigLines if x[0] != '#' ]
        for line in sysconfigLines:

            tmp_cmd = "/bin/sh -c 'for a in $*; do echo _$a; done' -- %s" % (line)
            if subprocess_module_available:
                tmp_cmd = []
                tmp_cmd.append('/bin/sh')
                tmp_cmd.append('-c')
                tmp_cmd.append('for a in $*; do echo _$a; done')
                tmp_cmd.append('--')
                tmp_cmd.append('%s' % (line))
                sysshOut = subprocess.Popen(tmp_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
                out_from_child = sysshOut.stdout
            else:
                sysshOut = popen2.Popen3(tmp_cmd)
                out_from_child = sysshOut.fromchild
            for shline in out_from_child:


#               systempargv.append(shline[1:].strip())    # 1: strips off the leading _
                sysroottempargv.append(shline[1:].strip())    # 1: strips off the leading _


# Remove all I_MPI_DEVICE entries if I_MPI_FABRICS exists.
        remove_device_entries(sysroottempargv)


    if os.environ.has_key('HOME'):
        sysconfFileName = os.environ['HOME'] + '/.mpiexec.conf'


#    systempargv = []

    try:
        sysconfigFileFD = os.open(sysconfFileName, os.O_RDONLY)
    except:
        pass
    else:
        sysconfigFile = os.fdopen(sysconfigFileFD,'r',0)
        sysconfigLines = sysconfigFile.readlines()
        sysconfigLines = [ x.strip()  for x in sysconfigLines if x[0] != '#' ]
        for line in sysconfigLines:

            tmp_cmd = "/bin/sh -c 'for a in $*; do echo _$a; done' -- %s" % (line)
            if subprocess_module_available:
                tmp_cmd = []
                tmp_cmd.append('/bin/sh')
                tmp_cmd.append('-c')
                tmp_cmd.append('for a in $*; do echo _$a; done')
                tmp_cmd.append('--')
                tmp_cmd.append('%s' % (line))
                sysshOut = subprocess.Popen(tmp_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
                out_from_child = sysshOut.stdout
            else:
                sysshOut = popen2.Popen3(tmp_cmd)
                out_from_child = sysshOut.fromchild
            for shline in out_from_child:


#                systempargv.append(shline[1:].strip())    # 1: strips off the leading _
                syshometempargv.append(shline[1:].strip())    # 1: strips off the leading _
# Remove all I_MPI_DEVICE entries if I_MPI_FABRICS exists.
        remove_device_entries(syshometempargv)

    sysconfFileName = './mpiexec.conf'

#    systempargv = []

    try:
        sysconfigFileFD = os.open(sysconfFileName, os.O_RDONLY)
    except:
        pass
    else:
        sysconfigFile = os.fdopen(sysconfigFileFD,'r',0)
        sysconfigLines = sysconfigFile.readlines()
        sysconfigLines = [ x.strip()  for x in sysconfigLines if x[0] != '#' ]
        for line in sysconfigLines:

            tmp_cmd = "/bin/sh -c 'for a in $*; do echo _$a; done' -- %s" % (line)
            if subprocess_module_available:
                tmp_cmd = []
                tmp_cmd.append('/bin/sh')
                tmp_cmd.append('-c')
                tmp_cmd.append('for a in $*; do echo _$a; done')
                tmp_cmd.append('--')
                tmp_cmd.append('%s' % (line))
                sysshOut = subprocess.Popen(tmp_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
                out_from_child = sysshOut.stdout
            else:
                sysshOut = popen2.Popen3(tmp_cmd)
                out_from_child = sysshOut.fromchild
            for shline in out_from_child:

                systempargv.append(shline[1:].strip())    # 1: strips off the leading _
    

# Remove all I_MPI_DEVICE entries if I_MPI_FABRICS exists.
        remove_device_entries(systempargv)
# Remove I_MPI_FABRICS, I_MPI_DEVICE entries which were added from <installdir>/etc/mpiexec.conf, ${HOME}/.mpiexec.conf, if I_MPI_FABRICS or I_MPI_DEVICE exist into ${PWD}/mpiexec.conf
    remove_low_priorities_entries(sysroottempargv,systempargv)
    remove_low_priorities_entries(syshometempargv,systempargv)
# Remove I_MPI_FABRICS, I_MPI_DEVICE entries which were added from <installdir>/etc/mpiexec.conf, if I_MPI_FABRICS or I_MPI_DEVICE exist into ${HOME}/.mpiexec.conf
    remove_low_priorities_entries(sysroottempargv,syshometempargv)
    syshometempargv.extend(systempargv)
    systempargv=syshometempargv


    parmdb = mpdlib.MPDParmDB(orderedSources=['cmdline','xml','env','rcfile','thispgm'])
    parmsToOverride = {
                        'MPD_USE_ROOT_MPD'            :  0,
                        'MPD_SECRETWORD'              :  '',
                        'MPIEXEC_SHOW_LINE_LABELS'    :  0,
                        'MPIEXEC_LINE_LABEL_FMT'      :  '%r',
                        'MPIEXEC_JOB_ALIAS'           :  '',
                        'MPIEXEC_USIZE'               :  0,
        
                        'MPIEXEC_NOLOCAL'             :  0,
                        'MPIEXEC_PERHOST'             :  0,
        
                        'MPIEXEC_GDB'                 :  0,
                        'MPIEXEC_IFHN'                :  '',  # use one from mpd as default
                        'MPIEXEC_MERGE_OUTPUT'        :  0,
                        'MPIEXEC_STDIN_DEST'          :  '0',
                        'MPIEXEC_MACHINEFILE'         :  '',
                        'MPIEXEC_BNR'                 :  0,
                        'MPIEXEC_TOTALVIEW'           :  0,
                        'MPIEXEC_TVSU'                :  0,

                        'MPIEXEC_IDB'                 :  0,

                        'MPIEXEC_EXITCODES_FILENAME'  :  '',
                        'MPIEXEC_TRY_1ST_LOCALLY'     :  1,
                        'MPIEXEC_TIMEOUT'             :  0,
                        'I_MPI_JOB_TIMEOUT'           :  0,
                        'MPIEXEC_HOST_LIST'           :  [],
                        'MPIEXEC_HOST_CHECK'          :  0,

                        'MPIEXEC_LDPRELOAD'           :  '',


                        'MPIEXEC_ORDERED_OUTPUT'              :  0,

                        'MPIEXEC_RECV_TIMEOUT'        :  20,
                      }
    for (k,v) in parmsToOverride.items():
        parmdb[('thispgm',k)] = v
    parmdb[('thispgm','mship')] = ''
    parmdb[('thispgm','rship')] = ''
    parmdb[('thispgm','userpgm')] = ''
    parmdb[('thispgm','nprocs')] = 0
    parmdb[('thispgm','ecfn_format')] = ''
    parmdb[('thispgm', '-gdba')] = ''

    parmdb[('thispgm', '-idba')] = ''


    parmdb[('thispgm', '-tva')] = ''

    parmdb[('thispgm','gdb_attach_jobid')] = ''
    parmdb[('thispgm','singinitpid')] = 0
    parmdb[('thispgm','singinitport')] = 0
    parmdb[('thispgm','ignore_rcfile')] = 0
    parmdb[('thispgm','ignore_environ')] = 0
    parmdb[('thispgm','inXmlFilename')] = ''
    parmdb[('thispgm','print_parmdb_all')] = 0
    parmdb[('thispgm','print_parmdb_def')] = 0

    appnum = 0
    nextRange = 0
    localArgSets = { 0 : [] }

    if sys.argv[1] == '-gdba':
        if len(sys.argv) != 3:
            print '-gdba arg must appear only with jobid'
            usage()
        parmdb[('cmdline','-gdba')] = sys.argv[2] 
        parmdb[('cmdline','MPIEXEC_GDB')] = 1 
        parmdb[('cmdline','MPIEXEC_MERGE_OUTPUT')] = 1       # implied
        parmdb[('cmdline','MPIEXEC_SHOW_LINE_LABELS')] = 1   # implied
        parmdb[('cmdline','MPIEXEC_STDIN_DEST')]   = 'all'   # implied

    elif sys.argv[1] == '-idba':
        if len(sys.argv) != 3:
            print '-idba arg must appear only with jobid'
            usage()
        parmdb[('cmdline','-idba')] = sys.argv[2]


    elif sys.argv[1] == '-tva':
        if len(sys.argv) != 3:
            print '-tva arg must appear only with jobid'
            usage()
        parmdb[('cmdline','-tva')] = sys.argv[2]

    elif sys.argv[1] == '-file'  or  sys.argv[1] == '-f':
        if len(sys.argv) != 3:
            print '-file (-f) arg must appear alone'
            usage()
        parmdb[('cmdline','inXmlFilename')] = sys.argv[2]
    elif sys.argv[1] == '-pmi_args':
        parmdb[('cmdline','singinitport')] = sys.argv[2]
        # ignoring interface name (where app is listening) and authentication key, for now
        parmdb[('cmdline','singinitpid')]  = sys.argv[5]
        parmdb[('cmdline','userpgm')] = 'unknown_pgmname'
        parmdb[('cmdline','nprocs')] = 1
        parmdb[('cmdline','MPIEXEC_TRY_1ST_LOCALLY')] = 1
        machineFileInfo = {}
        tempargv = [sys.argv[0],'unknown_pgmname']
        collect_args(tempargv,localArgSets)
    else:
        if sys.argv[1] == '-configfile':
            if len(sys.argv) != 3:
                usage()
            configFile = open(sys.argv[2],'r',0)
            configLines = configFile.readlines()
            configLines = [ x.strip() + ' : '  for x in configLines if x[0] != '#' and x.strip() != '' ]
            tempargv = []
#           tempargv.extend(systempargv)  

            colon = 0

            for line in configLines:

#                line = 'mpddummyarg ' + line  # gets pitched in shells that can't handle --

                (shellIn,shellOut) = \
                    os.popen4("/bin/sh -c 'for a in $*; do echo _$a; done' -- %s" % (line))
                for shellLine in shellOut:

                    resLine = shellLine[1:].strip() # 1: strips off the leading _
                    if resLine == ':':
                        colon += 1
                    else:
                        colon = 0
                    if colon == 2:
                        colon = 1
                        continue
                    if resLine:
                        tempargv.append(resLine)

            tempargv = [sys.argv[0]] + tempargv[0:-1]   # strip off the last : I added

            newtempargv = [ tempargv[0] ]
            if '-tune' in tempargv:
                if '-noconf' in tempargv:
                    tunedargs = get_tuned_values(tempargv, [], [], sysfullDirName)
                else:
                    tunedargs = get_tuned_values(tempargv, sysroottempargv, systempargv, sysfullDirName)
                newtempargv.extend(tunedargs)
            else:
                if not '-noconf' in tempargv:
                    newtempargv.extend(sysroottempargv)
                    newtempargv.extend(systempargv)

# Remove I_MPI_FABRICS, I_MPI_DEVICE entries which were added from <installdir>/etc/mpiexec.conf, ${HOME}/.mpiexec.conf, if I_MPI_FABRICS or I_MPI_DEVICE exist into environment
            if os.environ.has_key('I_MPI_DEVICE') or os.environ.has_key('I_MPI_FABRICS'):
                while 1:
                    try:
                        i=newtempargv.index('I_MPI_FABRICS')
                        del newtempargv[i-1]
                        del newtempargv[i-1]
                        del newtempargv[i-1]
                    except ValueError:
                        break
                while 1:
                    try:
                        i=newtempargv.index('I_MPI_DEVICE')
                        del newtempargv[i-1]
                        del newtempargv[i-1]
                        del newtempargv[i-1]
                    except ValueError:
                        break

            argidx = 0
            while argidx < len(newtempargv):
                if newtempargv[argidx] == '-genv' and os.environ.has_key(newtempargv[argidx+1]):
                    newtempargv[argidx:argidx+3] = []
                else:
                    argidx += 1

#            newtempargv.extend(tempargv[1:])
# Remove I_MPI_DEVICE from global and local arg sets of -configfile if I_MPI_FABRICS exists.
            tmptempargv=tempargv[1:]
            configargv=[]
            while 1:
                try:
                    tmp=tmptempargv[0:tmptempargv.index('-host')]
                    del tmptempargv[0:tmptempargv.index('-host')+1]
                    remove_device_entries(tmp)
                    configargv.extend(tmp)
                    configargv.append('-host')
                except ValueError:
                    remove_device_entries(tmptempargv)
                    configargv.extend(tmptempargv)
                    break
# Remove I_MPI_FABRICS, I_MPI_DEVICE entries which were added from <installdir>/etc/mpiexec.conf and remove them also from environment, if I_MPI_FABRICS or I_MPI_DEVICE exist into configuration file of -configfile option
            remove_low_priorities_and_environment_entries(newtempargv,configargv)
            newtempargv.extend(configargv)

            collect_args(newtempargv,localArgSets)

#            collect_args(tempargv,localArgSets)
        else:
            
            tempargv = [ sys.argv[0] ]

            if '-tune' in sys.argv:
                if '-noconf' in sys.argv:
                    tunedargs = get_tuned_values(sys.argv, [], [], sysfullDirName)
                else:
                    tunedargs = get_tuned_values(sys.argv, sysroottempargv, systempargv, sysfullDirName)
                tempargv.extend(tunedargs)
            else:
                if not '-noconf' in sys.argv:
                    tempargv.extend(sysroottempargv)
                    tempargv.extend(systempargv)

# Remove I_MPI_FABRICS, I_MPI_DEVICE entries which were added from <installdir>/etc/mpiexec.conf, ${HOME}/.mpiexec.conf, if I_MPI_DEVICE exists into environment
            if os.environ.has_key('I_MPI_DEVICE') or os.environ.has_key('I_MPI_FABRICS'):
                while 1:
                    try:
                        i=tempargv.index('I_MPI_FABRICS')
                        del tempargv[i-1]
                        del tempargv[i-1]
                        del tempargv[i-1]
                    except ValueError:
                        break
                while 1:
                    try:
                        i=tempargv.index('I_MPI_DEVICE')
                        del tempargv[i-1]
                        del tempargv[i-1]
                        del tempargv[i-1]
                    except ValueError:
                        break

            argidx = 0
            while argidx < len(tempargv):
                if tempargv[argidx] == '-genv' and os.environ.has_key(tempargv[argidx+1]):
                    tempargv[argidx:argidx+3] = []
                else:
                    argidx += 1

#           tempargv.extend(systempargv)

# Remove I_MPI_DEVICE from global and local arg sets of command line if I_MPI_FABRICS exists.
#            tempargv.extend(sys.argv[1:])
            tmptempargv=sys.argv[1:]
            commandlineargv=[]
            while 1:
                try:
                    tmp=tmptempargv[0:tmptempargv.index('-host')]
                    del tmptempargv[0:tmptempargv.index('-host')+1]
                    remove_device_entries(tmp)
                    commandlineargv.extend(tmp)
                    commandlineargv.append('-host')
                except ValueError:
                    remove_device_entries(tmptempargv)
                    commandlineargv.extend(tmptempargv)
                    break
# Remove I_MPI_FABRICS, I_MPI_DEVICE entries which were added from <installdir>/etc/mpiexec.conf and remove them also from environment, if I_MPI_FABRICS or I_MPI_DEVICE exist into command line
            remove_low_priorities_and_environment_entries(tempargv, commandlineargv)
            tempargv.extend(commandlineargv)

            
            collect_args(tempargv,localArgSets)
        machineFileInfo = read_machinefile(parmdb['MPIEXEC_MACHINEFILE'])

    # set some default values for mpd; others added as discovered below
    msgToMPD = { 'cmd'            : 'mpdrun',
                 'conhost'        : myHost,
                 'spawned'        : 0,
                 'nstarted'       : 0,
                 'hosts'          : {},
                 'execs'          : {},
                 'users'          : {},
                 'cwds'           : {},
                 'umasks'         : {},
                 'paths'          : {},
                 'args'           : {},
                 'limits'         : {},

                 'gl_envvars'     : {},
                 'envvars'        : {},

                 'envall'         : {},

                 'envexcl'        : {},

                 'ifhns'          : {},
               }

    if parmdb['inXmlFilename']:
        get_parms_from_xml_file(msgToMPD)  # fills in some more values of msgToMPD
    else:
        parmdb.get_parms_from_env(parmsToOverride)
        parmdb.get_parms_from_rcfile(parmsToOverride)

    # mostly old mpdrun below here
    numDoneWithIO = 0
    outXmlDoc = ''
    outECs = ''
    outECFile = None
    sigOccurred = 0

    listenSock = mpdlib.MPDListenSock('',0,name='socket_to_listen_for_man')
    recvTimeout = int(parmdb['MPIEXEC_RECV_TIMEOUT'])  # may be changed below

    listenPort = listenSock.getsockname()[1]
    if (hasattr(os,'getuid')  and  os.getuid() == 0)  or  parmdb['MPD_USE_ROOT_MPD']:
        fullDirName = os.path.abspath(os.path.split(sys.argv[0])[0])  # normalize
        mpdroot = os.path.join(fullDirName,'mpdroot')
        conSock = mpdlib.MPDConClientSock(mpdroot=mpdroot,secretword=parmdb['MPD_SECRETWORD'])
    else:
        conSock = mpdlib.MPDConClientSock(secretword=parmdb['MPD_SECRETWORD'])


    if parmdb['-idba']:
        idb_attach(conSock, parmdb['-idba'])


    if parmdb['-tva']:
        tv_attach(conSock, parmdb['-tva'])    



    msgToSend = { 'cmd' : 'get_mpd_hostname' }
    conSock.send_dict_msg(msgToSend)
    msg = conSock.recv_dict_msg(timeout=recvTimeout)
    if not msg:

        mpdlib.mpd_print(1, 'no message received from the mpd daemon during hostname check. Please examine the /tmp/mpd2.logfile_%s log file on each node of the ring.' % (mpdlib.mpd_get_my_username()))

    elif msg['cmd'] == 'mpd_hostname_response':
        myHost = msg['mpd_hostname']
        msgToMPD['conhost'] = myHost
    msgToSend = { 'cmd' : 'get_mpd_ip' }
    conSock.send_dict_msg(msgToSend)
    msg = conSock.recv_dict_msg(timeout=recvTimeout)
    if not msg:

        mpdlib.mpd_print(1, 'no message received from the mpd daemon during IP check. Please examine the /tmp/mpd2.logfile_%s log file on each node of the ring.' % (mpdlib.mpd_get_my_username()))

    elif msg['cmd'] == 'mpd_ip_response':
        myIP = msg['mpd_ip']
    msgToMPD['conip'] = myIP

    if parmdb['MPIEXEC_HOST_CHECK']:    # if this was requested in the xml file
        msgToSend = { 'cmd' : 'verify_hosts_in_ring',
                      'host_list' : parmdb['MPIEXEC_HOST_LIST'] }
        conSock.send_dict_msg(msgToSend)
        msg = conSock.recv_dict_msg(timeout=recvTimeout)
        if not msg:

            mpdlib.mpd_print(1,'no message received from the mpd daemon for the verify_host_in_ring request. Please examine the /tmp/mpd2.logfile_%s log file on each node of the ring.' % (mpdlib.mpd_get_my_username()))

            sys.exit(-1)
        elif msg['cmd'] != 'verify_hosts_in_ring_response':
            mpdlib.mpd_print(1,'unexpected msg from mpd :%s:' % (msg) )
            sys.exit(-1)
        if msg['host_list']:
            print 'These hosts are not in the mpd ring:'
            for host in  msg['host_list']:
                if host[0].isdigit():
                    print '    %s' % (host),
                    try:
                        print ' (%s)' % (socket.gethostbyaddr(host)[0])
                    except:
                        print ''
                else:
                    print '    %s' % (host)
            sys.exit(-1)

    msgToSend = { 'cmd' : 'get_mpdrun_values' }
    conSock.send_dict_msg(msgToSend)
    msg = conSock.recv_dict_msg(timeout=recvTimeout)
    if not msg:

        if not os.environ.has_key('I_MPI_TRY_20_STARTUP') or os.environ['I_MPI_TRY_20_STARTUP'].lower() not in ["1", "on", "yes", "enable"]:
            mpdlib.mpd_print(1, 'no msg recvd from mpd during version check. MPD ring is broken or you use old version of mpd.py')
            sys.exit(-1)
        else:

            print "Warning! You are trying to run your task built with Intel MPI 3.0 over early version of the mpd."
            searchedPgm = "mpd.py"
            try:
                os.stat(conSock.conFilename)
            except:
                is_my_mpd = 0
            else:
                is_my_mpd = 1

            if is_my_mpd:
                (shellIn, shellOut) = os.popen4("/bin/ps ux | grep %s | grep -v grep" % searchedPgm)
            else:
                (shellIn, shellOut) = os.popen4("/bin/ps aux | grep root | grep %s" % searchedPgm)

            fullLine = shellOut.readline()
            if fullLine:
                tlist = fullLine.split()
            else:
                print "Path to early mpiexec hasn't been found!\n"
                sys.exit(-1)

            for phrase in tlist:
                rv = phrase.find(searchedPgm)
                if rv > 0:
                    break
            old_mpiexec_path = phrase[:(rv-1)] + ":"
            old_mpiexec_args = sys.argv[:]
            old_mpiexec_args[0] = "mpiexec"
            os.environ['PATH'] = old_mpiexec_path + os.environ['PATH']
            try:
                os.execvpe("mpiexec", old_mpiexec_args, os.environ)
            except Exception, errmsg:
                mpdlib.mpd_print(1,'execvpe failed for running old mpiexec; errmsg=:%s:' % (errmsg) )
                sys.exit(-1)

    elif msg['cmd'] != 'response_get_mpdrun_values':
        mpdlib.mpd_print(1,'unexpected message from mpd :%s:' % (msg) )
        sys.exit(-1)
    if msg['mpd_version'] != mpdlib.mpd_version():
        mpdlib.mpd_print(1,'mpd version %s does not match mpiexec version %s' % \
                  (msg['mpd_version'],mpdlib.mpd_version()) )
        sys.exit(-1)
    # if using/testing the INET CONSOLE
    if os.environ.has_key('MPD_CON_INET_HOST_PORT'):
        try:
            myIfhn = socket.gethostbyname_ex(myHost)[2][0]

        except Exception, errmsg:
            print 'mpiexec failed: gethostbyname_ex failed for %s: %s' % (myHost,errmsg)

            sys.exit(-1)
        parmdb[('thispgm','MPIEXEC_IFHN')] = myIfhn
    elif not parmdb['MPIEXEC_IFHN']:    # if user did not specify one, use mpd's
        parmdb[('thispgm','MPIEXEC_IFHN')] = msg['mpd_ifhn']    # not really thispgm here


    if parmdb['-gdba']:

        gl_envToSend = {}

        get_vals_for_attach(parmdb, conSock, msgToMPD)
#    if parmdb['gdb_attach_jobid']:
#        get_vals_for_attach(parmdb,conSock,msgToMPD)

    elif not parmdb['inXmlFilename']:
        parmdb[('cmdline','nprocs')] = 0  # for incr later


        invalidGenvItems = [
            'I_MPI_JOB_TIMEOUT',
            'I_MPI_PMI_FAST_STARTUP',
            'I_MPI_JOB_FAST_STARTUP',
            'I_MPI_JOB_CHECK_LIBS',
            'I_MPI_JOB_TRACE_LIBS',
            'I_MPI_JOB_TIMEOUT_SIGNAL',
            'I_MPI_JOB_SIGNAL_PROPAGATION',

            'I_MPI_JOB_ABORT_SIGNAL',

            'I_MPI_OUTPUT_CHUNK_SIZE',
            'MPIEXEC_TIMEOUT',
            'MPIEXEC_OUTPUT_CHUNK_SIZE',
            'MPIEXEC_TRACE_LIBS'
            ]
        for k in parmdb['-genv'].keys():
            if k in invalidGenvItems:
                print 'Warning: %s doesn\'t work when listed in the -genv list. Please set it as an external environment variable.' % (k)




#        if parmdb['-genvlist']:
#            parmdb[('cmdline','-genvlist')] = parmdb['-genvlist'].split(',')


        msgToMPD['paths']['global'] = parmdb['-gpath']
        msgToMPD['cwds']['global'] = parmdb['-gwdir']


        for k in localArgSets.keys():
            handle_local_argset(localArgSets[k],machineFileInfo,msgToMPD)


        gl_envToSend = {}

        if not parmdb['-genvnone']:
            for envvar in os.environ.keys():

                if not (re.search('[^'+printable+']', os.environ[envvar])) and (envvar not in parmdb['-genvexcl']):

                    gl_envToSend[envvar] = os.environ[envvar]

        for envvar in parmdb['-genvlist']:
            if not os.environ.has_key(envvar):
                print '%s in envlist does not exist in your env' % (envvar)
                sys.exit(-1)
            if not (re.search('[^'+printable+']', os.environ[envvar])):
                gl_envToSend[envvar] = os.environ[envvar]
        msgToMPD['genvuser'] = parmdb['-genvuser']


        for envvar in parmdb['-genv'].keys():
            gl_envToSend[envvar] = parmdb['-genv'][envvar]


        if parmdb['MPIEXEC_LDPRELOAD']:
            linkage = 0 # 1 - static, 2 - dynamic, -1 - conflict between exec linkage methods
            for exec_name in msgToMPD['execs'].values():

                (shellIn, shellOut) = os.popen4("/usr/bin/file %s | egrep \" text\"" % (exec_name))
                outLine = shellOut.readline()
                if not outLine: # is binary executable

                    retCode = os.system("/usr/bin/ldd %s > /dev/null 2>&1" % (exec_name))


                    if retCode == 0:

                        if (linkage == 0) or (linkage == 2):
                            linkage = 2
                        else:
                            linkage = -1
                            break
                    else:
                        if (linkage == 0) or (linkage == 1):
                            linkage = 1
                        else:
                            linkage = -1
                            break

                else:
                    linkage = 2


            if linkage == 2:

                if not gl_envToSend.has_key('LD_PRELOAD') or not gl_envToSend['LD_PRELOAD']:
                    gl_envToSend['LD_PRELOAD'] = parmdb['MPIEXEC_LDPRELOAD']
                elif 'libmpi.so' in gl_envToSend['LD_PRELOAD'] or 'libmpi_dbg.so' in gl_envToSend['LD_PRELOAD']:
                    gl_envToSend['LD_PRELOAD'] = '%s %s' % (parmdb['MPIEXEC_LDPRELOAD'], gl_envToSend['LD_PRELOAD'])
                else:
                    gl_envToSend['LD_PRELOAD'] += ' %s' % (parmdb['MPIEXEC_LDPRELOAD'])

                msgToMPD['mpd_output_chunk_size'] = 64 * 1024
                gl_envToSend['MPDMAN_OUTPUT_CHUNK_SIZE'] = '64'
            elif linkage == 1:
                mpdlib.mpd_print(1, 'Warning: your application is statically linked. The library(-ies) for preloading will NOT be applied!')
            else:
                mpdlib.mpd_print(1, 'Warning: your application executable linking methods conflict with each other (mixing of static and dynamic ones). The library(-ies) for preloading will NOT be applied!')


        if parmdb['MPIEXEC_ORDERED_OUTPUT'] or (os.environ.has_key('I_MPI_ORDERED_OUTPUT') and (os.environ['I_MPI_ORDERED_OUTPUT'] in ['1', 'enable', 'yes', 'on'])):
            msgToMPD['ordered_output'] = 1


        msgToMPD['gl_envvars'] = gl_envToSend


    if parmdb['MPIEXEC_MERGE_OUTPUT']  and  not parmdb['MPIEXEC_SHOW_LINE_LABELS']:
        parmdb[('thispgm','MPIEXEC_SHOW_LINE_LABELS')] = 1   # causes line labels also

    if parmdb['print_parmdb_all']:
        parmdb.printall()
    if parmdb['print_parmdb_def']:
        parmdb.printdef()

    if parmdb['mship']:
        mshipSock = mpdlib.MPDListenSock('',0,name='socket_for_mship')
        mshipPort = mshipSock.getsockname()[1]
        mshipPid = os.fork()
        if mshipPid == 0:
            conSock.close()
            os.environ['MPDCP_AM_MSHIP'] = '1'
            os.environ['MPDCP_MSHIP_PORT'] = str(mshipPort)
            os.environ['MPDCP_MSHIP_FD'] = str(mshipSock.fileno())
            os.environ['MPDCP_MSHIP_NPROCS'] = str(parmdb['nprocs'])
            try:
                os.execvpe(parmdb['mship'],[parmdb['MPIEXEC_MSHIP']],os.environ)
            except Exception, errmsg:

                mpdlib.mpd_print(1,'execvpe failed for program %s; errmsg=:%s:' % \
                          (parmdb['MPIEXEC_MSHIP'],errmsg))

                sys.exit(-1)
            os._exit(0);  # do NOT do cleanup
        mshipSock.close()
    else:
        mshipPid = 0

    # make sure to do this after nprocs has its value
    linesPerRank = {}  # keep this a dict instead of a list
    for i in range(parmdb['nprocs']):
        linesPerRank[i] = []
    # make sure to do this after nprocs has its value
    if recvTimeout == recvTimeoutDefault:  # still the default
        recvTimeoutMultiplier = 0.1
        if os.environ.has_key('MPD_RECVTIMEOUT_MULTIPLIER'):
            try:
                recvTimeoutMultiplier = int(os.environ ['MPD_RECVTIMEOUT_MULTIPLIER'])
            except ValueError:
                try:
                    recvTimeoutMultiplier = float(os.environ ['MPD_RECVTIMEOUT_MULTIPLIER'])
                except ValueError:
                    print 'Invalid MPD_RECVTIMEOUT_MULTIPLIER. Value must be a number.'
                    sys.exit(-1)

        if (int(parmdb['nprocs']) > 200) :
            recvTimeout = int(parmdb['nprocs']) * recvTimeoutMultiplier



    if os.environ.has_key('I_MPI_JOB_STARTUP_TIMEOUT'):
        try:
            recvTimeoutMPI = int(os.environ['I_MPI_JOB_STARTUP_TIMEOUT'])
        except ValueError:
            print 'I_MPI_JOB_STARTUP_TIMEOUT=%s but it should be numerical. The default value (%d) will be used.' % (os.environ['I_MPI_JOB_STARTUP_TIMEOUT'], recvTimeout)
        else:
            if recvTimeoutMPI > 0:
                recvTimeout = recvTimeoutMPI
            else:
                print 'I_MPI_JOB_STARTUP_TIMEOUT=%d, but it should be positive. The default value (%d) will be used.' % (recvTimeoutMPI, recvTimeout)


    if parmdb['MPIEXEC_EXITCODES_FILENAME']:
        if parmdb['ecfn_format'] == 'xml':
            try:
                import xml.dom.minidom
            except:
                print 'you requested to save the exit codes in an xml file, but'
                print '  I was unable to import the xml.dom.minidom module'
                sys.exit(-1)
            outXmlDoc = xml.dom.minidom.Document()
            outECs = outXmlDoc.createElement('exit-codes')
            outXmlDoc.appendChild(outECs)
        else:
            outECs = 'exit-codes\n'

    msgToMPD['nprocs'] = parmdb['nprocs']
    msgToMPD['limits'][(0,parmdb['nprocs']-1)]  = {}
    msgToMPD['conport'] = listenPort
    msgToMPD['conip'] = myIP
    msgToMPD['conifhn'] = parmdb['MPIEXEC_IFHN']
    if parmdb['MPIEXEC_JOB_ALIAS']:
        msgToMPD['jobalias'] = parmdb['MPIEXEC_JOB_ALIAS']
    else:
        msgToMPD['jobalias'] = ''
    if parmdb['MPIEXEC_TRY_1ST_LOCALLY']:
        msgToMPD['try_1st_locally'] = 1

    chunk_size_str = ''
    if os.environ.has_key('MPIEXEC_OUTPUT_CHUNK_SIZE'):
        chunk_size_str = os.environ['MPIEXEC_OUTPUT_CHUNK_SIZE']
    if os.environ.has_key('I_MPI_OUTPUT_CHUNK_SIZE'):
        chunk_size_str = os.environ['I_MPI_OUTPUT_CHUNK_SIZE']

    if chunk_size_str:
        try:
            chunk_size=int(chunk_size_str)
        except:
            print 'incorrect value of I_MPI_OUTPUT_CHUNK_SIZE %s, should be int' % (chunk_size_str)
            sys.exit(-1)
        if chunk_size <= 0:
            print 'incorrect value of I_MPI_OUTPUT_CHUNK_SIZE %s, should be positive' % (chunk_size_str)
            sys.exit(-1)
        gl_envToSend['MPDMAN_OUTPUT_CHUNK_SIZE'] = chunk_size_str
        msgToMPD['mpd_output_chunk_size'] = chunk_size * 1024

    if parmdb['MPIEXEC_NOLOCAL']:
        msgToMPD['nolocal'] = 1

    if parmdb['MPIEXEC_PERHOST']:

        msgToMPD['perhost'] = parmdb['MPIEXEC_PERHOST']


    msgToMPD['job_fast_startup'] = 1
    if os.environ.has_key('I_MPI_PMI_FAST_STARTUP') and os.environ['I_MPI_PMI_FAST_STARTUP'].lower() in ["0", "off", "no", "disable"]:
        msgToMPD['job_fast_startup'] = 0

    if os.environ.has_key('I_MPI_JOB_FAST_STARTUP'):
        if os.environ['I_MPI_JOB_FAST_STARTUP'].lower() in ["0", "off", "no", "disable"]:
            msgToMPD['job_fast_startup'] = 0
        else:
            msgToMPD['job_fast_startup'] = 1


    msgToMPD['job_abort_signal'] = 9 # SIGKILL by default
    if os.environ.has_key('I_MPI_JOB_ABORT_SIGNAL'):
        sig_found = 0
        signo = int(os.environ['I_MPI_JOB_ABORT_SIGNAL'])
        for (key, value) in signal.__dict__.items():
            if value == signo:
                sig_found = 1
                msgToMPD['job_abort_signal'] = signo
                break
        if not sig_found:
            mpdlib.mpd_print(1, 'warning: the value of I_MPI_JOB_ABORT_SIGNAL is %d, but this number is not supported. The default signal number will be used.' % (signo))

    if parmdb['rship']:
        msgToMPD['rship'] = parmdb['rship']
        msgToMPD['mship_host'] = socket.gethostname()
        msgToMPD['mship_port'] = mshipPort
    if parmdb['MPIEXEC_BNR']:
        msgToMPD['doing_bnr'] = 1
    if parmdb['MPIEXEC_STDIN_DEST'] == 'all':
        stdinDest = '0-%d' % (parmdb['nprocs']-1)
    else:
        stdinDest = parmdb['MPIEXEC_STDIN_DEST']
    if parmdb['MPIEXEC_SHOW_LINE_LABELS']:
        gl_envToSend['MPDMAN_LINE_LABELS_FMT'] = parmdb['MPIEXEC_LINE_LABEL_FMT']
        msgToMPD['line_labels'] = parmdb['MPIEXEC_LINE_LABEL_FMT']
    else:
        msgToMPD['line_labels'] = ''
    msgToMPD['stdin_dest'] = stdinDest
    msgToMPD['gdb'] = parmdb['MPIEXEC_GDB']
    msgToMPD['gdba'] = parmdb['-gdba']
    msgToMPD['totalview'] = parmdb['MPIEXEC_TOTALVIEW']
    msgToMPD['singinitpid'] = parmdb['singinitpid']
    msgToMPD['singinitport'] = parmdb['singinitport']
    msgToMPD['host_spec_pool'] = parmdb['MPIEXEC_HOST_LIST']

    # set sig handlers up right before we send mpdrun msg to mpd
    if hasattr(signal,'SIGINT'):
        signal.signal(signal.SIGINT, sig_handler)
    if hasattr(signal,'SIGTSTP'):
        signal.signal(signal.SIGTSTP,sig_handler)
    if hasattr(signal,'SIGCONT'):
        signal.signal(signal.SIGCONT,sig_handler)
    if hasattr(signal,'SIGALRM'):
        signal.signal(signal.SIGALRM,sig_handler)
    if hasattr(signal,'SIGTERM'):
        signal.signal(signal.SIGTERM,sig_handler)

    conSock.send_dict_msg(msgToMPD)
    msg = conSock.recv_dict_msg(timeout=recvTimeout)
    if not msg:

        mpdlib.mpd_print(1, 'no msg recvd from mpd when expecting ack of request. Please examine the /tmp/mpd2.logfile_%s log file on each node of the ring.' % (mpdlib.mpd_get_my_username()))

        sys.exit(-1)
    elif msg['cmd'] == 'mpdrun_ack':
        currRingSize = msg['ringsize']
        currRingNCPUs = msg['ring_ncpus']
    else:
        if msg['cmd'] == 'already_have_a_console':
            print 'mpd already has a console (e.g. for long ringtest); try later'
            sys.exit(-1)
        elif msg['cmd'] == 'job_failed':
            if  msg['reason'] == 'some_procs_not_started':
                if parmdb['MPIEXEC_NOLOCAL'] == 1:
                    print 'mpiexec: unable to use -nolocal for mpd ring with size 1'
                else :
                    print 'mpiexec: unable to start all procs; may have invalid machine names'
                    print '    remaining specified hosts:'
                    for host in msg['remaining_hosts'].values():
                        if host != '_any_':
                            try:
                                print '        %s (%s)' % (host,socket.gethostbyaddr(host)[0])
                            except:
                                print '        %s' % (host)
            elif  msg['reason'] == 'invalid_username':
                print 'mpiexec: invalid username %s at host %s' % \
                      (msg['username'],msg['host'])
            else:
                print 'mpiexec: job failed; reason=:%s:' % (msg['reason'])
            sys.exit(-1)
        else:
            mpdlib.mpd_print(1, 'unexpected message from mpd: %s' % (msg) )
            sys.exit(-1)
    conSock.close()
    jobTimeout = int(parmdb['MPIEXEC_TIMEOUT'])
    if parmdb['I_MPI_JOB_TIMEOUT']:
        jobTimeout = int(parmdb['I_MPI_JOB_TIMEOUT'])    
    if jobTimeout:
        if hasattr(signal,'alarm'):
            signal.alarm(jobTimeout)
        else:
            def timeout_function():
                mpdlib.mpd_print(1,'job ending due to env var MPIEXEC_TIMEOUT=%d' % jobTimeout)
                thread.interrupt_main()
            try:
                import thread, threading
                timer = threading.Timer(jobTimeout,timeout_function)
                timer.start()
            except:
                print 'unable to establish timeout for MPIEXEC_TIMEOUT'

    streamHandler = mpdlib.MPDStreamHandler()

    (manSock,addr) = listenSock.accept()
    if not manSock:

        mpdlib.mpd_print(1, 'failed to obtain sock from the process manager (mpdman daemon). Please examine the /tmp/mpd2.logfile_%s log file on each node of the ring.' % (mpdlib.mpd_get_my_username()))

        sys.exit(-1)
    streamHandler.set_handler(manSock,handle_man_input,args=(streamHandler,))
    if hasattr(os,'fork'):
        streamHandler.set_handler(sys.stdin,handle_stdin_input,
                                  args=(parmdb,streamHandler,manSock))
    else:  # not using select on fd's when using subprocess module (probably M$)
        import threading
        def read_fd_with_func(fd,func):
            line = 'x'
            while line:
                line = func(fd)
        stdin_thread = threading.Thread(target=read_fd_with_func,
                                        args=(sys.stdin.fileno(),handle_stdin_input))
    # first, do handshaking with man
    msg = manSock.recv_dict_msg()
    if (not msg  or  not msg.has_key('cmd') or msg['cmd'] != 'man_checking_in'):

        mpdlib.mpd_print(1, 'invalid message from the process manager (mpdman) :%s: Please examine the /tmp/mpd2.logfile_%s log file on each node of the ring.' % (msg, mpdlib.mpd_get_my_username()))

        sys.exit(-1)
    msgToSend = { 'cmd' : 'ringsize', 'ring_ncpus' : currRingNCPUs,
                  'ringsize' : currRingSize }
    manSock.send_dict_msg(msgToSend)
    msg = manSock.recv_dict_msg()
    if (not msg  or  not msg.has_key('cmd')):

        mpdlib.mpd_print(1, 'invalid message from the process manager (mpdman) :%s: Please examine the /tmp/mpd2.logfile_%s log file on each node of the ring.' % (msg, mpdlib.mpd_get_my_username()))

        sys.exit(-1)
    if (msg['cmd'] == 'job_started'):
        jobid = msg['jobid']
        if outECs:
            if parmdb['ecfn_format'] == 'xml':
                outECs.setAttribute('jobid',jobid.strip())
            else:
                outECs += 'jobid=%s\n' % (jobid.strip())
        # print 'mpiexec: job %s started' % (jobid)
        if parmdb['MPIEXEC_TVSU']:
            import mtv
            mtv.allocate_proctable(parmdb['nprocs'])
            # extract procinfo (rank,hostname,exec,pid) tuples from msg
            for i in range(parmdb['nprocs']):
                tvhost = msg['procinfo'][i][0]
                tvpgm  = msg['procinfo'][i][1]
                tvpid  = msg['procinfo'][i][2]
                # print "%d %s %s %d" % (i,host,pgm,pid)
                mtv.append_proctable_entry(tvhost,tvpgm,tvpid)
            mtv.complete_spawn()
            msgToSend = { 'cmd' : 'tv_ready' }
            manSock.send_dict_msg(msgToSend)
#        if parmdb['MPIEXEC_TOTALVIEW']:
        elif parmdb['MPIEXEC_TOTALVIEW']:
            if not parmdb['MPIEXEC_IDB']:

                if os.environ.has_key('TOTALVIEW'):
                    tv_exe = os.environ['TOTALVIEW']
                else:
                    tv_exe = 'totalview'
                tv_cmd = 'dattach python ' + `os.getpid()` + '; dgo; dassign MPIR_being_debugged 1'
                dbg_cmd = tv_exe + ' -e ' + '"' + tv_cmd + '"' + '&'
            else:
                tv_exe = 'idb'
                dbg_cmd = 'xterm -e ' + tv_exe + ' -pid ' + `os.getpid()` + ' -mpi2 -parallel /usr/bin/python &'
            if tv_exe.count('/'):
               if not os.access(tv_exe,os.X_OK):
                   print 'cannot find executable "%s"' % (tv_exe)
                   myExitStatus = -1  # used in main
                   sys.exit(myExitStatus) # really forces jump back into main
            elif not mpdlib.mpd_which(tv_exe):
                print 'cannot find "%s" in your $PATH:' % (tv_exe)
                print '    ', os.environ['PATH']
                myExitStatus = -1  # used in main
                sys.exit(myExitStatus) # really forces jump back into main


            pattmp = re.compile(r'..-bit')
            dir_path = os.path.abspath(os.path.split(sys.argv[0])[0])
            # Checking Python for the arch
            (shellIn, shellOut) = os.popen4('/usr/bin/file -L %s' % (sys.executable))
            shellLine = shellOut.readline()
            shellLine = shellLine.strip()
            ws = re.search(pattmp, shellLine)
            python_type = ''
            if ws:
                python_type = ws.group()
            # Checking mtv.so for the arch
            (shellIn, shellOut) = os.popen4('/usr/bin/file -L %s' % (os.path.join(dir_path, 'mtv.so')))
            shellLine = shellOut.readline()
            shellLine = shellLine.strip()
            ws = re.search(pattmp, shellLine)
            mtv_type = ''
            if ws:
                mtv_type = ws.group()
            need_repath = 0
            if python_type and mtv_type and python_type != mtv_type:
                if python_type == '32-bit':
                    new_dir = os.path.join(sysfullDirName, 'bin')
                    if os.path.exists(new_dir):
                        need_repath = 1
                        sys.path.insert(0, new_dir)
                elif python_type == '64-bit':
                    new_dir = os.path.join(sysfullDirName, 'bin64')
                    if os.path.exists(new_dir):
                        need_repath = 1
                        sys.path.insert(0, new_dir)
            import mtv
            if need_repath:
                sys.path = sys.path[1:]

            os.system(dbg_cmd)
            mtv.wait_for_debugger()
            mtv.allocate_proctable(parmdb['nprocs'])
            # extract procinfo (rank,hostname,exec,pid) tuples from msg
            for i in range(parmdb['nprocs']):
                tvhost = msg['procinfo'][i][0]
                tvpgm  = msg['procinfo'][i][1]
                tvpid  = msg['procinfo'][i][2]
                # print "%d %s %s %d" % (i,host,pgm,pid)
                mtv.append_proctable_entry(tvhost,tvpgm,tvpid)
            mtv.complete_spawn()
            msgToSend = { 'cmd' : 'tv_ready' }
            manSock.send_dict_msg(msgToSend)
    else:

        mpdlib.mpd_print(1, 'unknown message from the process manager (mpdman) :%s:' % (msg) )

        sys.exit(-1)

    (manCliStdoutSock,addr) = listenSock.accept()
    streamHandler.set_handler(manCliStdoutSock,
                              handle_cli_stdout_input,
                              args=(parmdb,streamHandler,linesPerRank,))
    (manCliStderrSock,addr) = listenSock.accept()
    streamHandler.set_handler(manCliStderrSock,
                              handle_cli_stderr_input,
                              args=(streamHandler,))

    # Main Loop
    timeDelayForPrints = 2  # seconds
    timeForPrint = time() + timeDelayForPrints   # to get started
    numDoneWithIO = 0
    while numDoneWithIO < 3:    # man, client stdout, and client stderr
        if sigOccurred:
            handle_sig_occurred(manSock)
        rv = streamHandler.handle_active_streams(timeout=1.0)
        if rv[0] < 0:  # will handle some sigs at top of next loop
            pass       # may have to handle some err conditions here
        if parmdb['MPIEXEC_MERGE_OUTPUT']:
            if timeForPrint < time():
                print_ready_merged_lines(1,parmdb,linesPerRank)
                timeForPrint = time() + timeDelayForPrints
            else:
                print_ready_merged_lines(parmdb['nprocs'],parmdb,linesPerRank)

    if parmdb['MPIEXEC_MERGE_OUTPUT']:
        print_ready_merged_lines(1,parmdb,linesPerRank)
    if mshipPid:
        (donePid,status) = os.wait()    # os.waitpid(mshipPid,0)
    if parmdb['MPIEXEC_EXITCODES_FILENAME']:
        outECFile = open(parmdb['MPIEXEC_EXITCODES_FILENAME'],'w')
        if parmdb['ecfn_format'] == 'xml':
            print >>outECFile, outXmlDoc.toprettyxml(indent='   ')
        else:
            print >>outECFile, outECs,
        outECFile.close()
    return myExitStatus


def collect_args(args,localArgSets):
    validGlobalArgs = { '-l' : 0, '-usize' : 1, '-gdb' : 0, '-bnr' : 0, '-tv' : 0,
                        '-idb' : 0, '-ifhn' : 1, '-machinefile' : 1, '-s' : 1, '-1' : 0,
                        '-a' : 1, '-m' : 0, '-ecfn' : 1, '-recvtimeout' : 1,
                        '-gn' : 1, '-gnp' : 1, '-ghost' : 1, '-gpath' : 1, '-gwdir' : 1,
                        '-gsoft' : 1, '-garch' : 1, '-gexec' : 1, '-gumask' : 1,
                        '-genvall' : 0, '-genv' : 2, '-genvnone' : 0,
                        '-genvlist' : 1, '-nolocal' : 0, '-perhost' : 1,

                        '-genvuser' : 0, '-genvexcl' : 1,


                        '-ilp64' : 0,


                        '-trace' : -1,
                        '-t'     : -1,


                        '-tvsu'  : 0,


                        '-check' : -1,
                        '-check_mpi' : -1,


                        '-rr' : 0, '-grr' : 0, '-ppn' : 0,


                        '-tune' : 0,
                        '-noconf' : 0,


                        '-rdma' : 0,
                        '-RDMA' : 0,
                        '-dapl' : 0,
                        '-DAPL' : 0,
                        '-gm' : 0,
                        '-GM' : 0,
                        '-mx' : 0,
                        '-MX' : 0,


                        '-ib' : 0,
                        '-IB' : 0,

                        '-tmi' : 0,
                        '-TMI' : 0,
                        '-psm' : 0,
                        '-PSM' : 0,


                        '-ordered-output' : 0}

    currumask = os.umask(0) ; os.umask(currumask)  # grab it and set it back
    parmdb[('cmdline','-gn')]          = 1
    parmdb[('cmdline','-ghost')]       = '_any_'
    if os.environ.has_key('PATH'):
        parmdb[('cmdline','-gpath')]   = os.environ['PATH']
    else:
        parmdb[('cmdline','-gpath')]   =  ''
    parmdb[('cmdline','-gwdir')]       = os.path.abspath(os.getcwd())
    parmdb[('cmdline','-gumask')]      = str(currumask)
    parmdb[('cmdline','-gsoft')]       = 0
    parmdb[('cmdline','-garch')]       = ''
    parmdb[('cmdline','-gexec')]       = ''
    parmdb[('cmdline','-genv')]        = {}
    parmdb[('cmdline','-genvlist')]    = []
    parmdb[('cmdline','-genvnone')]    = 0

    parmdb[('cmdline','-genvuser')]    = 1
    parmdb[('cmdline','-genvexcl')]    = []

    argidx = 1
    while argidx < len(args)  and  args[argidx] in validGlobalArgs.keys():
        garg = args[argidx]

        if validGlobalArgs[garg] > -1:

            if len(args) <= (argidx+validGlobalArgs[garg]):
                print "missing sub-arg to %s" % (garg)
                usage()
        if garg == '-genv':
            parmdb['-genv'][args[argidx+1]] = args[argidx+2]
            argidx += 3

        elif garg == '-tune':
            # do nothing here; everything has been done before
            if argidx + 1 < len(args) and not args[argidx + 1].startswith("-"):
                argidx += 2
            else:
                argidx += 1
        elif garg == '-noconf':
            argidx += 1 # do nothing here; everything has been done before

        elif garg == '-gn'  or  garg == '-gnp':
            if args[argidx+1].isdigit():
                parmdb[('cmdline','-gn')] = int(args[argidx+1])
            else:
                print 'argument to %s must be numeric' % (garg)
                usage()
            argidx += 2
        elif garg == '-ghost':
            try:
                parmdb[('cmdline',garg)] = socket.gethostbyname_ex(args[argidx+1])[2][0]

            except Exception, errmsg:
                print 'unable to do find info for host %s: %s' % (args[argidx+1],errmsg)

                sys.exit(-1)
            argidx += 2
        elif garg == '-gpath':
            parmdb[('cmdline','-gpath')] = args[argidx+1]
            argidx += 2
        elif garg == '-gwdir':
            parmdb[('cmdline','-gwdir')] = args[argidx+1]
            argidx += 2
        elif garg == '-gumask':
            parmdb[('cmdline','-gumask')] = args[argidx+1]
            argidx += 2
        elif garg == '-gsoft':
            parmdb[('cmdline','-gsoft')] = args[argidx+1]
            argidx += 2
        elif garg == '-garch':
            parmdb[('cmdline','-garch')] = args[argidx+1]
            argidx += 2
            print '-garch is accepted but not used'
        elif garg == '-gexec':
            parmdb[('cmdline','-gexec')] = args[argidx+1]
            argidx += 2
        elif garg == '-genv':
            parmdb[('cmdline','-genv')] = args[argidx+1]
            argidx += 2
        elif garg == '-genvlist':

            if parmdb['-genvlist']:
                tmp_list = parmdb['-genvlist']
                tmp_add_list = args[argidx+1].split(',')
                for l in tmp_list:
                    for a in tmp_add_list:
                        if l != a:
                            tmp_list.append(a)
                            parmdb[('cmdline','-genvlist')] = tmp_list
            else:
                tmp_add_list = args[argidx+1].split(',')
                add_list = []
                for a in tmp_add_list:
                    if a not in add_list:
                        add_list.append(a)
                parmdb[('cmdline','-genvlist')] = add_list
            if parmdb['-genvexcl']:
                old_excl = parmdb['-genvexcl'][:]
                for e in old_excl:
                    for l in parmdb['-genvlist']:
                        if e == l:
                            tmp_excl = parmdb['-genvexcl']
                            tmp_excl.remove(l)
                            parmdb[('cmdline','-genvexcl')] = tmp_excl

            argidx += 2
        elif garg == '-genvnone':

            parmdb[('cmdline','-genvnone')] = 1
            parmdb[('cmdline','-genvuser')] = 0

            argidx += 1

        elif garg == '-genvall':
            parmdb[('cmdline','-genvnone')] = 0
            parmdb[('cmdline','-genvuser')] = 0
            argidx += 1
        elif garg == '-genvuser':
            parmdb[('cmdline','-genvuser')] = 1
            argidx += 1
        elif garg == '-genvexcl':
            if parmdb['-genvexcl']:
                tmp_excl = parmdb['-genvexcl']
                tmp_add_excl = args[argidx+1].split(',')
                for e in tmp_excl:
                    for a in tmp_add_excl:
                        if e != a:
                            tmp_excl.append(a)
                            parmdb[('cmdline','-genvexcl')] = tmp_excl
            else:
                tmp_add_excl = args[argidx+1].split(',')
                add_excl = []
                for a in tmp_add_excl:
                    if a not in add_excl:
                        add_excl.append(a)
                parmdb[('cmdline','-genvexcl')] = add_excl
            if parmdb['-genvlist']:
                old_list = parmdb['-genvlist'][:]
                for l in old_list:
                    for e in parmdb['-genvexcl']:
                        if e == l:
                            tmp_list = parmdb['-genvlist']
                            tmp_list.remove(l)
                            parmdb[('cmdline','-genvlist')] = tmp_list
            argidx += 2

        elif garg == '-l':
            parmdb[('cmdline','MPIEXEC_SHOW_LINE_LABELS')] = 1
            argidx += 1
        elif garg == '-a':
            parmdb[('cmdline','MPIEXEC_JOB_ALIAS')] = args[argidx+1]
            argidx += 2
        elif garg == '-usize':
            if args[argidx+1].isdigit():
                parmdb[('cmdline','MPIEXEC_USIZE')] = int(args[argidx+1])
            else:
                print 'argument to %s must be numeric' % (garg)
                usage()
            argidx += 2


        elif garg == '-perhost' or garg == '-grr' or garg == '-ppn':

            if args[argidx+1].isdigit():
                parmdb[('cmdline','MPIEXEC_PERHOST')] = int(args[argidx+1])
            else:
                print 'argument to %s must be numeric' % (garg)
                usage()
            argidx += 2
        elif garg == '-nolocal':
            parmdb[('cmdline','MPIEXEC_NOLOCAL')] = 1
            argidx += 1


        elif garg == '-rr':
            parmdb[('cmdline','MPIEXEC_PERHOST')] = 1
            argidx += 1

        elif garg == '-recvtimeout':
            if args[argidx+1].isdigit():
                parmdb[('cmdline','MPIEXEC_RECV_TIMEOUT')] = int(args[argidx+1])
            else:
                print 'argument to %s must be numeric' % (garg)
                usage()
            argidx += 2
        elif garg == '-gdb':
            parmdb[('cmdline','MPIEXEC_GDB')] = 1
            argidx += 1
            parmdb[('cmdline','MPIEXEC_MERGE_OUTPUT')] = 1       # implied
            parmdb[('cmdline','MPIEXEC_SHOW_LINE_LABELS')] = 1   # implied
            parmdb[('cmdline','MPIEXEC_STDIN_DEST')]   = 'all'   # implied
        elif garg == '-ifhn':
            parmdb[('cmdline','MPIEXEC_IFHN')] = args[argidx+1]
            argidx += 2
            try:
                hostinfo = socket.gethostbyname_ex(parmdb['MPIEXEC_IFHN'])

            except Exception, errmsg:
                print 'mpiexec: gethostbyname_ex failed for host (ifhn) %s: %s' % (parmdb['MPIEXEC_IFHN'],errmsg)

                sys.exit(-1)
        elif garg == '-m':
            parmdb[('cmdline','MPIEXEC_MERGE_OUTPUT')] = 1
            argidx += 1
        elif garg == '-s':
            parmdb[('cmdline','MPIEXEC_STDIN_DEST')] = args[argidx+1]
            argidx += 2
        elif garg == '-machinefile':
            parmdb[('cmdline','MPIEXEC_MACHINEFILE')] = args[argidx+1]
            argidx += 2
        elif garg == '-bnr':
            parmdb[('cmdline','MPIEXEC_BNR')] = 1
            argidx += 1
        elif garg == '-tv':
            parmdb[('cmdline','MPIEXEC_TOTALVIEW')] = 1
            argidx += 1
        elif garg == '-tvsu':
            parmdb[('cmdline','MPIEXEC_TOTALVIEW')] = 1
            parmdb[('cmdline','MPIEXEC_TVSU')] = 1
            argidx += 1

        elif garg == '-idb':
            parmdb[('cmdline','MPIEXEC_IDB')] = 1
            parmdb[('cmdline','MPIEXEC_TOTALVIEW')] = 1
            argidx += 1

        elif garg == '-ecfn':
            parmdb[('cmdline','MPIEXEC_EXITCODES_FILENAME')] = args[argidx+1]
            argidx += 2
        elif garg == '-1':
            parmdb[('cmdline','MPIEXEC_TRY_1ST_LOCALLY')] = 0  # reverses meaning
            argidx += 1

        elif garg == '-ilp64':

            if parmdb['MPIEXEC_LDPRELOAD']:
                print 'Warning: -ilp64 does not work with -trace and -check_mpi for now. -ilp64 will be used'

            parmdb[('cmdline', 'MPIEXEC_LDPRELOAD')] = 'libmpi_ilp64.so'
            argidx += 1


        elif garg == '-trace' or garg == '-t':

            if parmdb['MPIEXEC_LDPRELOAD']:
                print 'Warning: -trace and -check_mpi can not be used simultaneously. -trace will be used.'

            pattern = re.compile(r'^[-:]')

            if not re.search(pattern, args[argidx+1]) and argidx+2 < len(args):

                parmdb[('cmdline', 'MPIEXEC_LDPRELOAD')] = args[argidx+1]
                argidx += 2
            elif os.environ.has_key('I_MPI_JOB_TRACE_LIBS'):
                parmdb[('cmdline', 'MPIEXEC_LDPRELOAD')] = os.environ['I_MPI_JOB_TRACE_LIBS']
                argidx += 1
            elif os.environ.has_key('MPIEXEC_TRACE_LIBS'):
                parmdb[('cmdline', 'MPIEXEC_LDPRELOAD')] = os.environ['MPIEXEC_TRACE_LIBS']
                argidx += 1
            else:
                parmdb[('cmdline', 'MPIEXEC_LDPRELOAD')] = 'libVT.so'
                argidx += 1


        elif garg == '-check' or garg == '-check_mpi':
            if parmdb['MPIEXEC_LDPRELOAD']:
                print 'Warning: -trace and -check_mpi can not be used simultaneously. -check_mpi will be used.'
            pattern = re.compile(r'^[-:]')

            if not re.search(pattern, args[argidx+1]) and argidx+2 < len(args):

                parmdb[('cmdline', 'MPIEXEC_LDPRELOAD')] = args[argidx+1]
                argidx += 2

            elif os.environ.has_key('I_MPI_JOB_CHECK_LIBS'):
                parmdb[('cmdline', 'MPIEXEC_LDPRELOAD')] = os.environ['I_MPI_JOB_CHECK_LIBS']
                argidx += 1

            else:
                parmdb[('cmdline', 'MPIEXEC_LDPRELOAD')] = 'libVTmc.so'
                argidx += 1


        elif garg == '-ordered-output':
            parmdb[('cmdline', 'MPIEXEC_ORDERED_OUTPUT')] = 1
            argidx += 1



        elif garg == '-rdma':
            parmdb['-genv']['I_MPI_FABRICS_LIST'] = 'dapl,ofa,tcp,tmi'
            argidx += 1
        elif garg == '-RDMA':
            parmdb['-genv']['I_MPI_FABRICS_LIST'] = 'dapl,ofa'
            argidx += 1
        elif garg == '-dapl':
            parmdb['-genv']['I_MPI_FABRICS_LIST'] = 'dapl,tcp,tmi,ofa'
            argidx += 1
        elif garg == '-DAPL':
            parmdb['-genv']['I_MPI_FABRICS_LIST'] = 'dapl'
            parmdb['-genv']['I_MPI_FALLBACK'] = '0'
            argidx += 1
        elif garg == '-gm':
            parmdb['-genv']['I_MPI_DEVICE'] = 'rdma:GmHca0'
            parmdb['-genv']['I_MPI_FALLBACK_DEVICE'] = '1'
            argidx += 1
        elif garg == '-GM':
            parmdb['-genv']['I_MPI_DEVICE'] = 'rdma:GmHca0'
            parmdb['-genv']['I_MPI_FALLBACK_DEVICE'] = '0'
            argidx += 1
        elif garg == '-mx':
            parmdb['-genv']['I_MPI_FABRICS_LIST'] = 'tmi,dapl,tcp,ofa'
            parmdb['-genv']['I_MPI_TMI_PROVIDER'] = 'mx'
            argidx += 1
        elif garg == '-MX':
            parmdb['-genv']['I_MPI_FABRICS_LIST'] = 'tmi'
            parmdb['-genv']['I_MPI_TMI_PROVIDER'] = 'mx'
            parmdb['-genv']['I_MPI_FALLBACK'] = '0'
            argidx += 1


        elif garg == '-ib':
            parmdb['-genv']['I_MPI_FABRICS_LIST'] = 'ofa,dapl,tcp,tmi'
            argidx += 1
        elif garg == '-IB':
            parmdb['-genv']['I_MPI_FABRICS_LIST'] = 'ofa'
            parmdb['-genv']['I_MPI_FALLBACK'] = '0'
            argidx += 1

        elif garg == '-tmi':
            parmdb['-genv']['I_MPI_FABRICS_LIST'] = 'tmi,dapl,tcp,ofa'
            argidx += 1
        elif garg == '-TMI':
            parmdb['-genv']['I_MPI_FABRICS_LIST'] = 'tmi'
            parmdb['-genv']['I_MPI_FALLBACK'] = '0'
            argidx += 1
        elif garg == '-psm':
            parmdb['-genv']['I_MPI_FABRICS_LIST'] = 'tmi,dapl,tcp,ofa'
            parmdb['-genv']['I_MPI_TMI_PROVIDER'] = 'psm'
            argidx += 1
        elif garg == '-PSM':
            parmdb['-genv']['I_MPI_FABRICS_LIST'] = 'tmi'
            parmdb['-genv']['I_MPI_TMI_PROVIDER'] = 'psm'
            parmdb['-genv']['I_MPI_FALLBACK'] = '0'
            argidx += 1

    if args[argidx] == ':':
        argidx += 1
    localArgsKey = 0
    # collect local arg sets but do not validate them until handled below
    while argidx < len(args):
        if args[argidx] == ':':
            localArgsKey += 1
            localArgSets[localArgsKey] = []
        else:
            localArgSets[localArgsKey].append(args[argidx])
        argidx += 1

def handle_local_argset(argset,machineFileInfo,msgToMPD):
    global parmdb, nextRange, appnum, recvTimeout
    validLocalArgs  = { '-n' : 1, '-np' : 1, '-host' : 1, '-path' : 1, '-wdir' : 1,
                        '-soft' : 1, '-arch' : 1, '-umask' : 1,
                        '-envall' : 0, '-env' : 2, '-envnone' : 0, '-envlist' : 1,

                        '-envuser' : 0, '-envexcl' : 1,

    
                        '-V' : 0, '-version' : 0 }
    
    host   = parmdb['-ghost']

    host_option = 0


#    wdir   = parmdb['-gwdir']
    wdir = ''

    wumask = parmdb['-gumask']

#    wpath  = parmdb['-gpath']
    wpath = ''

    nProcs = parmdb['-gn']
    usize  = parmdb['MPIEXEC_USIZE']
    gexec  = parmdb['-gexec']
    softness =  parmdb['-gsoft']

    envall = 1


#    if parmdb['-genvlist']:
#        parmdb[('cmdline','-genvlist')] = parmdb['-genvlist'].split(',')

    localEnvlist = []

    localExclList = []
    envuser = 0
    envnone = 0

    localEnv  = {}

    argidx = 0
    while argidx < len(argset):
        if argset[argidx] not in validLocalArgs:
            if argset[argidx][0] == '-':
                print 'invalid "local" arg: %s' % argset[argidx]
                usage()
            break                       # since now at executable
        if parmdb['MPIEXEC_MACHINEFILE']:
            if argset[argidx] == '-host'  or  argset[argidx] == ['-ghost']:
                print '-host (or -ghost) and -machinefile are incompatible'
                sys.exit(-1)

        if parmdb['MPIEXEC_PERHOST']:
            if argset[argidx] == '-host'  or  argset[argidx] == ['-ghost']:
                print '-host (or -ghost) and -perhost are incompatible'
                sys.exit(-1)

        if argset[argidx] == '-n' or argset[argidx] == '-np':
            if len(argset) < (argidx+2):

                print 'missing arg to -n option'

                usage()
            nProcs = argset[argidx+1]
            if not nProcs.isdigit():

                print 'non-numeric arg to -n option: %s' % nProcs

                usage()
            nProcs = int(nProcs)
            argidx += 2
        elif argset[argidx] == '-host':

            host_option = 1

            if len(argset) < (argidx+2):

                print 'missing arg to -host option'

                usage()

            host = argset[argidx+1]

            argidx += 2
        elif argset[argidx] == '-path':
            if len(argset) < (argidx+2):

                print 'missing arg to -path option'

                usage()
            wpath = argset[argidx+1]
            argidx += 2
        elif argset[argidx] == '-wdir':
            if len(argset) < (argidx+2):

                print 'missing arg to -wdir option'

                usage()
            wdir = argset[argidx+1]
            argidx += 2
        elif argset[argidx] == '-umask':
            if len(argset) < (argidx+2):

                print 'missing arg to -umask option'

                usage()
            wumask = argset[argidx+1]
            argidx += 2
        elif argset[argidx] == '-soft':
            if len(argset) < (argidx+2):

                print 'missing arg to -soft option'

                usage()
            softness = argset[argidx+1]
            argidx += 2
        elif argset[argidx] == '-arch':
            if len(argset) < (argidx+2):

                print 'missing arg to -arch option'

                usage()
            print '-arch is accepted but not used'
            argidx += 2
        elif argset[argidx] == '-envall':

            envall = 2

            argidx += 1
        elif argset[argidx] == '-envnone':
            envall = 0
            argidx += 1
        elif argset[argidx] == '-envlist':

            if localEnvlist:
                tmp_add_list = argset[argidx+1].split(',')
                for l in localEnvlist:
                    for a in tmp_add_list:
                        if l != a:
                            localEnvlist.append(a)
            else:
                tmp_add_list = argset[argidx+1].split(',')
                for a in tmp_add_list:
                    if a not in localEnvlist:
                        localEnvlist.append(a)
            if localExclList:
                old_excl = localExclList[:]
                for e in old_excl:
                    for l in localEnvlist:
                        if e == l:
                            localExclList.remove(e)

            argidx += 2

        elif argset[argidx] == '-envuser':
            envall = 3
            envuser = 1
            argidx += 1
        elif argset[argidx] == '-envexcl':
            if localExclList:
                tmp_add_excl = argset[argidx+1].split(',')
                for e in localExclList:
                    for a in tmp_add_excl:
                        if e != a:
                            localExclList.append(a)
            else:
                tmp_add_excl = argset[argidx+1].split(',')
                for a in tmp_add_excl:
                    if a not in localExclList:
                        localExclList.append(a)
            if localEnvlist:
                old_list = localEnvlist[:]
                for l in old_list:
                    for e in localExclList:
                        if e == l:
                            localEnvlist.remove(l)
            argidx += 2

        elif argset[argidx] == '-env':
            if len(argset) < (argidx+3):

                print 'missing arg to -env option'

                usage()
            var = argset[argidx+1]
            val = argset[argidx+2]
            localEnv[var] = val
            argidx += 3
    
        elif argset[argidx] == '-V' or argset[argidx] == '-version':


            argidx += 1
    
        else:
            print 'unknown "local" option: %s' % argset[argidx]
            usage()

    if softness:
        nProcs = adjust_nprocs(nProcs,softness)

    cmdAndArgs = []
    if argidx < len(argset):
        while argidx < len(argset):
            cmdAndArgs.append(argset[argidx])
            argidx += 1
    else:
        if gexec:
            cmdAndArgs = [gexec]
    if not cmdAndArgs:
        print 'mpiexec: no cmd specified; for help type "mpiexec -help"'
    
        sys.exit(-1);
    
        usage()

    argsetLoRange = nextRange
    argsetHiRange = nextRange + nProcs - 1
    loRange = argsetLoRange
    hiRange = argsetHiRange

    defaultHostForArgset = host
    while loRange <= argsetHiRange:
        host = defaultHostForArgset
        if machineFileInfo:
            if len(machineFileInfo) <= hiRange:
                print 'too few entries in machinefile'
                sys.exit(-1)
            host = machineFileInfo[loRange]['host']
            ifhn = machineFileInfo[loRange]['ifhn']
            if ifhn:
                msgToMPD['ifhns'][loRange] = ifhn
            for i in range(loRange+1,hiRange+1):
                if machineFileInfo[i]['host'] != host  or  machineFileInfo[i]['ifhn'] != ifhn:
                    hiRange = i - 1
                    break

        asRange = (loRange,hiRange)  # this argset range as a tuple

        msgToMPD['users'][asRange]  = mpdlib.mpd_get_my_username()
        msgToMPD['execs'][asRange]  = cmdAndArgs[0]

        if wpath:
            msgToMPD['paths'][asRange]  = wpath
        if wdir:
            msgToMPD['cwds'][asRange]   = wdir

        msgToMPD['umasks'][asRange] = wumask
        msgToMPD['args'][asRange]   = cmdAndArgs[1:]
        if host.startswith('_any_'):
            msgToMPD['hosts'][(loRange,hiRange)] = host
        else:

            try:
               hostip = socket.gethostbyname_ex(host)[2][0]

            except Exception, errmsg:
                print 'unable to do find info for host %s: %s' % (host,errmsg)

                sys.exit(-1)

            if hostip.startswith('127.0.0'):

                msgToMPD['hosts'][(loRange,hiRange)] = msgToMPD['conip']
            else:
                msgToMPD['hosts'][(loRange,hiRange)] = hostip

#            msgToMPD['hosts'][asRange] = host

        envToSend = {}

        if envall:
            msgToMPD['envall'][(loRange,hiRange)] = envall
        else:
            msgToMPD['envall'][(loRange,hiRange)] = 0



        if envall > 1 and parmdb['-genvnone']:
            for envvar in os.environ.keys():
                if not (re.search('[^'+printable+']', os.environ[envvar])) and (envvar not in localExclList):
                    envToSend[envvar] = os.environ[envvar]
        if localExclList and not parmdb['-genvnone']:
            msgToMPD['envexcl'][(loRange,hiRange)] = localExclList


#        for envvar in parmdb['-genvlist']:
#            if not os.environ.has_key(envvar):
#                print '%s in envlist does not exist in your env' % (envvar)
#                sys.exit(-1)
#            if not (re.search('[^'+printable+']', os.environ[envvar])):
#                envToSend[envvar] = os.environ[envvar]

        for envvar in localEnvlist:
            if not os.environ.has_key(envvar):
                print '%s in envlist does not exist in your env' % (envvar)
                sys.exit(-1)
            if not (re.search('[^'+printable+']', os.environ[envvar])):
                envToSend[envvar] = os.environ[envvar]

#        for envvar in parmdb['-genv'].keys():
#            envToSend[envvar] = parmdb['-genv'][envvar]

        for envvar in localEnv.keys():
            envToSend[envvar] = localEnv[envvar]


        if parmdb['-genv'].has_key('I_MPI_PERHOST'):
            impiperhost = parmdb['-genv']['I_MPI_PERHOST']

        elif os.environ.has_key('I_MPI_PERHOST'):
            impiperhost = os.environ['I_MPI_PERHOST']
        else:
            impiperhost = 'allcores'

        if host_option and impiperhost:
#            print '-host and I_MPI_PERHOST are incompatible'
            impiperhost = ''

        if impiperhost:
            msgToMPD['impiperhost'] = impiperhost            

        if usize:
            envToSend['MPI_UNIVERSE_SIZE'] = str(usize)
        envToSend['MPI_APPNUM'] = str(appnum)
        msgToMPD['envvars'][(loRange,hiRange)] = envToSend

        loRange = hiRange + 1
        hiRange = argsetHiRange  # again

    appnum += 1
    nextRange += nProcs
    parmdb[('cmdline','nprocs')] = parmdb['nprocs'] + nProcs

# Adjust nProcs (called maxprocs in the Standard) according to soft:
# Our interpretation is that we need the largest number <= nProcs that is
# consistent with the list of possible values described by soft.  I.e.
# if the user says
#
#   mpiexec -n 10 -soft 5 a.out
#
# we adjust the 10 down to 5.  This may not be what was intended in the Standard,
# but it seems to be what it says.

def adjust_nprocs(nProcs,softness):
    biglist = []
    list1 = softness.split(',')
    for triple in list1:                # triple is a or a:b or a:b:c
        thingy = triple.split(':')
        if len(thingy) == 1:
            a = int(thingy[0])
            if a <= nProcs and a >= 0:
                biglist.append(a)
        elif len(thingy) == 2:
            a = int(thingy[0])
            b = int(thingy[1])
            for i in range(a,b+1):
                if i <= nProcs and i >= 0:
                    biglist.append(i)
        elif len(thingy) == 3:
            a = int(thingy[0])
            b = int(thingy[1])
            c = int(thingy[2])
            for i in range(a,b+1,c):
                if i <= nProcs and i >= 0:
                    biglist.append(i)
        else:
            print 'invalid subargument to -soft: %s' % (softness)
            print 'should be a or a:b or a:b:c'
            usage()

        if len(biglist) == 0:
            print '-soft argument %s allows no valid number of processes' % (softness)
            usage()
        else:
            return max(biglist)


def read_machinefile(machineFilename):
    if not machineFilename:
        return None
    try:
        machineFile = open(machineFilename,'r')
    except:

        print 'unable to open machinefile %s' % (machineFilename)

        sys.exit(-1)
    procID = 0
    machineFileInfo = {}
    for line in machineFile:
        line = line.strip()
        if not line  or  line[0] == '#':
            continue
        splitLine = re.split(r'\s+',line)
        host = splitLine[0]
        if ':' in host:
            (host,nprocs) = host.split(':',1)
            nprocs = int(nprocs)
        else:
            nprocs = 1
        kvps = {'ifhn' : ''}
        for kv in splitLine[1:]:
            (k,v) = kv.split('=',1)
            if k == 'ifhn':  # interface hostname
                kvps[k] = v
            else:  # may be other kv pairs later
                print 'unrecognized key in machinefile:', k
                sys.exit(-1)
        for i in range(procID,procID+nprocs):
            machineFileInfo[i] = { 'host' : host, 'nprocs' : nprocs }
            machineFileInfo[i].update(kvps)
        procID += nprocs
    return machineFileInfo

def handle_man_input(sock,streamHandler):
    global numDoneWithIO, myExitStatus
    global outXmlDoc, outECs
    msg = sock.recv_dict_msg()
    if not msg:
        streamHandler.del_handler(sock)
        numDoneWithIO += 1
    elif not msg.has_key('cmd'):

        mpdlib.mpd_print(1,'invalid message from the process manager (mpdman) :%s:' % (msg) )

        sys.exit(-1)
    elif msg['cmd'] == 'startup_status':
        if msg['rc'] != 0:
            # print 'rank %d (%s) in job %s failed to find executable %s' % \
                  # ( msg['rank'], msg['src'], msg['jobid'], msg['exec'] )
            host = msg['src'].split('_')[0]
            reason = unquote(msg['reason'])
            print 'problem with execution of %s  on  %s:  %s ' % \
                  (msg['exec'],host,reason)

            myExitStatus=-1

            # don't stop ; keep going until all top-level mans finish
    elif msg['cmd'] == 'job_aborted_early':
        print 'rank %d in job %s caused collective abort of all ranks' % \
              ( msg['rank'], msg['jobid'] )
        status = msg['exit_status']
        if hasattr(os,'WIFSIGNALED')  and  os.WIFSIGNALED(status):

            if status > myExitStatus and status <> 0:

                myExitStatus = status
            killed_status = status & 0x007f  # AND off core flag
            print '  exit status of rank %d: killed by signal %d ' % \
                  (msg['rank'],killed_status)
        elif hasattr(os,'WEXITSTATUS'):
            exit_status = os.WEXITSTATUS(status)

            if exit_status > myExitStatus and status <> 0:

                myExitStatus = exit_status
            print '  exit status of rank %d: return code %d ' % \
                  (msg['rank'],exit_status)
        else:
            myExitStatus = 0
    elif msg['cmd'] == 'job_aborted':
        print 'job aborted; reason = %s' % (msg['reason'])
    elif msg['cmd'] == 'client_exit_status':
        if outECs:
            if parmdb['ecfn_format'] == 'xml':
                outXmlProc = outXmlDoc.createElement('exit-code')
                outECs.appendChild(outXmlProc)
                outXmlProc.setAttribute('rank',str(msg['cli_rank']))
                outXmlProc.setAttribute('status',str(msg['cli_status']))
                outXmlProc.setAttribute('pid',str(msg['cli_pid']))
                outXmlProc.setAttribute('host',msg['cli_host'])  # cli_ifhn is also avail
            else:
                outECs += 'rank=%d status=%d pid=%d host=%s\n' % \
                          (msg['cli_rank'],msg['cli_status'],msg['cli_pid'],msg['cli_host'])

        # print "exit info: rank=%d  host=%s  pid=%d  status=%d" % \
              # (msg['cli_rank'],msg['cli_host'],
               # msg['cli_pid'],msg['cli_status'])
        status = msg['cli_status']
        if hasattr(os,'WIFSIGNALED')  and  os.WIFSIGNALED(status):

            if status > myExitStatus and status <> 0:

                myExitStatus = status
            killed_status = status & 0x007f  # AND off core flag
            # print 'exit status of rank %d: killed by signal %d ' % \
            #        (msg['cli_rank'],killed_status)
        elif hasattr(os,'WEXITSTATUS'):
            exit_status = os.WEXITSTATUS(status)

            if exit_status > myExitStatus and status <> 0:

                myExitStatus = exit_status
            # print 'exit status of rank %d: return code %d ' % \
            #       (msg['cli_rank'],exit_status)
        else:
            myExitStatus = 0
    else:
        print 'unrecognized msg from manager :%s:' % msg

def handle_cli_stdout_input(sock,parmdb,streamHandler,linesPerRank):
    global numDoneWithIO
    if parmdb['MPIEXEC_MERGE_OUTPUT']:
        line = sock.recv_one_line()
        if not line:
            streamHandler.del_handler(sock)
            numDoneWithIO += 1
        else:
            if parmdb['MPIEXEC_GDB']:
                line = line.replace('(gdb)\n','(gdb) ')
            try:
                (rank,rest) = line.split(':',1)
                rank = int(rank)
                linesPerRank[rank].append(rest)
            except:
                print line
            print_ready_merged_lines(parmdb['nprocs'],parmdb,linesPerRank)
    else:
        msg = sock.recv(1024)
        if not msg:
            streamHandler.del_handler(sock)
            numDoneWithIO += 1
        else:
            sys.stdout.write(msg)
            sys.stdout.flush()

def handle_cli_stderr_input(sock,streamHandler):
    global numDoneWithIO
    msg = sock.recv(1024)
    if not msg:
        streamHandler.del_handler(sock)
        numDoneWithIO += 1
    else:
        sys.stderr.write(msg)
        sys.stderr.flush()

# NOTE: stdin is supposed to be slow, low-volume.  We read it all here (as it
# appears on the fd) and send it immediately to the receivers.  If the user
# redirects a "large" file (perhaps as small as 5k) into us, we will send it
# all out right away.  This can cause things to hang on the remote (recvr) side.
# We do not wait to read here until the recvrs read because there may be several
# recvrs and they may read at different speeds/times.
def handle_stdin_input(stdin_stream,parmdb,streamHandler,manSock):
    line  = ''
    try:
        line = stdin_stream.readline()
    except IOError, errinfo:
        sys.stdin.flush()  # probably does nothing

        if errinfo[0] == errno.EBADF:
            streamHandler.del_handler(sys.stdin)
            sys.stdin.close()

#       else:
        # print "I/O err on stdin:", errinfo
#           mpdlib.mpd_print(1,'stdin problem; if pgm is run in background, redirect from /dev/null')


    else:
        gdbFlag = parmdb['MPIEXEC_GDB']
        if line:    # not EOF
            msgToSend = { 'cmd' : 'stdin_from_user', 'line' : line } # default
            if gdbFlag and line.startswith('z'):
                line = line.rstrip()
                if len(line) < 3:    # just a 'z'
                    line += ' 0-%d' % (parmdb['nprocs']-1)
                s1 = line[2:].rstrip().split(',')
                for s in s1:
                    s2 = s.split('-')
                    for i in s2:
                        if not i.isdigit():
                            print 'invalid arg to z :%s:' % i
                            continue
                msgToSend = { 'cmd' : 'stdin_dest', 'stdin_procs' : line[2:] }
                sys.stdout.softspace = 0
                print '%s:  (gdb) ' % (line[2:]),
            elif gdbFlag and line.startswith('q'):
                msgToSend = { 'cmd' : 'stdin_dest',
                              'stdin_procs' : '0-%d' % (parmdb['nprocs']-1) }
                if manSock:
                    manSock.send_dict_msg(msgToSend)
                msgToSend = { 'cmd' : 'stdin_from_user','line' : 'q\n' }
            elif gdbFlag and line.startswith('^'):
                msgToSend = { 'cmd' : 'stdin_dest',
                              'stdin_procs' : '0-%d' % (parmdb['nprocs']-1) }
                if manSock:
                    manSock.send_dict_msg(msgToSend)
                msgToSend = { 'cmd' : 'signal', 'signo' : 'SIGINT' }
            if manSock:
                manSock.send_dict_msg(msgToSend)
        else:
            streamHandler.del_handler(sys.stdin)
            sys.stdin.close()
            if manSock:
                msgToSend = { 'cmd' : 'stdin_from_user', 'eof' : '' }
                manSock.send_dict_msg(msgToSend)
    return line

def handle_sig_occurred(manSock):
    global sigOccurred


    propagation = 'no'
    if os.environ.has_key('MPIEXEC_SIGNAL_PROPAGATION'):
        if os.environ['MPIEXEC_SIGNAL_PROPAGATION'] in ['1', 'on', 'yes', 'enable']:
            propagation = 'yes'
    if os.environ.has_key('I_MPI_JOB_SIGNAL_PROPAGATION'):
        if os.environ['I_MPI_JOB_SIGNAL_PROPAGATION'] in ['1', 'on', 'yes', 'enable']:
            propagation = 'yes'
        else:
            propagation = 'no'


    if sigOccurred != signal.SIGALRM and sigOccurred != signal.SIGTSTP and sigOccurred != signal.SIGCONT:
        if manSock:
            msgToSend = { 'cmd' : 'signal', 'signo' : 'SIGKILL' }
            sig_found = 0
            for (key, value) in signal.__dict__.items():
                if value == sigOccurred:
                    msgToSend['signo'] = key
                    sig_found = 1
                    break
            msgToSend['propagation'] = propagation
            manSock.send_dict_msg(msgToSend)
            if propagation == 'no':
                manSock.close()
        sigOccurred = 0
        if propagation == 'no':
            sys.exit(-1)
    elif sigOccurred == signal.SIGALRM:
        if manSock:
            msgToSend = { 'cmd' : 'signal', 'signo' : 'SIGKILL' }

            sig_found = -1
            if os.environ.has_key('MPIEXEC_TIMEOUT_SIGNAL'):
                signo = int(os.environ['MPIEXEC_TIMEOUT_SIGNAL'])
                sig_found = 0
            if os.environ.has_key('I_MPI_JOB_TIMEOUT_SIGNAL'):
                signo = int(os.environ['I_MPI_JOB_TIMEOUT_SIGNAL'])
                sig_found = 0
            if not sig_found:
                for (key, value) in signal.__dict__.items():
                    if value == signo:
                        msgToSend['signo'] = key
                        sig_found = 1
                        break
                if not sig_found:
                    mpdlib.mpd_print(1, 'warning: the value of TIMEOUT SIGNAL is %d, but this number is not supported. The default signal number will be used.' % (signo))
            msgToSend['propagation'] = propagation

            manSock.send_dict_msg(msgToSend)
            if propagation == 'no':
                manSock.close()
        if os.environ.has_key('I_MPI_JOB_TIMEOUT'):
            mpdlib.mpd_print(1,'job ending due to env var I_MPI_JOB_TIMEOUT=%s' % os.environ['I_MPI_JOB_TIMEOUT'])
        elif os.environ.has_key('MPIEXEC_TIMEOUT'):
            mpdlib.mpd_print(1,'job ending due to env var MPIEXEC_TIMEOUT=%s' % os.environ['MPIEXEC_TIMEOUT'])
        sigOccurred = 0
        if propagation == 'no':
            sys.exit(-1)
    elif sigOccurred == signal.SIGTSTP:
        sigOccurred = 0  # do this before kill below
        if manSock:
            msgToSend = { 'cmd' : 'signal', 'signo' : 'SIGTSTP' }
            manSock.send_dict_msg(msgToSend)
        signal.signal(signal.SIGTSTP,signal.SIG_DFL)      # stop myself
        os.kill(os.getpid(),signal.SIGTSTP)
        signal.signal(signal.SIGTSTP,sig_handler)  # restore this handler
    elif sigOccurred == signal.SIGCONT:
        sigOccurred = 0  # do it before handling
        if manSock:
            msgToSend = { 'cmd' : 'signal', 'signo' : 'SIGCONT' }
            manSock.send_dict_msg(msgToSend)

def sig_handler(signum,frame):
    global sigOccurred
    sigOccurred = signum
    mpdlib.mpd_handle_signal(signum,frame)

def format_sorted_ranks(ranks):
    all = []
    one = []
    prevRank = -999
    for i in range(len(ranks)):
        if i != 0  and  ranks[i] != (prevRank+1):
            all.append(one)
            one = []
        one.append(ranks[i])
        if i == (len(ranks)-1):
            all.append(one)
        prevRank = ranks[i]
    pline = ''
    for i in range(len(all)):
        if len(all[i]) > 1:
            pline += '%d-%d' % (all[i][0],all[i][-1])
        else:
            pline += '%d' % (all[i][0])
        if i != (len(all)-1):
            pline += ','
    return pline

def print_ready_merged_lines(minRanks,parmdb,linesPerRank):
    printFlag = 1  # default to get started
    while printFlag:
        printFlag = 0
        for r1 in range(parmdb['nprocs']):
            if not linesPerRank[r1]:
                continue
            sortedRanks = []
            lineToPrint = linesPerRank[r1][0]
            for r2 in range(parmdb['nprocs']):
                if linesPerRank[r2] and linesPerRank[r2][0] == lineToPrint: # myself also
                    sortedRanks.append(r2)
            if len(sortedRanks) >= minRanks:
                fsr = format_sorted_ranks(sortedRanks)
                sys.stdout.softspace = 0
                print '%s: %s' % (fsr,lineToPrint),
                for r2 in sortedRanks:
                    linesPerRank[r2] = linesPerRank[r2][1:]
                printFlag = 1
    sys.stdout.flush()

def get_parms_from_xml_file(msgToMPD):
    global parmdb
    try:
        import xml.dom.minidom
    except:
        print 'you requested to parse an xml file, but'
        print '  I was unable to import the xml.dom.minidom module'
        sys.exit(-1)
    known_rlimit_types = ['core','cpu','fsize','data','stack','rss',
                          'nproc','nofile','ofile','memlock','as','vmem']
    try:
        inXmlFilename = parmdb['inXmlFilename']
        parmsXMLFile = open(inXmlFilename,'r')
    except:
        print 'could not open job xml specification file %s' % (inXmlFilename)
        sys.exit(-1)
    fileContents = parmsXMLFile.read()
    try:
        parsedXML = xml.dom.minidom.parseString(fileContents)
    except:
        print "mpiexec failed parsing xml file (perhaps from mpiexec); here is the content:"
        print fileContents
        sys.exit(-1)
    if parsedXML.documentElement.tagName != 'create-process-group':
        print 'expecting create-process-group; got unrecognized doctype: %s' % \
              (parsedXML.documentElement.tagName)
        sys.exit(-1)
    cpg = parsedXML.getElementsByTagName('create-process-group')[0]
    if cpg.hasAttribute('totalprocs'):
        parmdb[('xml','nprocs')] = int(cpg.getAttribute('totalprocs'))
    else:
        print 'totalprocs not specified in %s' % inXmlFilename
        sys.exit(-1)
    if cpg.hasAttribute('try_1st_locally'):
        parmdb[('xml','MPIEXEC_TRY_1ST_LOCALLY')] = int(cpg.getAttribute('try_1st_locally'))
    if cpg.hasAttribute('output')  and  cpg.getAttribute('output') == 'label':
        parmdb[('xml','MPIEXEC_SHOW_LINE_LABELS')] = 1
    if cpg.hasAttribute('pgid'):    # our jobalias
        parmdb[('xml','MPIEXEC_JOB_ALIAS')] = cpg.getAttribute('pgid')
    if cpg.hasAttribute('stdin_dest'):
        parmdb[('xml','MPIEXEC_STDIN_DEST')] = cpg.getAttribute('stdin_dest')
    if cpg.hasAttribute('doing_bnr'):
        parmdb[('xml','MPIEXEC_BNR')] = int(cpg.getAttribute('doing_bnr'))
    if cpg.hasAttribute('ifhn'):
        parmdb[('xml','MPIEXEC_IFHN')] = cpg.getAttribute('ifhn')
    if cpg.hasAttribute('exit_codes_filename'):
        parmdb[('xml','MPIEXEC_EXITCODES_FILENAME')] = cpg.getAttribute('exit_codes_filename')
        parmdb[('xml','ecfn_format')] = 'xml'
    if cpg.hasAttribute('gdb'):
        gdbFlag = int(cpg.getAttribute('gdb'))
        if gdbFlag:
            parmdb[('xml','MPIEXEC_GDB')]     = 1
            parmdb[('xml','MPIEXEC_MERGE_OUTPUT')] = 1       # implied
            parmdb[('xml','MPIEXEC_SHOW_LINE_LABELS')] = 1   # implied
            parmdb[('xml','MPIEXEC_STDIN_DEST')]   = 'all'   # implied
    if cpg.hasAttribute('use_root_pm'):
        parmdb[('xml','MPD_USE_ROOT_MPD')] = int(cpg.getAttribute('use_root_pm'))
    if cpg.hasAttribute('tv'):
        parmdb[('xml','MPIEXEC_TOTALVIEW')] = int(cpg.getAttribute('tv'))

    if cpg.hasAttribute('idb'):
        parmdb[('xml','MPIEXEC_IDB')] = int(cpg.getAttribute('idb'))
        parmdb[('xml','MPIEXEC_TOTALVIEW')] = int(cpg.getAttribute('idb'))

    hostSpec = cpg.getElementsByTagName('host-spec')
    if hostSpec:
        hostList = []
        for node in hostSpec[0].childNodes:
            node = node.data.strip()
            hostnames = re.findall(r'\S+',node)
            for hostname in hostnames:
                if hostname:    # some may be the empty string
                    try:
                        ipaddr = socket.gethostbyname_ex(hostname)[2][0]
                    except:
                        print 'unable to determine IP info for host %s' % (hostname)
                        sys.exit(-1)
                    hostList.append(ipaddr)
        parmdb[('xml','MPIEXEC_HOST_LIST')] = hostList
    if hostSpec and hostSpec[0].hasAttribute('check'):
        hostSpecMode = hostSpec[0].getAttribute('check')
        if hostSpecMode == 'yes':
            parmdb[('xml','MPIEXEC_HOST_CHECK')] = 1
    covered = [0] * parmdb['nprocs']
    procSpec = cpg.getElementsByTagName('process-spec')
    if not procSpec:
        print 'No process-spec specified'
        usage()
    for p in procSpec:
        if p.hasAttribute('range'):
            therange = p.getAttribute('range')
            splitRange = therange.split('-')
            if len(splitRange) == 1:
                loRange = int(splitRange[0])
                hiRange = loRange
            else:
                (loRange,hiRange) = (int(splitRange[0]),int(splitRange[1]))
        else:
            (loRange,hiRange) = (0,parmdb['nprocs']-1)
        for i in xrange(loRange,hiRange+1):
            nprocs = parmdb['nprocs']
            if i >= nprocs:
                print 'exiting; rank %d is greater than nprocs' % (nprocs)
                sys.exit(-1)
            if covered[i]:
                print 'exiting; rank %d is doubly used in proc specs' % (nprocs)
                sys.exit(-1)
            covered[i] = 1
        if p.hasAttribute('exec'):
            msgToMPD['execs'][(loRange,hiRange)] = p.getAttribute('exec')
        else:
            print 'exiting; range %d-%d has no exec' % (loRange,hiRange)
            sys.exit(-1)
        if p.hasAttribute('user'):
            username = p.getAttribute('user')
            if pwd_module_available:
                try:
                    pwent = pwd.getpwnam(username)
                except:
                    print username, 'is an invalid username'
                    sys.exit(-1)
            if username == mpdlib.mpd_get_my_username()  \
            or (hasattr(os,'getuid') and os.getuid() == 0):
                msgToMPD['users'][(loRange,hiRange)] = p.getAttribute('user')
            else:
                print username, 'username does not match yours and you are not root'
                sys.exit(-1)
        else:
            msgToMPD['users'][(loRange,hiRange)] = mpdlib.mpd_get_my_username()
        if p.hasAttribute('cwd'):
            msgToMPD['cwds'][(loRange,hiRange)] = p.getAttribute('cwd')
        else:
            msgToMPD['cwds'][(loRange,hiRange)] = os.path.abspath(os.getcwd())
        if p.hasAttribute('umask'):
            msgToMPD['umasks'][(loRange,hiRange)] = p.getAttribute('umask')
        else:
            currumask = os.umask(0) ; os.umask(currumask)
            msgToMPD['umasks'][(loRange,hiRange)] = str(currumask)
        if p.hasAttribute('path'):
            msgToMPD['paths'][(loRange,hiRange)] = p.getAttribute('path')
        else:
            msgToMPD['paths'][(loRange,hiRange)] = os.environ['PATH']
        if p.hasAttribute('host'):
            host = p.getAttribute('host')
            if host.startswith('_any_'):
                msgToMPD['hosts'][(loRange,hiRange)] = host
            else:
                try:
                    msgToMPD['hosts'][(loRange,hiRange)] = socket.gethostbyname_ex(host)[2][0]
                except:
                    print 'unable to do find info for host %s' % (host)
                    sys.exit(-1)
        else:
            if hostSpec  and  hostList:
                msgToMPD['hosts'][(loRange,hiRange)] = '_any_from_pool_'
            else:
                msgToMPD['hosts'][(loRange,hiRange)] = '_any_'
        argDict = {}
        argList = p.getElementsByTagName('arg')
        for argElem in argList:
            argDict[int(argElem.getAttribute('idx'))] = argElem.getAttribute('value')
        argVals = [0] * len(argList)
        for i in argDict.keys():
            argVals[i-1] = unquote(argDict[i])
        msgToMPD['args'][(loRange,hiRange)] = argVals
        limitDict = {}
        limitList = p.getElementsByTagName('limit')
        for limitElem in limitList:
            typ = limitElem.getAttribute('type')
            if typ in known_rlimit_types:
                limitDict[typ] = limitElem.getAttribute('value')
            else:
                print 'mpiexec: invalid type in limit: %s' % (typ)
                sys.exit(-1)
        msgToMPD['limits'][(loRange,hiRange)] = limitDict
        envVals = {}
        envVarList = p.getElementsByTagName('env')
        for envVarElem in envVarList:
            envkey = envVarElem.getAttribute('name')
            envval = unquote(envVarElem.getAttribute('value'))
            envVals[envkey] = envval
        msgToMPD['envvars'][(loRange,hiRange)] = envVals
    for i in range(len(covered)):
        if not covered[i]:
            print 'exiting; %d procs are requested, but proc %d is not described' % \
                  (parmdb['nprocs'],i)
            sys.exit(-1)

def get_vals_for_attach(parmdb,conSock,msgToMPD):
    global recvTimeout
    sjobid = parmdb['-gdba'].split('@')    # jobnum and originating host
    msgToSend = { 'cmd' : 'mpdlistjobs' }
    conSock.send_dict_msg(msgToSend)
    msg = conSock.recv_dict_msg(timeout=recvTimeout)
    if not msg:
        mpdlib.mpd_print(1,'no msg recvd from mpd before timeout')
        sys.exit(-1)
    if msg['cmd'] != 'local_mpdid':     # get full id of local mpd for filters later
        mpdlib.mpd_print(1,'did not receive local_mpdid message from local mpd; received: %s' % msg)
        sys.exit(-1)
    else:
        if len(sjobid) == 1:
            sjobid.append(msg['id'])
    got_info = 0
    while 1:
        msg = conSock.recv_dict_msg()
        if not msg.has_key('cmd'):
            mpdlib.mpd_print(1,'invalid message from mpd :%s:' % (msg))
            sys.exit(-1)
        if msg['cmd'] == 'mpdlistjobs_info':
            got_info = 1
            smjobid = msg['jobid'].split('  ')  # jobnum, mpdid, and alias (if present)
            if sjobid[0] == smjobid[0]  and  sjobid[1] == smjobid[1]:  # jobnum and mpdid
                rank = int(msg['rank'])
                msgToMPD['users'][(rank,rank)]   = msg['username']
                msgToMPD['hosts'][(rank,rank)]   = msg['ifhn']
                msgToMPD['execs'][(rank,rank)]   = msg['pgm']

                msgToMPD['cwds']['global']       = os.path.abspath(os.getcwd())
                msgToMPD['cwds'][(rank,rank)]    = os.path.abspath(os.getcwd()) # orig line
                msgToMPD['paths']['global']      = os.environ['PATH']
                msgToMPD['paths'][(rank,rank)]   = os.environ['PATH'] # orig line

                msgToMPD['args'][(rank,rank)]    = [msg['clipid']]
                msgToMPD['envvars'][(rank,rank)] = {}
                msgToMPD['limits'][(rank,rank)]  = {}
                currumask = os.umask(0) ; os.umask(currumask)  # grab it and set it back  
                msgToMPD['umasks'][(rank,rank)]  = str(currumask) 
        elif  msg['cmd'] == 'mpdlistjobs_trailer':
            if not got_info:
                print 'no info on this jobid; probably invalid'
                sys.exit(-1)
            break
        else:
            print 'invaild msg from mpd :%s:' % (msg)
            sys.exit(-1)
    parmdb[('thispgm','nprocs')] = len(msgToMPD['execs'].keys())  # all dicts are same len


def idb_attach (conSock, jobId):
    import mtv
    jobid    = ''
    sjobid   = ''

    pid = {}
    host = {}
    pgm = {}

    msgToSend = { 'cmd' : 'mpdlistjobs' }
    conSock.send_dict_msg(msgToSend)
    msg = conSock.recv_dict_msg(timeout=5.0)
    if not msg:
        mpdlib.mpd_print(1,'no message received from mpd before timeout 5.0 sec')
    if msg['cmd'] != 'local_mpdid':     # get full id of local mpd for filters later
        mpdlib.mpd_print(1,'did not recv local_mpdid msg from local mpd; instead, recvd: %s' % msg)
    else:
        if len(sjobid) == 1:
            sjobid.append(msg['id'])

    i = 0
    done = 0
    while not done:
        msg = conSock.recv_dict_msg()
        if not msg.has_key('cmd'):
            mpdlib.mpd_print(1,'mpdlistjobs: invalid msg=:%s:' % (msg) )
            sys.exit(-1)
        if msg['cmd'] == 'mpdlistjobs_info':
            smjobid = msg['jobid'].split('  ')  # jobnum, mpdid, and alias (if present)
            jobid = '%s@%s' % (smjobid[0],smjobid[1])
            if jobid == jobId:
                pid[i]  = msg['clipid']
                pgm[i]  = msg['pgm']
                host[i] = msg['host']
                i += 1
        else:  # mpdlistjobs_trailer
            done = 1
    nprocs = i
    if nprocs > 0:
        mtv.allocate_proctable(nprocs)
        for i in range(nprocs):
            mtv.append_proctable_entry(host[i],pgm[i],int(pid[i]))

        if not mpdlib.mpd_which('idb'):
            print 'cannot find "idb" in your $PATH:'
            print '    ', environ['PATH']
            myExitStatus = -1  # used in main
            sys.exit(myExitStatus) # really forces jump back into main
        idb_run = 'idb -pid ' + `os.getpid()` + ' -mpi2 -parallelattach /usr/bin/python '
        os.system(idb_run)
    else:
        print 'There is no MPI-2 application'
        conSock.close()
        sys.exit(-1)

    conSock.close()
    sys.exit(0)



def tv_attach (conSock, jobId):
    import mtv
    jobid    = ''
    sjobid   = ''

    pid = {}
    host = {}
    pgm = {}

    msgToSend = { 'cmd' : 'mpdlistjobs' }
    conSock.send_dict_msg(msgToSend)
    msg = conSock.recv_dict_msg(timeout=5.0)
    if not msg:
        mpdlib.mpd_print(1,'no message received from mpd before timeout 5.0 sec')
    if msg['cmd'] != 'local_mpdid':     # get full id of local mpd for filters later
        mpdlib.mpd_print(1,'did not recv local_mpdid msg from local mpd; instead, recvd: %s' % msg)
    else:
        if len(sjobid) == 1:
            sjobid.append(msg['id'])

    i = 0
    done = 0
    while not done:
        msg = conSock.recv_dict_msg()
        if not msg.has_key('cmd'):
            mpdlib.mpd_print(1,'mpdlistjobs: invalid msg=:%s:' % (msg) )
            sys.exit(-1)
        if msg['cmd'] == 'mpdlistjobs_info':
            smjobid = msg['jobid'].split('  ')  # jobnum, mpdid, and alias (if present)
            jobid = '%s@%s' % (smjobid[0],smjobid[1])
            if jobid == jobId:
                pid[i]  = msg['clipid']
                pgm[i]  = msg['pgm']
                host[i] = msg['host']
                i += 1
        else:  # mpdlistjobs_trailer
            done = 1
    nprocs = i
    if nprocs > 0:
        mtv.allocate_proctable(nprocs)
        for i in range(nprocs):
            mtv.append_proctable_entry(host[i],pgm[i],int(pid[i]))

        if os.environ.has_key('TOTALVIEW'):
            tv_exe = os.environ['TOTALVIEW']
        else:
            tv_exe = 'totalview'

        if not mpdlib.mpd_which(tv_exe):
            print 'cannot find %s in your $PATH:' % (tv_exe)
            print '    ', environ['PATH']
            myExitStatus = -1  # used in main
            sys.exit(myExitStatus) # really forces jump back into main
        tv_cmd = 'dattach python ' + `os.getpid()` + '; dgo; dassign MPIR_being_debugged 1'
        tv_run = tv_exe + ' -e ' + '"' + tv_cmd + '"'
        os.system(tv_run)
#        mtv.wait_for_debugger()
    else:
        print 'There is no MPI-2 application'
        conSock.close()
        sys.exit(-1)

    conSock.close()
    sys.exit(0)


def get_tuned_values(cmdline, rootconfline, confline, mpiinstalldir):
    newcmdline = []
# predefined values

    tuneconfdir = os.path.join(mpiinstalldir, 'etc')

    device = 'default'


#    validDeviceList = [ 'default', 'sock', 'ssm', 'shm', 'rdma', 'rdssm', 'gm', 'mx' ]
    validDeviceList = [ 'default', 'sock', 'ssm', 'shm', 'rdma', 'rdssm', 'gm', 'mx', 'shm-dapl', 'shm-tcp', 'shm-tmi', 'shm-ofa', 'dapl', 'dapl-tcp', 'dapl-tmi', 'dapl-ofa', 'tcp', 'tcp-dapl', 'tcp-tmi', 'tcp-ofa', 'tmi', 'tmi-dapl', 'tmi-tcp', 'tmi-ofa', 'ofa', 'ofa-dapl', 'ofa-tcp', 'ofa-tmi' ]


    np = 0
    ppn = 1

# processing data from the mpiexec.conf files
    rev = rootconfline[:]
    rev.extend(confline)
    rev.reverse()
    if 'I_MPI_DEVICE' in rev:
        idx = rev.index('I_MPI_DEVICE')
        device = rev[idx-1]

    if 'I_MPI_FABRICS' in rev:
        idx = rev.index('I_MPI_FABRICS')
        device = rev[idx-1]
    try:
        device.index(':')
        device=device[:device.index(':')]+'-'+device[device.index(':')+1:]
    except ValueError:
        pass


    if '-rdma' in rev:
        device = 'rdma'
    if '-RDMA' in rev:
        device = 'rdma'
    if '-gm' in rev:
        device = 'gm'
    if '-GM' in rev:
        device = 'gm'
    if '-mx' in rev:
        device = 'mx'
    if '-MX' in rev:
        device = 'mx'


    if '-ib' in rev:
        device = 'rdma'
    if '-IB' in rev:
        device = 'rdma'


    if 'I_MPI_PERHOST' in rev:
        idx = rev.index('I_MPI_PERHOST')
        ppn = rev[idx-1]

    if '-perhost' in rev:
        idx = rev.index('-perhost')
        ppn = rev[idx-1]

    if '-rr' in rev:
        ppn = '1'
    if '-grr' in rev:
        idx = rev.index('-grr')
        ppn = rev[idx-1]
    if '-ppn' in rev:
        idx = rev.index('-ppn')
        ppn = rev[idx-1]


    argidx = 0
    while argidx < len(confline):
        confarg = confline[argidx]
        if confarg == '-n' or confarg == '-np':
            np += int(confline[argidx + 1])
            argidx += 2
        else:
            argidx += 1

# processing data from the environment and  mpiexec command line
    srev = cmdline[1:]
    srev.reverse()
    if os.environ.has_key('I_MPI_DEVICE'):
        device = os.environ['I_MPI_DEVICE']

    if os.environ.has_key('I_MPI_FABRICS'):
        device = os.environ['I_MPI_FABRICS']
    try:
        device.index(':')
        device=device[:device.index(':')]+'-'+device[device.index(':')+1:]
    except ValueError:
        pass


    if os.environ.has_key('I_MPI_PERHOST'):
        ppn = os.environ['I_MPI_PERHOST']


    tmpdirname = None

    # Check if tune configuration directory specified explicitly
    argidx = 0
    while argidx < len(confline):
        if confline[argidx] == "-tune":
            if argidx + 1 < len(confline) and not confline[argidx + 1].startswith("-"):
                tmpdirname = confline[argidx + 1]
                argidx += 1
            else:
                tmpdirname = None
        argidx += 1
    argidx = 0
    while argidx < len(cmdline):
        if cmdline[argidx] == "-tune":
            if argidx + 1 < len(cmdline)  and not cmdline[argidx + 1].startswith("-"):
                tmpdirname = cmdline[argidx + 1]
                argidx += 1
            else:
                tmpdirname = None
        argidx += 1
    if tmpdirname != None:
        if os.path.isdir(tmpdirname):
            if os.access(tmpdirname, os.R_OK | os.X_OK):
                tuneconfdir = tmpdirname
            else:
                print 'Warning: the %s directory has wrong permissions. Tuned data files will be searched in the default directory.' % (tmpdirname)
                tmpdirname = None


    if 'I_MPI_DEVICE' in srev:
        idx = srev.index('I_MPI_DEVICE')
        device = srev[idx-1]

    if 'I_MPI_FABRICS' in srev:
        idx = srev.index('I_MPI_FABRICS')
        device = srev[idx-1]
    try:
        device.index(':')
        device=device[:device.index(':')]+'-'+device[device.index(':')+1:]
    except ValueError:
        pass


    if '-rdma' in srev:
        device = 'rdma'
    if '-RDMA' in srev:
        device = 'rdma'
    if '-gm' in srev:
        device = 'gm'
    if '-GM' in srev:
        device = 'gm'
    if '-mx' in srev:
        device = 'mx'
    if '-MX' in srev:
        device = 'mx'


    if '-ib' in srev:
        device = 'rdma'
    if '-IB' in srev:
        device = 'rdma'


    if 'I_MPI_PERHOST' in srev:
        idx = srev.index('I_MPI_PERHOST')
        ppn = srev[idx-1]

    if '-perhost' in srev:
        idx = srev.index('-perhost')
        ppn = srev[idx-1]

    if '-rr' in srev:
        ppn = '1'
    if '-grr' in srev:
        idx = srev.index('-grr')
        ppn = srev[idx-1]
    if '-ppn' in srev:
        idx = srev.index('-ppn')
        ppn = srev[idx-1]

    argidx = 0
    while argidx < len(cmdline):
        cmdarg = cmdline[argidx]
        if cmdarg == '-n' or cmdarg == '-np':
            np += int(cmdline[argidx + 1])
            argidx += 2
        else:
            argidx += 1
    if not np:
        np = 1 # overriding illegal zero with default 1; frankly, this is a strange situation if we are here

    resFileName = ''
    resFile = ''

    if tuneconfdir != tmpdirname:
        # Check if tune configuration file specified explicitly
        argidx = 0
        while argidx < len(confline):
            if confline[argidx] == "-tune":
                if argidx + 1 < len(confline) and not confline[argidx + 1].startswith("-"):
                    resFileName = confline[argidx + 1]
                    argidx += 1
                else:
                    resFileName = ''
            argidx += 1
                
        argidx = 0
        while argidx < len(cmdline):
            if cmdline[argidx] == "-tune":
                if argidx + 1 < len(cmdline)  and not cmdline[argidx + 1].startswith("-"):
                    resFileName = cmdline[argidx + 1]
                    argidx += 1
                else:
                    resFileName = ''
                    resFile = ''
            argidx += 1

        # Check if configuration file accessible 
        if resFileName:

            #resFile = os.path.join(tuneconfdir, resFileName)
            resFile = os.path.join(tuneconfdir, os.getcwd(), resFileName)

            if not os.access(resFile, os.F_OK):
                if os.access(resFile + '.conf', os.F_OK):
                    resFile += '.conf'
                else:
                    resFile = ''

        if resFile == '' and tmpdirname != None:
            print 'Warning: the %s file or directory doesn\'t exist. Tuned data files will be searched in the default directory.' % (resFileName)

    # if application-specific tune configration is not specified, 
    # try to find cluster-specific one
    if resFileName == '':
      if device not in validDeviceList:
        print 'You typed a wrong device name: %s. The sock device will be used' % (device)
        device = 'sock'

      if ppn in ['all', 'allcores']:
        print 'Value I_MPI_PERHOST=\"%s\" for -tune is not supported. Please specify a numerical one. I_MPI_PERHOST=1 will be used for data choosing.' % (ppn)
        ppn = 1


      try:
        AllFilesThere = os.listdir(tuneconfdir)
      except:
        AllFilesThere = []

      for file in AllFilesThere:

        fullName = os.path.join(tuneconfdir, file)

        tmp_fields = file.split('.')
        suffix = tmp_fields[len(tmp_fields) - 1]
        if file == 'mpiexec.conf' or not file.startswith('mpiexec_') or suffix != 'conf' or os.path.isdir(fullName):
            continue
        shortName = file[8:-5]
        fields = shortName.split('_')
        if len(fields) < 7: # 7 is specified by the file format
            continue
        finding_device = fields[0]
        try:
            index_np = fields.index('np')
            index_ppn = fields.index('ppn')
        except ValueError:
            continue # the file has a wrong format
        finding_np = fields[index_np + 1]
        finding_ppn = fields[index_ppn + 1]
        if device != finding_device:
            continue
# np processing
        np_data = finding_np.split('-')
        np_min = int(np_data[0])
        np_data_len = len(np_data)
        if np_data_len > 2:
            np_max = int(np_data[1])
            np_step = int(np_data[2])
        elif np_data_len > 1:
            np_max = int(np_data[1])
            np_step = 1
        else:
            np_max = np_min
            np_step = 1
        np_range = range(np_min, np_max + 1, np_step)

        if int(np) not in np_range:
            continue
# ppn processing
        ppn_data = finding_ppn.split('-')
        ppn_min = int(ppn_data[0])
        ppn_data_len = len(ppn_data)
        if ppn_data_len > 2:
            ppn_max = int(ppn_data[1])
            ppn_step = int(ppn_data[2])
        elif ppn_data_len > 1:
            ppn_max = int(ppn_data[1])
            ppn_step = 1
        else:
            ppn_max = ppn_min
            ppn_step = 1
        ppn_range = range(ppn_min, ppn_max + 1, ppn_step)

        if int(ppn) not in ppn_range:
            continue
        resFile = fullName
        break

    tunedTmpArgv = []
    if not resFile:
        if resFileName:
            print "WARNING: tune configuration '%s' not found." % resFileName
        else:
            print 'WARNING: there are no tuned data files appropriate for your configuration: device = %s, np = %d, ppn = %s' % \
                (device, np, ppn)
    else:
        try:
            tunedconfigFileFD = os.open(resFile,os.O_RDONLY)
        except Exception, errmsg:
            print 'Tuned data file (%s) opening failed!\n%s' % (resFile, errmsg)
            #pass
        else:
            tunedconfigFile = os.fdopen(tunedconfigFileFD,'r',0)
            tunedconfigLines = tunedconfigFile.readlines()
            tunedconfigLines = [ x.strip()  for x in tunedconfigLines if x[0] != '#' ]
            for line in tunedconfigLines:

                tmp_cmd = "/bin/sh -c 'for a in $*; do echo _$a; done' -- %s" % (line)
                if subprocess_module_available:
                    tmp_cmd = []
                    tmp_cmd.append('/bin/sh')
                    tmp_cmd.append('-c')
                    tmp_cmd.append('for a in $*; do echo _$a; done')
                    tmp_cmd.append('--')
                    tmp_cmd.append('%s' % (line))
                    sysshOut = subprocess.Popen(tmp_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
                    out_from_child = sysshOut.stdout
                else:
                    sysshOut = popen2.Popen3(tmp_cmd)
                    out_from_child = sysshOut.fromchild
                for shline in out_from_child:

                    tunedTmpArgv.append(shline[1:].strip())    # 1: strips off the leading _
    
    newcmdline.extend(rootconfline) # The lowest priority (<mpiinstalldir>/etc/mpiexec.conf)
    newcmdline.extend(tunedTmpArgv) # The tuned data
    newcmdline.extend(confline)     # The rest data from the mpiexec.conf files

    return newcmdline



# This function removes I_MPI_DEVICE entries if I_MPI_FABRICS exists
def remove_device_entries(arglist):
    try:
        arglist.index('I_MPI_FABRICS')
        while 1:
            try:
                i=arglist.index('I_MPI_DEVICE')
                del arglist[i-1]
                del arglist[i-1]
                del arglist[i-1]
            except ValueError:
                break
    except ValueError:
        pass

# This function removes I_MPI_DEVICE, I_MPI_FABRICS entries from the low priority list
def remove_low_priorities_entries(low_priority_arglist, high_priority_arglist):
    try:
        high_priority_arglist.index('I_MPI_FABRICS')
        while 1:
            try:
                i=low_priority_arglist.index('I_MPI_FABRICS')
                del low_priority_arglist[i-1]
                del low_priority_arglist[i-1]
                del low_priority_arglist[i-1]
            except ValueError:
                break
        while 1:
            try:
                i=low_priority_arglist.index('I_MPI_DEVICE')
                del low_priority_arglist[i-1]
                del low_priority_arglist[i-1]
                del low_priority_arglist[i-1]
            except ValueError:
                break
    except ValueError:
        pass
    try:
        high_priority_arglist.index('I_MPI_DEVICE')
        while 1:
            try:
                i=low_priority_arglist.index('I_MPI_FABRICS')
                del low_priority_arglist[i-1]
                del low_priority_arglist[i-1]
                del low_priority_arglist[i-1]
            except ValueError:
                break
        while 1:
            try:
                i=low_priority_arglist.index('I_MPI_DEVICE')
                del low_priority_arglist[i-1]
                del low_priority_arglist[i-1]
                del low_priority_arglist[i-1]
            except ValueError:
                break
    except ValueError:
        pass


# This function removes I_MPI_DEVICE, I_MPI_FABRICS entries from the low priority list and environment
def remove_low_priorities_and_environment_entries(low_priority_arglist, high_priority_arglist):
    try:
        high_priority_arglist.index('I_MPI_FABRICS')
        while 1:
            try:
                i=low_priority_arglist.index('I_MPI_FABRICS')
                del low_priority_arglist[i-1]
                del low_priority_arglist[i-1]
                del low_priority_arglist[i-1]
            except ValueError:
                break
        while 1:
            try:
                i=low_priority_arglist.index('I_MPI_DEVICE')
                del low_priority_arglist[i-1]
                del low_priority_arglist[i-1]
                del low_priority_arglist[i-1]
            except ValueError:
                break
        if os.environ.has_key('I_MPI_FABRICS'):
            del os.environ['I_MPI_FABRICS']
        if os.environ.has_key('I_MPI_DEVICE'):
            del os.environ['I_MPI_DEVICE']
    except ValueError:
        pass
    try:
        high_priority_arglist.index('I_MPI_DEVICE')
        while 1:
            try:
                i=low_priority_arglist.index('I_MPI_FABRICS')
                del low_priority_arglist[i-1]
                del low_priority_arglist[i-1]
                del low_priority_arglist[i-1]
            except ValueError:
                break
        while 1:
            try:
                i=low_priority_arglist.index('I_MPI_DEVICE')
                del low_priority_arglist[i-1]
                del low_priority_arglist[i-1]
                del low_priority_arglist[i-1]
            except ValueError:
                break
        if os.environ.has_key('I_MPI_FABRICS'):
            del os.environ['I_MPI_FABRICS']
        if os.environ.has_key('I_MPI_DEVICE'):
            del os.environ['I_MPI_DEVICE']
    except ValueError:
        pass


def usage():
    print __doc__
    sys.exit(-1)


if __name__ == '__main__':
    try:
        mpiexec()
    except SystemExit, errExitStatus:  # bounced to here by sys.exit inside mpiexec()
        myExitStatus = errExitStatus
    sys.exit(myExitStatus)
