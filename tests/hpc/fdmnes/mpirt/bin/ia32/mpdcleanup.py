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

## NOTE: we do NOT allow this pgm to run via mpdroot

"""
usage: mpdcleanup', '[-f <hostsfile>] [-r <rshcmd>] [-u <user>] [-c <cleancmd>] [-a] [-V]
   or: mpdcleanup', '[--file=<hostsfile>] [--rsh=<rshcmd>] [--user=<user>] [--clean=<cleancmd>] [--all] [--version]
Removes the Unix socket on local (the default) and remote machines and, if -a (--all) is specified, also kills
all mpd daemons related to the current ring on the hosts specified in the <hostfile>.
This is useful in case the mpd crashed badly and did not remove it, which it normally does

Copyright (C) 2003-2014 Intel Corporation.  All rights reserved.
"""
from time import ctime
__author__ = "Ralph Butler and Rusty Lusk"
__date__ = ctime()
__version__ = "$Revision: 9833 $"
__credits__ = ""


import sys, os, socket

from getopt import getopt
from mpdlib import mpd_get_my_username

import re, signal


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
        from subprocess import Popen, PIPE, STDOUT
        subprocess_module_available = 1
    except:
        from popen2 import Popen4
        subprocess_module_available = 0
else:
    try:
        from popen2 import Popen4
        subprocess_module_available = 0
    except:
        from subprocess import Popen, PIPE, STDOUT
        subprocess_module_available = 1


from mpdlib import mpd_get_my_username, mpd_same_ips, mpd_set_tmpdir

def mpdcleanup():
    rshCmd    = 'ssh'
    user      = mpd_get_my_username()
    cleanCmd  = '/bin/rm -f '

    killMpdsOnAllHosts = 0
    pidCmd = '/bin/cat'

    pidString = 'logfile for mpd with pid'


    hostsFile = ''
    verbose = 0
    numFromHostsFile = 0  # chgd below

    if os.environ.has_key('I_MPI_MPD_RSH'):
        rshCmd = os.environ['I_MPI_MPD_RSH']

    try:

#       (opts, args) = getopt(sys.argv[1:], 'hf:r:u:c:', ['help', 'file=', 'rsh=', 'user=', 'clean='])
        (opts, args) = getopt(sys.argv[1:], 'ahVf:r:u:c:', ['all', 'help', 'version', 'file=', 'rsh=', 'user=', 'clean='])

    except:
        print 'invalid arg(s) specified'
        usage()
    else:
        for opt in opts:

            if opt[0] == '-a' or opt[0] == '--all':
                killMpdsOnAllHosts = 1


            elif opt[0] == '-V' or opt[0] == '--version':
                vers = 'Version 4.1.3  Build 20140226'
                print 'Intel(R) MPI Library for Linux* OS, 32-bit applications,',vers
                print 'Copyright (C) 2003-2014 Intel Corporation.  All rights reserved.\n'
                sys.exit(0)

            elif opt[0] == '-r' or opt[0] == '--rsh':
                rshCmd = opt[1]
            elif opt[0] == '-u' or opt[0] == '--user':
                user   = opt[1]
            elif opt[0] == '-f' or opt[0] == '--file':
                hostsFile = opt[1]
            elif opt[0] == '-h' or opt[0] == '--help':
                usage()
            elif opt[0] == '-c' or opt[0] == '--clean':
                cleanCmd = opt[1]
    if args:
        print 'invalid arg(s) specified: ' + ' '.join(args)
        usage()

    if os.environ.has_key('MPD_CON_EXT'):
        conExt = '_' + os.environ['MPD_CON_EXT']
    else:
        conExt = ''
    if os.environ.has_key('I_MPI_JOB_CONTEXT'):
        conExt = '_'  + os.environ['I_MPI_JOB_CONTEXT']

    tmpDir = '/tmp'
    if os.environ.has_key('TMPDIR'):
        if os.path.exists(os.environ['TMPDIR']):
            tmpDir = os.environ['TMPDIR']
        else:
            if not os.environ.has_key('MPD_TMPDIR') and not os.environ.has_key('I_MPI_MPD_TMPDIR'):
                print 'Warning: the directory pointed by TMPDIR (%s) does not exist! /tmp will be used.' % (os.environ['TMPDIR'])
    if os.environ.has_key('MPD_TMPDIR'):
        if os.path.exists(os.environ['MPD_TMPDIR']):
            tmpDir = os.environ['MPD_TMPDIR']
        else:
            if not os.environ.has_key('I_MPI_MPD_TMPDIR'):
                print 'Warning: the directory pointed by MPD_TMPDIR (%s) does not exist! /tmp will be used.' % (os.environ['MPD_TMPDIR'])
    if os.environ.has_key('I_MPI_MPD_TMPDIR'):
        if os.path.exists(os.environ['I_MPI_MPD_TMPDIR']):
            tmpDir = os.environ['I_MPI_MPD_TMPDIR']
        else:
            print 'Warning: the directory pointed by I_MPI_MPD_TMPDIR (%s) does not exist! %s will be used.' % (os.environ['I_MPI_MPD_TMPDIR'], tmpDir)
    if tmpDir and tmpDir != '/tmp':
        cleanFile = '%s/mpd2.console_' % (tmpDir) + socket.gethostname() + '_' + user + conExt
        logFile = '%s/mpd2.logfile_' % (tmpDir) + socket.gethostname() + '_' + user + conExt    
    else:    
        cleanFile = '/tmp/mpd2.console_' + user + conExt

        logFile = '/tmp/mpd2.logfile_' + user + conExt    


    os.system( '%s %s' % (cleanCmd,cleanFile) )
    if rshCmd == 'ssh':
        xOpt = '-x -q'
    else:
        xOpt = ''


    if killMpdsOnAllHosts:
        try:
            file = open(logFile, 'r')
        except Exception, errmsg:
            print 'Can\'t open file %s: %s' % (logFile, errmsg)
            sys.exit(-1)

#        first_string = file.readline()
        strings = file.read()
        file.close()

#        first_string = first_string.strip()
#        pid = re.split(r'\s+', first_string)[5]
        try:
            pidIndex = strings.index(pidString)
        except:
            print 'No pid in log file %s found' % logFile
            sys.exit(-1)
        pidLen = len(pidString) + 1
        pid = strings[pidIndex+pidLen:]

        try:
            os.kill(int(pid), signal.SIGINT)
        except:
            pass


    if hostsFile:
        try:
            f = open(hostsFile,'r')
        except:
            print 'No remote hosts to cleanup; file %s not found' % hostsFile
            sys.exit(0)
        hosts  = f.readlines()
        for host in hosts:
            host = host.strip()
            if host[0] != '#':

                if tmpDir and tmpDir != '/tmp':
                    cleanFile = '%s/mpd2.console_' % (tmpDir) + host + '_' + user + conExt

                cmd = '%s %s -n %s %s %s &' % (rshCmd, xOpt, host, cleanCmd, cleanFile)
                # print 'cmd=:%s:' % (cmd)
                os.system(cmd)

                if killMpdsOnAllHosts:

                    if tmpDir and tmpDir != '/tmp':
                        logFile = '%s/mpd2.logfile_' % (tmpDir) + host + '_' + user + conExt    

                    pid_obtainer = '%s %s -n %s %s %s' % (rshCmd, xOpt, host, pidCmd, logFile)
                    (shellIn, shellOut) = os.popen4(pid_obtainer)

#                    first_string = shellOut.readline()
#                    first_string = first_string.strip()
#                    pid = re.split(r'\s+', first_string)[5]
                    strings = shellOut.read()
                    try:
                        pidIndex = strings.index(pidString)
                    except:
                        print 'No pid in log file %s on host %s found' % (logFile, host)
                        sys.exit(-1)
                    pidLen = len(pidString) + 1
                    pid = strings[pidIndex+pidLen:]

                    killCmd = 'kill %s' % (pid)
                    killer = '%s %s -n %s %s &' % (rshCmd, xOpt, host, killCmd)

                    if subprocess_module_available:
                        killer = re.split(r'\s+', killer)
                        Popen(killer, bufsize=0, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
                    else:
                        Popen4(killer, 0)



def usage():
    print __doc__
    sys.exit(-1)


if __name__ == '__main__':
#    try:
#        mpdcleanup()
#    except SystemExit, errmsg:
#        pass
#    except mpdError, errmsg:
#        print 'mpdcleanup failed: %s' % (errmsg)
    mpdcleanup()
