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
usage: mpdlistjobs [-u | --user=username] [-a | --alias=jobalias] [-j | --jobid=jobid] [-V | --version]
    (only use one of jobalias or jobid)'
lists jobs being run by an mpd ring, all by default, or filtered'
    by user, mpd job id, or alias assigned when the job was submitted'

Copyright (C) 2003-2014 Intel Corporation.  All rights reserved.
"""
from time import ctime
__author__ = "Ralph Butler and Rusty Lusk"
__date__ = ctime()
__version__ = "$Revision: 9833 $"
__credits__ = ""


import sys, os, signal, socket

from  mpdlib  import  mpd_set_my_id, mpd_uncaught_except_tb, mpd_print, \
                      mpd_handle_signal, mpd_get_my_username, MPDConClientSock, MPDParmDB

def mpdlistjobs():
    import sys    # to get access to excepthook in next line
    sys.excepthook = mpd_uncaught_except_tb
    signal.signal(signal.SIGINT, sig_handler)
    mpd_set_my_id(myid='mpdlistjobs')
    uname    = ''
    jobid    = ''
    sjobid   = ''
    jobalias = ''
    sssPrintFormat = 0
    if len(sys.argv) > 1:
        aidx = 1
        while aidx < len(sys.argv):
            if sys.argv[aidx] == '-h'  or  sys.argv[aidx] == '--help':
                usage()
            if sys.argv[aidx] == '-u':    # or --user=
                
                try:

                    uname = sys.argv[aidx+1]

                    aidx += 2
                except:
                    print 'mpdlistjobs: not enough arguments. need username'
                    usage()
                #I_MPI END
            elif sys.argv[aidx].startswith('--user'):
                splitArg = sys.argv[aidx].split('=')
                try:
                    uname = splitArg[1]
                except:
                    print 'mpdlistjobs: invalid argument:', sys.argv[aidx]
                    usage()
                aidx += 1
            elif sys.argv[aidx] == '-j':    # or --jobid=
                
                try:

                    jobid = sys.argv[aidx+1]

                    aidx += 2
                except:
                    print 'mpdlistjobs: not enough arguments. need jobid'
                    usage()
                #I_MPI END
                sjobid = jobid.split('@')    # jobnum and originating host
            elif sys.argv[aidx].startswith('--jobid'):
                splitArg = sys.argv[aidx].split('=')
                try:
                    jobid = splitArg[1]
                    sjobid = jobid.split('@')    # jobnum and originating host
                except:
                    print 'mpdlistjobs: invalid argument:', sys.argv[aidx]
                    usage()
                aidx += 1
            elif sys.argv[aidx] == '-a':    # or --alias=
                
                try:

                    jobalias = sys.argv[aidx+1]

                    aidx += 2
                except:
                    print 'mpdlistjobs: not enough arguments. need jobalias'
                    usage()
                
            elif sys.argv[aidx].startswith('--alias'):
                splitArg = sys.argv[aidx].split('=')
                try:
                    jobalias = splitArg[1]
                except:
                    print 'mpdlistjobs: invalid argument:', sys.argv[aidx]
                    usage()
                aidx += 1
            elif sys.argv[aidx] == '--sss':
                sssPrintFormat = 1
                aidx +=1

            elif sys.argv[aidx] == '-V' or sys.argv[aidx] == '--version':
                vers = 'Version 4.1.3  Build 20140226'
                print 'Intel(R) MPI Library for Linux* OS, 32-bit applications,',vers
                print 'Copyright (C) 2003-2014 Intel Corporation.  All rights reserved.\n'
                if len(sys.argv) < 3:
                    sys.exit(0)

            else:
                print 'unrecognized arg: %s' % sys.argv[aidx]
                sys.exit(-1)

    parmdb = MPDParmDB(orderedSources=['cmdline','xml','env','rcfile','thispgm'])
    parmsToOverride = {
                        'MPD_USE_ROOT_MPD'            :  0,
                        'MPD_SECRETWORD'              :  '',
                      }
    for (k,v) in parmsToOverride.items():
        parmdb[('thispgm',k)] = v
    parmdb.get_parms_from_env(parmsToOverride)
    parmdb.get_parms_from_rcfile(parmsToOverride)
    if (hasattr(os,'getuid')  and  os.getuid() == 0)  or  parmdb['MPD_USE_ROOT_MPD']:
        fullDirName = os.path.abspath(os.path.split(sys.argv[0])[0])  # normalize
        mpdroot = os.path.join(fullDirName,'mpdroot')
        conSock = MPDConClientSock(mpdroot=mpdroot,secretword=parmdb['MPD_SECRETWORD'])
    else:
        conSock = MPDConClientSock(secretword=parmdb['MPD_SECRETWORD'])

    msgToSend = { 'cmd' : 'mpdlistjobs' }
    conSock.send_dict_msg(msgToSend)
    msg = conSock.recv_dict_msg(timeout=5.0)
    if not msg:

        mpd_print(1,'no message received from the mpd daemon before timeout 5.0 sec')

    if msg['cmd'] != 'local_mpdid':     # get full id of local mpd for filters later

        mpd_print(1,'did not recv local_mpdid message from local mpd; got: %s' % msg)

    else:
        if len(sjobid) == 1:
            sjobid.append(msg['id'])
    done = 0
    while not done:
        msg = conSock.recv_dict_msg()
        if not msg.has_key('cmd'):

            mpd_print(1,'invalid message from the mpd daemon :%s:' % (msg) )

            sys.exit(-1)
        if msg['cmd'] == 'mpdlistjobs_info':
            smjobid = msg['jobid'].split('  ')  # jobnum, mpdid, and alias (if present)
            if len(smjobid) < 3:
                smjobid.append('')
            print_based_on_uname    = 0    # default
            print_based_on_jobid    = 0    # default
            print_based_on_jobalias = 0    # default
            if not uname  or  uname == msg['username']:
                print_based_on_uname = 1
            if not jobid  and  not jobalias:
                print_based_on_jobid = 1
                print_based_on_jobalias = 1
            else:
                if sjobid  and  sjobid[0] == smjobid[0]  and  sjobid[1] == smjobid[1]:
                    print_based_on_jobid = 1
                if jobalias  and  jobalias == smjobid[2]:
                    print_based_on_jobalias = 1
            if not smjobid[2]:
                smjobid[2] = '          '  # just for printing
            if print_based_on_uname and (print_based_on_jobid or print_based_on_jobalias):
                if sssPrintFormat:
                    print "%s %s %s"%(msg['host'],msg['clipid'],msg['sid'])
                else:
                    print 'jobid    = %s@%s' % (smjobid[0],smjobid[1])
                    print 'jobalias = %s'    % (smjobid[2])
                    print 'username = %s'    % (msg['username'])
                    print 'host     = %s'    % (msg['host'])
                    print 'pid      = %s'    % (msg['clipid'])
                    print 'sid      = %s'    % (msg['sid'])
                    print 'rank     = %s'    % (msg['rank'])
                    print 'pgm      = %s'    % (msg['pgm'])
                    print
        else:  # mpdlistjobs_trailer
            done = 1
    conSock.close()

def sig_handler(signum,frame):
    mpd_handle_signal(signum,frame)  # not nec since I exit next
    sys.exit(-1)

def usage():
    print __doc__
    sys.exit(-1)

if __name__ == '__main__':
    mpdlistjobs()
