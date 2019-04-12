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
usage: mpdsigjob  sigtype  [-j jobid OR -a jobalias] [-s|g] [-V or --version]
    sigtype must be the first arg
    jobid can be obtained via mpdlistjobs and is of the form:
        jobnum@mpdid where mpdid is mpd where first process runs, e.g.:
            1@linux02_32996 (may need \@ in some shells)
            1  is sufficient if you are on the machine where the job started
    one of -j or -a must be specified (but only one)
    -s or -g specify whether to signal the single user process or its group (default is g)
Delivers a Unix signal to all the application processes in the job

Copyright (C) 2003-2014 Intel Corporation.  All rights reserved.
"""
from time import ctime
__author__ = "Ralph Butler and Rusty Lusk"
__date__ = ctime()
__version__ = "$Revision: 9833 $"
__credits__ = ""


from os     import environ, getuid, close, path
from sys    import argv, exit
from socket import socket, fromfd, AF_UNIX, SOCK_STREAM
from signal import signal, SIG_DFL, SIGINT, SIGTSTP, SIGCONT, SIGALRM
from  mpdlib  import  mpd_set_my_id, mpd_uncaught_except_tb, mpd_print, \
                      mpd_handle_signal, mpd_get_my_username, MPDConClientSock, MPDParmDB

def mpdsigjob():
    import sys    # to get access to excepthook in next line
    sys.excepthook = mpd_uncaught_except_tb
    if len(argv) < 3 and not (len(argv) > 1 and (argv[1] == '-V'  or  argv[1] == '--version')) or  argv[1] == '-h'  or  argv[1] == '--help':
        usage()

    elif len(argv) > 1  and (argv[1] == '-V'  or  argv[1] == '--version'):
        vers = 'Version 4.1.3  Build 20140226'
        print 'Intel(R) MPI Library for Linux* OS, 32-bit applications,',vers
        print 'Copyright (C) 2003-2014 Intel Corporation.  All rights reserved.\n'
        if len(argv) < 3:
            exit(0)

    signal(SIGINT, sig_handler)
    mpd_set_my_id(myid='mpdsigjob')
    sigtype = argv[1]
    if sigtype.startswith('-'):
        sigtype = sigtype[1:]
    if sigtype.startswith('SIG'):
        sigtype = sigtype[3:]
    import signal as tmpsig  # just to get valid SIG's
    if sigtype.isdigit():
        if int(sigtype) > tmpsig.NSIG:
            print 'invalid signum: %s' % (sigtype)
            exit(-1)
    else:
        if not tmpsig.__dict__.has_key('SIG' + sigtype):
            print 'invalid sig type: %s' % (sigtype)
            exit(-1)
    jobalias = ''
    jobnum = ''
    mpdid = ''
    single_or_group = 'g'
    i = 2
    while i < len(argv):
        if argv[i] == '-a':
            if jobnum:      # should not have both alias and jobid

                print 'cannot specify both jobalias and jobid'

                usage()
            jobalias = argv[i+1]
            i += 1
            jobnum = '0'
        elif argv[i] == '-j':
            if jobalias:    # should not have both alias and jobid

                print 'cannot specify both jobalias and jobid'

                usage()
            jobid = argv[i+1]
            i += 1
            sjobid = jobid.split('@')
            jobnum = sjobid[0]
            if len(sjobid) > 1:
                mpdid = sjobid[1]
        elif argv[i] == '-s':
            single_or_group = 's'
        elif argv[i] == '-g':
            single_or_group = 'g'
        else:

            print 'unrecognized arg: %s' % (argv[i])

            usage()
        i += 1

    parmdb = MPDParmDB(orderedSources=['cmdline','xml','env','rcfile','thispgm'])
    parmsToOverride = {
                        'MPD_USE_ROOT_MPD'            :  0,
                        'MPD_SECRETWORD'              :  '',
                      }
    for (k,v) in parmsToOverride.items():
        parmdb[('thispgm',k)] = v
    parmdb.get_parms_from_env(parmsToOverride)
    parmdb.get_parms_from_rcfile(parmsToOverride)
    if getuid() == 0  or  parmdb['MPD_USE_ROOT_MPD']:
        fullDirName = path.abspath(path.split(argv[0])[0])  # normalize
        mpdroot = path.join(fullDirName,'mpdroot')
        conSock = MPDConClientSock(mpdroot=mpdroot,secretword=parmdb['MPD_SECRETWORD'])
    else:
        conSock = MPDConClientSock(secretword=parmdb['MPD_SECRETWORD'])

    msgToSend = {'cmd' : 'mpdsigjob', 'sigtype': sigtype, 'jobnum' : jobnum,
                 'mpdid' : mpdid, 'jobalias' : jobalias, 's_or_g' : single_or_group,
                 'username' : mpd_get_my_username() }
    conSock.send_dict_msg(msgToSend)
    msg = conSock.recv_dict_msg(timeout=5.0)
    if not msg:

        mpd_print(1,'no message received from the mpd daemon before timeout 5.0 sec')

    if msg['cmd'] != 'mpdsigjob_ack':
        if msg['cmd'] == 'already_have_a_console':
            mpd_print(1,'mpd already has a console (e.g. for long ringtest); try later')
        else:

            mpd_print(1,'unexpected message from the mpd daemon: %s' % (msg) )

        exit(-1)
    if not msg['handled']:
        print 'job not found'
        exit(-1)
    conSock.close()

def sig_handler(signum,frame):
    mpd_handle_signal(signum,frame)  # not nec since I exit next
    exit(-1)

def usage():
    print __doc__
    exit(-1)


if __name__ == '__main__':
    mpdsigjob()
