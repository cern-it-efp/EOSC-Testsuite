#!/bin/sh
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

which which > /dev/null 2>&1
if [ $? -eq 0 ]; then
    enable_which=1
else
    enable_which=0
fi
if [ $enable_which ]; then
    PYTHON=$(which python 2>/dev/null)
else
    PYTHON=$(whereis python | cut -d ' ' -f 3)
fi


# check executable of find python
if [ ! -x "$PYTHON" ] ; then
    echo "Python executable not found! Please install python or check proper PATH!"
    exit -1
fi

# check version of python
$PYTHON - - $@ << END_OF_PYTHON_CODE
from sys import version, argv, exit
from socket import gethostname
if version[0] == '1' and version[1] == '.':
    print "You can't run mpdboot on %s your python version must be >= 2.2, current version is: %s" % ([gethostname()], [version[0:3]])
    exit(-1)
elif version[0] == '2' and version[1] == '.' and version[2] < '2':
    print "You can't run mpdboot on %s your python version must be >= 2.2, current version is: %s" % ([gethostname()], [version[0:3]])
    exit(-1)
END_OF_PYTHON_CODE

if [ $? != 0 ]; then
    exit -1
fi

# export PYTHONPATH for search mpdlib module

if [ $enable_which ]; then

    EXECPATH=$(which "$0")
    PYTHONPATH=$(dirname "$EXECPATH")

else
    PYTHONPATH=I_MPI_SUBSTITUTE_INSTALLDIR/ia32/bin
fi

export PYTHONPATH

# run mpdboot in normal mode

exec $PYTHON - "$0" $@ << END_OF_PYTHON_CODE

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
usage:  mpdboot --totalnum=<n_to_start> [--file=<hostsfile>]  [--help]
                [--rsh=<rshcmd>] [--user=<user>] [--mpd=<mpdcmd>] 
                [--loccons] [--remcons] [--shell] [--verbose] [-1]    
                [--ncpus=<ncpus>] [--ifhn=<ifhn>] [--chkup] [--chkuponly]
                [--ordered] [--maxbranch=<maxbranch>]
                [--parallel-startup] [--version]
 or, in short form,
        mpdboot -n n_to_start [-f <hostsfile>] [-h] [-r <rshcmd>] [-u <user>]
                [-m <mpdcmd>]  -s -v [-1] [-c] [-o] [-b] [-p] [-V]

--totalnum specifies the total number of mpds to start; at least
  one mpd will be started locally, and others on the machines specified
  by the file argument; by default, only one mpd per host will be
  started even if the hostname occurs multiple times in the hosts file
-1 means remove the restriction of starting only one mpd per machine;
  in this case, at most the first mpd on a host will have a console
--file specifies the file of machines to start the rest of the mpds on;
  it defaults to mpd.hosts
--mpd specifies the full path name of mpd on the remote hosts if it is
  not in your path
--rsh specifies the name of the command used to start remote mpds; it
  defaults to rsh; an alternative is ssh
--shell says that the Bourne shell is your default for rsh'
--verbose shows the ssh attempts as they occur; it does not provide
  confirmation that the sshs were successful
--loccons says you do not want a console available on local mpd(s)
--remcons says you do not want consoles available on remote mpd(s)
--ncpus indicates how many cpus you want to show for the local machine;
  others are listed in the hosts file
--ifhn indicates the interface hostname to use for the local mpd; others
  may be specified in the hostsfile
--chkup requests that mpdboot try to verify that the hosts in the host file
  are up before attempting start mpds on any of them; it just checks the number
  of hosts specified by -n
--chkuponly requests that mpdboot try to verify that the hosts in the host file
  are up; it then terminates; it just checks the number of hosts specified by -n
--ordered requests that mpdboot start all the mpd daemons in the exact order as
  specified in the host file
--maxbranch indicates the maximum number of mpds to enter the ring under another;
  the default is 4
--parallel-startup allows parallel fast starting of mpds under one root;
  useful for shells which do not support stdout transfer
--version prints version information

Copyright (C) 2003-2014 Intel Corporation.  All rights reserved.
"""

# workaround to suppress deprecated module warnings in python2.6
# see https://trac.mcs.anl.gov/projects/mpich2/ticket/362 for tracking
import warnings
warnings.filterwarnings('ignore', '.*the popen2 module is deprecated.*', DeprecationWarning)

from time import ctime
__author__ = "Ralph Butler and Rusty Lusk"
__date__ = ctime()
__version__ = "$Revision: 9833 $"
__credits__ = ""

import re

from os     import environ, system, path, kill, access, X_OK

from os     import getuid, WIFEXITED, WEXITSTATUS

from sys    import argv, exit, stdout

from errno import ENOENT



from sys import version
if version[0] == '2' and version[1] == '.' and version[2] > '4':
    import warnings
    warnings.filterwarnings("ignore", "", DeprecationWarning)
use_subprocess=0
if environ.has_key('I_MPI_PYTHON_MODULES'):
    modules = environ['I_MPI_PYTHON_MODULES']
    if modules == 'popen2':
        use_subprocess = 0
    elif modules == 'subprocess':
        use_subprocess = 1
if use_subprocess:
    try:
        from subprocess import Popen, PIPE, STDOUT
        subprocess_module_available = 1
    except:
        from popen2 import Popen4, Popen3, popen2
        subprocess_module_available = 0
else:
    try:
        from popen2 import Popen4, Popen3, popen2
        subprocess_module_available = 0
    except:
        from subprocess import Popen, PIPE, STDOUT
        subprocess_module_available = 1


from socket import gethostname, gethostbyname_ex
from select import select, error
from signal import SIGKILL
from commands import getoutput, getstatusoutput
from mpdlib import mpd_set_my_id, mpd_get_my_username, mpd_same_ips, mpd_get_ranks_in_binary_tree, \
                   mpd_print, MPDSock

global myHost, fullDirName, rshCmd, user, mpdCmd, debug, verbose


import sys
sys.path.insert(0,argv[1])
del argv[0:1]


def getversionpython(rshCmd, host):
    find_version = re.compile(r'(^\d\.\d)')
    ret_version = ''
    ver_of_python = {}
    fdsToSelect = []
    if rshCmd == '':
        cmd_get_version = "python -c 'from sys import version; print version[:3]'"

        if subprocess_module_available:
            cmd_get_version = []
            cmd_get_version.append('python')
            cmd_get_version.append('-c')
            cmd_get_version.append('from sys import version; print version[:3]')

    else:

#        if rshCmd != "rsh":
        if not re.search('rsh$', rshCmd):

            cmd_get_version = "%s -x %s -n 'python -c \"from sys import version; print version[:3]\"'" % (rshCmd, host)

            if subprocess_module_available:
                cmd_get_version = []
                cmd_get_version.append('%s' % rshCmd)
                cmd_get_version.append('-x')
                cmd_get_version.append('%s' % host)
                cmd_get_version.append('-n')
                cmd_get_version.append('python')
                cmd_get_version.append('-c')
                cmd_get_version.append("\"from sys import version; print version[:3]\"")

        else:
            cmd_get_version = "%s %s -n 'python -c \"from sys import version; print version[:3]\"'" % (rshCmd, host)

            if subprocess_module_available:
                cmd_get_version = []
                cmd_get_version.append('%s' % rshCmd)
                cmd_get_version.append('%s' % host)
                cmd_get_version.append('-n')
                cmd_get_version.append('python')
                cmd_get_version.append('-c')
                cmd_get_version.append("\"from sys import version; print version[:3]\"")

 
    if subprocess_module_available:
        mpdboot_get_version = Popen(cmd_get_version, bufsize=0, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        vfd = mpdboot_get_version.stdout
    else:
        mpdboot_get_version = Popen4(cmd_get_version, 0)
        vfd = mpdboot_get_version.fromchild

    fdsToSelect.append(vfd)
    while fdsToSelect:
        try:
            (readyFDs,unused1,unused2) = select(fdsToSelect,[],[],0.1)
        except error, errmsg:
            mpd_raise('mpdboot: select failed: errmsg=:%s:' % (errmsg) )
        if vfd and vfd in readyFDs:
            line = vfd.readline()
            if line:
                if re.search('Host key not found from database|Host key verification failed', line):
                    ret_version = "ERROR:\tCould not execute command on %s via %s.\n\tCould you please connect to %s node without password authentication first?" % ([host], [rshCmd], host)
                    break
                if re.search(find_version, line):
                    ver_of_python = re.findall(find_version, line)
            else:
                vfd.close()
                fdsToSelect.remove(vfd)
    if len(ver_of_python) != 0:
        ret_version = ver_of_python[0]
    return ret_version

def deletekey(hostsInfo, hostkey):
    for info in hostsInfo:
        for host_key in info.keys():
            if host_key == "host":
                if info[host_key] == hostkey:
                    del hostsInfo[hostsInfo.index(info)]



def mpdboot():
    global myHost, fullDirName, rshCmd, user, mpdCmd, debug, verbose

    global qS


    global totalnumToStart, taggedMpdPortOutput

    myHost = gethostname()
    mpd_set_my_id('mpdboot_%s' % (myHost) )
    fullDirName = path.abspath(path.split(argv[0])[0])

    rshCmd = 'ssh'

    user = mpd_get_my_username()
    mpdCmd = path.join(fullDirName,'mpd.py')

    mpdCmd = mpdCmd.replace(' ', '\_')

    hostsFilename = 'mpd.hosts'
    totalnumToStart = 1    # may get chgd below
    debug = 0
    verbose = 0
    localConArg  = ''
    remoteConArg = ''
    oneMPDPerHost = 1

    quickStartup = 0


    qS = 0


    checkpython = 0
    if environ.has_key('I_MPI_MPD_CHECK_PYTHON') \
        and environ['I_MPI_MPD_CHECK_PYTHON'] in ['1', 'on', 'yes', 'enable']:
        checkpython = 1

    myNcpus = 1

    numCpusOverride = 1

    myIfhn = ''
    chkupIndicator = 0  # 1 -> chk and start ; 2 -> just chk

    if environ.has_key('I_MPI_MPD_CHECK_HOSTSUP') \
        and environ['I_MPI_MPD_CHECK_HOSTSUP'] in ['1', 'on', 'yes', 'enable']:
        chkupIndicator = 1


    checkHostname = 1


    maxUnderOneRoot = 4 # Default value


    taggedMpdPortOutput = 1
    if environ.has_key('I_MPI_JOB_TAGGED_PORT_OUTPUT') \
        and environ['I_MPI_JOB_TAGGED_PORT_OUTPUT'] in ['0', 'off', 'no', 'disable']:
        taggedMpdPortOutput = 0


    if environ.has_key('I_MPI_MPD_RSH'):
        rshCmd = environ['I_MPI_MPD_RSH']

    
    version_of_python = {}
    
    try:
        shell = path.split(environ['SHELL'])[-1]
    except:
        shell = 'csh'

    argidx = 1    # skip arg 0
    while argidx < len(argv):
        if   argv[argidx] == '-h' or argv[argidx] == '--help':
            usage()
        elif argv[argidx] == '-r':    # or --rsh=
            rshCmd = argv[argidx+1]
            argidx += 2
        elif argv[argidx].startswith('--rsh'):
            splitArg = argv[argidx].split('=')
            try:
                rshCmd = splitArg[1]
            except:
                print 'mpdboot: invalid argument:', argv[argidx]
                usage()
            argidx += 1
        elif argv[argidx] == '-u':    # or --user=
            user = argv[argidx+1]
            argidx += 2
        elif argv[argidx].startswith('--user'):
            splitArg = argv[argidx].split('=')
            try:
                user = splitArg[1]
            except:
                print 'mpdboot: invalid argument:', argv[argidx]
                usage()
            argidx += 1
        elif argv[argidx] == '-m':    # or --mpd=
            mpdCmd = argv[argidx+1]
            argidx += 2
        elif argv[argidx].startswith('--mpd'):
            splitArg = argv[argidx].split('=')
            try:
                mpdCmd = splitArg[1]
            except:
                print 'mpdboot: invalid argument:', argv[argidx]
                usage()
            argidx += 1
        elif argv[argidx] == '-f':    # or --file=
            hostsFilename = argv[argidx+1]
            argidx += 2
        elif argv[argidx].startswith('--file'):
            splitArg = argv[argidx].split('=')
            try:
                hostsFilename = path.expanduser(splitArg[1])
            except:
                print 'mpdboot: invalid argument:', argv[argidx]
                usage()
            argidx += 1
        elif argv[argidx].startswith('--ncpus'):
            splitArg = argv[argidx].split('=')
            try:
                myNcpus = int(splitArg[1])
            except:
                print 'mpdboot: invalid argument:', argv[argidx]
                usage()

            numCpusOverride = 0

            argidx += 1
        elif argv[argidx].startswith('--ifhn'):
            splitArg = argv[argidx].split('=')
            myIfhn = splitArg[1]
            myHost = splitArg[1]
            argidx += 1
        elif argv[argidx] == '-n':    # or --totalnum=
            totalnumToStart = int(argv[argidx+1])
            argidx += 2
        elif argv[argidx].startswith('--totalnum'):
            splitArg = argv[argidx].split('=')
            try:
                totalnumToStart = int(splitArg[1])
            except:
                print 'mpdboot: invalid argument:', argv[argidx]
                usage()
            argidx += 1

        elif argv[argidx] == '-b':    # or --maxbranch
            maxUnderOneRoot = int(argv[argidx+1])
            argidx += 2

        elif argv[argidx].startswith('--maxbranch'):
            splitArg = argv[argidx].split('=')
            try:
                maxUnderOneRoot = int(splitArg[1])
            except:
                print 'mpdboot: invalid argument:', argv[argidx]
                usage()
            argidx += 1
        elif argv[argidx] == '-d' or argv[argidx] == '--debug':
            debug = 1
            argidx += 1
        elif argv[argidx] == '-s' or argv[argidx] == '--shell':
            shell = 'bourne'
            argidx += 1
        elif argv[argidx] == '-v' or argv[argidx] == '--verbose':
            verbose = 1
            argidx += 1
        elif argv[argidx] == '-c' or argv[argidx] == '--chkup':
            chkupIndicator = 1
            argidx += 1
        elif argv[argidx] == '--chkuponly':
            chkupIndicator = 2
            argidx += 1
        elif argv[argidx] == '-1':
            oneMPDPerHost = 0
            argidx += 1
        elif argv[argidx] == '--loccons':
            localConArg  = '-n'
            argidx += 1
        elif argv[argidx] == '--remcons':
            remoteConArg = '-n'
            argidx += 1

        elif argv[argidx] == '--nochkname':

#            checkHostname = 0
            print 'mpdboot: --nochkname option is for internal use only and under construction. No special actions will be done.'

            argidx += 1


        elif argv[argidx] == '-p' or argv[argidx] == '--parallel-startup':
            quickStartup = 1
            argidx += 1


        elif argv[argidx] == '-o' or argv[argidx] == '--ordered':
            maxUnderOneRoot = 1 # value for ordered mpds start
            argidx += 1


        elif argv[argidx] == '-V' or argv[argidx] == '--version':
            vers = 'Version 4.1.3  Build 20140226'
            print 'Intel(R) MPI Library for Linux* OS, 32-bit applications,',vers
            print 'Copyright (C) 2003-2014 Intel Corporation.  All rights reserved.\n'
            if len(sys.argv) < 3:
                sys.exit(0)            

        else:
            print 'mpdboot: unrecognized argument:', argv[argidx]
            usage()
    if debug:
        print 'debug: starting'

    lines = []

#    if totalnumToStart > 1:

    try:
        f = open(hostsFilename,'r')
        for line in f:
            lines.append(line)

    except IOError, errinfo:
        if errinfo[0] != ENOENT:
            print 'unable to open hostsfile %s: %s' % (hostsFilename, errinfo[1])
            exit(-1)

    except:
        print 'unable to open (or read) hostsfile %s' % (hostsFilename)
        exit(-1)

    hostsAndInfo = [ {'host' : myHost, 'ncpus' : myNcpus, 'ifhn' : myIfhn, 'ip' : ''} ]
    if checkHostname:
        from socket import socket, AF_INET, SOCK_STREAM
        try:
            sock1 = socket(AF_INET,SOCK_STREAM)
        except Exception, data:
            mpd_print(1, 'failed to create a socket (sock1): %s, %s' % ( data.__class__, data) )
        try:
            sock1.bind(('',0))
            sock1.listen(1)
            port1 = sock1.getsockname()[1]
            sock2 = socket(AF_INET,SOCK_STREAM)
        except Exception, data:
            mpd_print(1, 'failed to create a socket (sock2): %s, %s' % ( data.__class__, data) )
            sock1.close()


    is_different_ncpus = 0 # if 0 all daemons will receive the same ncpus values which are equal to 1

    for line in lines:
        line = line.strip()
        if not line  or  line[0] == '#':
            continue

        line = re.split('#', line)[0] # Cutting off comments at the end of the line
        line = line.strip()

        splitLine = re.split(r'\s+',line)
        host = splitLine[0]

        ncpus = 1  # default

        if ':' in host:
            (host,ncpus) = host.split(':',1)

            ncpus = int(ncpus)

            if ncpus != 1:
                is_different_ncpus = 1


        ifhn = ''  # default
        for kv in splitLine[1:]:
            (k,v) = kv.split('=',1)
            if k == 'ifhn':
                ifhn = v

        try:
            ip = gethostbyname_ex(host)[2][0]
        except:
            ip = ''
        if checkHostname:
            try:
                rc = sock2.connect_ex((host,port1))
                if rc == 0:
                    sock3, addr = sock1.accept()
                    sock1.close()
                    sock2.close()
                    sock3.close()
                    myHost = hostsAndInfo[0]['host'] = host

                    if numCpusOverride:
                        myNcpus = hostsAndInfo[0]['ncpus'] = ncpus

                    myIfhn = hostsAndInfo[0]['ifhn'] = ifhn
                    hostsAndInfo[0]['ip'] = ip
                    checkHostname=0
                    continue

#           except: # original lines was commented out
#                mpd_print(1, ' sock2 connect failed' % ( data.__class__, data) )
            except Exception, data:                
                mpd_print(1, 'failed to connect to the socket (sock2): {%s, %s}. Probable reason: host \"%s\" is invalid' % ( data.__class__, data, host) )

                sock1.close()
                sock2.close()
        hostsAndInfo.append( {'host' : host, 'ncpus' : ncpus, 'ifhn' : ifhn, 'ip' : ip} )

    if oneMPDPerHost  and  totalnumToStart > 1:
        oldHosts = hostsAndInfo[:]
        hostsAndInfo = []
        for x in oldHosts:
           keep = 1
           for y in hostsAndInfo:

               if x['ip'] == y['ip']:

                   keep = 0
                   break
           if keep:
               hostsAndInfo.append(x)
    if len(hostsAndInfo) < totalnumToStart:    # one is local
        print 'totalnum=%d  numhosts=%d' % (totalnumToStart,len(hostsAndInfo))
        print 'there are not enough hosts on which to start all processes'
        exit(-1)
    

    if checkpython and not quickStartup:

        for info in hostsAndInfo:
            for host_key in info.keys():
                if host_key == "host":
                    if not version_of_python.has_key(myHost):
                        version_of_python[myHost] = getversionpython('', myHost)
                    elif not version_of_python.has_key(info[host_key]):
                        version_of_python[info[host_key]] = getversionpython(rshCmd, info[host_key])

        if re.match('2.4',version_of_python[myHost]):
            for key, val in version_of_python.items():
                if not re.match('2.4', val):
                    print "You can't run mpdboot on %s version of python must be >= 2.4, current %s" %([key], [val])

                    deletekey(hostsAndInfo, key)

                    totalnumToStart -= 1
        else:
            for key in version_of_python.keys():
                if re.match('1.5|2.0|2.1', version_of_python[key]):
                    print "You can't run mpdboot on %s version of python must be >= 2.2, current %s" %([key], [version_of_python[key]])
                    deletekey(hostsAndInfo, key)
                    totalnumToStart -= 1
                elif re.match('2.4', version_of_python[key]):
                    print "You can't run mpdboot on %s version of python must be < 2.4, current %s" %([key], [version_of_python[key]])
                    deletekey(hostsAndInfo, key)
                    totalnumToStart -= 1
                elif re.search("ERROR:", version_of_python[key]):
                    print version_of_python[key]
                    deletekey(hostsAndInfo, key)
                    totalnumToStart -= 1
    

    if chkupIndicator:
        hostsToCheck = [ hai['host'] for hai in hostsAndInfo[1:totalnumToStart] ]
        (upList,dnList) = chkupdn(hostsToCheck)
        if dnList:
            print "these hosts are down; exiting"
            print dnList
            exit(-1)
        print "there are %d hosts up (counting local)" % (len(upList)+1)
        if chkupIndicator == 2:  # do the chkup and quit
            exit(0)

    try:


        rc = system('"%s"/mpdallexit.py > /dev/null' % (fullDirName)) # stop current mpds


        if verbose or debug:
            print 'running mpdallexit on %s' % (myHost)
    except:
        pass


    if getuid() == 0 and WIFEXITED(rc) and WEXITSTATUS(rc) == 1:
        print '%s/mpdboot terminated' % (fullDirName)
        exit(-1)

    if myIfhn:
        ifhn = '--ifhn=%s' % (myIfhn)
    else:
        ifhn = ''
    hostsAndInfo[0]['entry_host'] = ''
    hostsAndInfo[0]['entry_port'] = ''

    mpdArgs = '%s %s --ncpus=%d --myhost=%s' % (localConArg,ifhn,myNcpus,myHost)


    if taggedMpdPortOutput:
        mpdCmd_ori = mpdCmd[:]
        mpdCmd = 'env I_MPI_JOB_TAGGED_PORT_OUTPUT=1 %s' % (mpdCmd)

    (mpdPID,mpdFD) = launch_one_mpd(0,0,mpdArgs,hostsAndInfo)
    fd2idx = {mpdFD : 0}

    handle_mpd_output(mpdFD,fd2idx,hostsAndInfo)

    if taggedMpdPortOutput:
        mpdCmd = mpdCmd_ori


    try:
        from os import sysconf
        maxfds = sysconf('SC_OPEN_MAX')
    except:
        maxfds = 1024
    maxAtOnce = min(128,maxfds-8)  # -8  for stdeout, etc. + a few more for padding

    if quickStartup:
        maxAtOnce = min(maxAtOnce, totalnumToStart)
        maxUnderOneRoot = totalnumToStart


    hostsSeen = { myHost : 1 }
    fdsToSelect = []
    numStarted = 1  # local already going
    numStarting = 0
    numUnderCurrRoot = 0
    possRoots = []
    currRoot = 0
    idxToStart = 1  # local mpd already going

    envsToOverrideOnLocalHosts = [
        'HOSTNAME',
        'HOSTTYPE',
        'MACHTYPE',
        'OSTYPE' ]


    if environ.has_key('SHELL') and (environ['SHELL'].find('csh') != -1):
        envsToOverrideOnLocalHosts.remove('HOSTNAME')
        envsToOverrideOnLocalHosts.insert(-1, 'HOST')


    mpdAddEnvsString = 'env'

    mpdAddEnvsString += ' I_MPI_JOB_TAGGED_PORT_OUTPUT=1'


    for env in envsToOverrideOnLocalHosts:

        if environ.has_key(env):
            mpdAddEnvsString += ' %s=\$%s' % (env, env)


    if environ.has_key('I_MPI_MPD_CONF'):
#       mpdCmd = 'env I_MPI_MPD_CONF=%s %s' % (environ['I_MPI_MPD_CONF'], mpdCmd)
        mpdAddEnvsString += ' I_MPI_MPD_CONF=%s' % (environ['I_MPI_MPD_CONF'])


    if environ.has_key('MPD_CON_EXT'):
#       mpdCmd = 'env MPD_CON_EXT=%s %s' % (environ['MPD_CON_EXT'], mpdCmd)
        mpdAddEnvsString += ' MPD_CON_EXT=%s' % (environ['MPD_CON_EXT'])
    if environ.has_key('I_MPI_JOB_CONTEXT'):
        mpdAddEnvsString += ' I_MPI_JOB_CONTEXT=%s' % (environ['I_MPI_JOB_CONTEXT'])


    if environ.has_key('TMPDIR'):
        mpdAddEnvsString += ' TMPDIR=%s' % (environ['TMPDIR'])
    if environ.has_key('MPD_TMPDIR'):
        mpdAddEnvsString += ' MPD_TMPDIR=%s' % (environ['MPD_TMPDIR'])
    if environ.has_key('I_MPI_MPD_TMPDIR'):
        mpdAddEnvsString += ' I_MPI_MPD_TMPDIR=%s' % (environ['I_MPI_MPD_TMPDIR'])


    if mpdAddEnvsString != 'env':
        mpdCmd = '%s %s' % (mpdAddEnvsString, mpdCmd)


    if quickStartup:
        qS = 1

    while numStarted < totalnumToStart:
        if  numStarting < maxAtOnce  and  idxToStart < totalnumToStart:
            if numUnderCurrRoot < maxUnderOneRoot:
                entryHost = hostsAndInfo[currRoot]['host']
                entryPort = hostsAndInfo[currRoot]['list_port']
                hostsAndInfo[idxToStart]['entry_host'] = entryHost
                hostsAndInfo[idxToStart]['entry_port'] = entryPort
                if hostsSeen.has_key(hostsAndInfo[idxToStart]['host']):
                    remoteConArg = '-n'

                hostName = hostsAndInfo[idxToStart]['host']
                ipAddress = hostsAndInfo[idxToStart]['ip']


                hostNcpus = hostsAndInfo[idxToStart]['ncpus']

                ifhn = hostsAndInfo[idxToStart]['ifhn']

                if ifhn:
                    ifhn = '--ifhn=%s' % (ifhn)
# multihome support
                else:
                    ifhn = '--ifhn=%s' % (ipAddress)

                mpdArgs = '%s -h %s -p %s %s --ncpus=%d --myhost=%s --myip=%s' % \
                (remoteConArg,entryHost,entryPort,ifhn,hostNcpus,hostName,ipAddress)
#                (remoteConArg,entryHost,entryPort,ifhn,myNcpus,hostName,ipAddress)


                (mpdPID,mpdFD) = launch_one_mpd(idxToStart,currRoot,mpdArgs,hostsAndInfo)
                numStarting += 1
                numUnderCurrRoot += 1
                hostsAndInfo[idxToStart]['pid'] = mpdPID
                hostsSeen[hostsAndInfo[idxToStart]['host']] = 1
                fd2idx[mpdFD] = idxToStart
                fdsToSelect.append(mpdFD)
                idxToStart += 1
            else:
                if possRoots:
                    currRoot = possRoots.pop()
                    numUnderCurrRoot = 0
            selectTime = 0.01
        else:
            selectTime = 0.1

        if not qS:
            try:
               (readyFDs,unused1,unused2) = select(fdsToSelect,[],[],selectTime)
            except error, errmsg:
                mpd_print(1,'mpdboot: select failed: errmsg=:%s:' % (errmsg) )
                exit(-1)
            for fd in readyFDs:

                handle_mpd_output(fd,fd2idx,hostsAndInfo)

                numStarted += 1
                numStarting -= 1
                possRoots.append(fd2idx[fd])
                fdsToSelect.remove(fd)
                fd.close()
        else:
                numStarted += 1
                numStarting -= 1
    if qS:
        numStarted=1
        while numStarted < totalnumToStart:
            try:
                (readyFDs,unused1,unused2) = select(fdsToSelect,[],[],0.1)
            except error, errmsg:
                mpd_print(1,'mpdboot: select failed: errmsg=:%s:' % (errmsg) )
                exit(-1)
            for fd in readyFDs:
                handle_mpd_output(fd,fd2idx,hostsAndInfo)
                numStarted += 1
                possRoots.append(fd2idx[fd])
                fdsToSelect.remove(fd)
                fd.close()


    if 1:
        import os, mpdlib
        if (hasattr(os,'getuid')  and  getuid() == 0):

            fullDirName = path.abspath(path.split(sys.argv[0])[0])  # normalize

            mpdroot = path.join(fullDirName,'mpdroot')
            conSock = mpdlib.MPDConClientSock(mpdroot=mpdroot,secretword='')
        else:
            conSock = mpdlib.MPDConClientSock(secretword='')
    
        if is_different_ncpus:
            msgToMPD = { 'cmd' : 'get_ncpus_table' }
            conSock.send_dict_msg(msgToMPD)
            msg  = conSock.recv_dict_msg(timeout=20)
            if not msg:
                print 'Can not get answer from mpd'
        else:
            msgToMPD = { 'cmd' : 'set_ncpus_equality' }
            conSock.send_dict_msg(msgToMPD)
            msg  = conSock.recv_dict_msg(timeout=20)
            if not msg:
                print 'Can not get answer from mpd'
        conSock.close()



def insert_space(cmd, idxToStart):
    i = 0
    for x in cmd:

        if re.search(r'\\\_', x):

            cmd[i] = x.replace('\_', ' ')
            if idxToStart != 0:
                cmd[i] = '"' + cmd[i] + '"'
        i = i + 1
    return


def launch_one_mpd(idxToStart,currRoot,mpdArgs,hostsAndInfo):
    global myHost, fullDirName, rshCmd, user, mpdCmd, debug, verbose

    global totalnumToStart

    mpdHost = hostsAndInfo[idxToStart]['host']
    if idxToStart == 0:


        if qS:
            cmd = '%s %s -e -d -s %d &' % (mpdCmd,mpdArgs,totalnumToStart)
        else:
            cmd = '%s %s -e -d -s %d' % (mpdCmd,mpdArgs,totalnumToStart)


    else:
        if rshCmd == 'ssh':
            rshArgs = '-x -n -q'
        else:
            rshArgs = '-n'
        mpdHost = hostsAndInfo[idxToStart]['host']


        if qS:
            cmd = "%s %s %s %s %s -e -d -s %d &" % \
               (rshCmd,rshArgs,mpdHost,mpdCmd,mpdArgs,totalnumToStart)
        else:
            cmd = "%s %s %s %s %s -e -d -s %d " % \
              (rshCmd,rshArgs,mpdHost,mpdCmd,mpdArgs,totalnumToStart)


    if verbose:
        entryHost = hostsAndInfo[idxToStart]['entry_host']
        entryPort = hostsAndInfo[idxToStart]['entry_port']
        # print "LAUNCHED mpd on %s  via  %s  %s" % (mpdHost,entryHost,str(entryPort))
        print "LAUNCHED mpd on %s  via  %s" % (mpdHost,entryHost)
    if debug:
        print "debug: launch cmd=", cmd

    if subprocess_module_available:
        cmd = re.split(r'\s+', cmd)

        insert_space(cmd, idxToStart)

        mpd = Popen(cmd, bufsize=0, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        mpdFD = mpd.stdout
    else:
        cmd = re.split(r'\s+', cmd)

        insert_space(cmd, idxToStart)

        mpd = Popen4(cmd,0)
        mpdFD = mpd.fromchild
    mpdPID = mpd.pid

    return (mpdPID,mpdFD)

def handle_mpd_output(fd,fd2idx,hostsAndInfo):
    global myHost, fullDirName, rshCmd, user, mpdCmd, debug, verbose

    global qS


    global taggedMpdPortOutput

    idx = fd2idx[fd]
    host = hostsAndInfo[idx]['host']

#    port = fd.readline().strip()
    port = ''

    starting_phrase = '<I_MPI_MPD_PORT>'
    closing_phrase = '</I_MPI_MPD_PORT>'

    lines = fd.readlines()

    if qS:
        return


    if not lines:
        mpd_print(1, 'mpdboot: can not get anything from the mpd daemon; please check connection to %s' % (host))
        try:

            system('"%s"/mpdallexit.py > /dev/null' % (fullDirName)) # stop current mpds

        except:
            pass
        exit(-1)

    firstline = lines[0].strip()
    if firstline.isdigit(): # a port is in the first line
        port = firstline

    elif taggedMpdPortOutput: # seeking the port

        for l in lines:
            line = l.strip()
            if not line:

                continue

            l_idx = line.find(starting_phrase)
            if l_idx != -1:
                try:
                    r_idx = line.index(closing_phrase)
                except:
                    continue
                port = line[l_idx+len(starting_phrase):r_idx]
                break

    if debug:
        print "debug: mpd on %s  on port %s" % (host,port)
    if port.isdigit():
        hostsAndInfo[idx]['list_port'] = int(port)
        tempSock = MPDSock(name='temp_to_mpd')
        try:
            tempSock.connect((host,int(port)))

        except Exception, errmsg:
            mpd_print(1, 'Failed to establish a socket connection with %s:%s : %s' % (host, port, errmsg))

            tempSock.close()
            tempSock = 0
        if tempSock:
            msgToSend = { 'cmd' : 'ping', 'ifhn' : 'dummy', 'port' : 0}
            tempSock.send_dict_msg(msgToSend)
            msg = tempSock.recv_dict_msg()    # RMB: WITH TIMEOUT ??
            if not msg  or  not msg.has_key('cmd')  or  msg['cmd'] != 'challenge':
                mpd_print(1,'failed to ping mpd on %s; received output=%s' % \
                          (host,msg) )

                mpd_print(1,'Please examine the /tmp/mpd2.logfile_%s log file on each node of the ring' % \
                          (mpd_get_my_username()) )

                tempOut = tempSock.recv(1000)
                print tempOut

                try: getoutput('"%s"/mpdallexit.py' % (fullDirName))

                except: pass
                exit(-1)
            tempSock.close()
        else:
            mpd_print(1,'failed to connect to mpd on %s' % (host) )

            try: getoutput('"%s"/mpdallexit.py' % (fullDirName))

            except: pass
            exit(-1)
    else:
        mpd_print(1,'from mpd on %s, invalid port info:' % (host) )

        for l in lines:
            print l.strip()
#        print port
#        print fd.read()


        try: getoutput('"%s"/mpdallexit.py' % (fullDirName))

        except: pass
        exit(-1)
    if verbose:
        print "RUNNING: mpd on", hostsAndInfo[fd2idx[fd]]['host']
    if debug:
        print "debug: info for running mpd:", hostsAndInfo[fd2idx[fd]]

def chkupdn(hostList):
    upList = []
    dnList = []
    for hostname in hostList:
        print 'checking', hostname
        if rshCmd == 'ssh':
            rshArgs = '-x -n'
        else:
            rshArgs = '-n'
        cmd = "%s %s %s /bin/echo hello" % (rshCmd,rshArgs,hostname)

        if subprocess_module_available:
            cmd = re.split(r'\s+', cmd)
            runner = Popen(cmd, bufsize=0, stdin=PIPE, stdout=PIPE, stderr=PIPE, close_fds=True)
            runout = runner.stdout
            runerr = runner.stderr
            runin  = runner.stdin
        else:
            runner = Popen3(cmd,1,0)
            runout = runner.fromchild
            runerr = runner.childerr
            runin  = runner.tochild

        runpid = runner.pid
        up = 0
        try:
            # (readyFDs,unused1,unused2) = select([runout,runerr],[],[],9)
            (readyFDs,unused1,unused2) = select([runout],[],[],9)
        except:
            print 'select failed'
            readyFDs = []
        for fd in readyFDs:  # may have runout and runerr sometimes
            line = fd.readline()
            if line and line.startswith('hello'):
                up = 1
            else:
                pass
        if up:
            upList.append(hostname)
        else:
            dnList.append(hostname)
        try:
            kill(runpid,SIGKILL)
        except:
            pass
    return(upList,dnList)

def usage():
    print __doc__
    stdout.flush()
    exit(-1)

if __name__ == '__main__':
    mpdboot()
END_OF_PYTHON_CODE
