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
usage: mpdkilljob  jobnum  [mpdid]  # as obtained from mpdlistjobs
   or: mpdkilljob  -a jobalias      # as obtained from mpdlistjobs
    mpdid is mpd where process with 'rank' 0 starts
    mpdid of form 1@linux02_32996 (may need \@ in csh)

Copyright (C) 2003-2014 Intel Corporation.  All rights reserved.
"""
from time import ctime
__author__ = "Ralph Butler and Rusty Lusk"
__date__ = ctime()
__version__ = "$Revision: 9831 $"
__credits__ = ""


import sys, os, signal

from  mpdlib  import  mpd_set_my_id, mpd_uncaught_except_tb, mpd_print, \
                      mpd_handle_signal, mpd_get_my_username, MPDConClientSock, MPDParmDB


def mpdkilljob():
    import sys    # to get access to excepthook in next line
    sys.excepthook = mpd_uncaught_except_tb
    if len(sys.argv) < 2  or  sys.argv[1] == '-h'  or  sys.argv[1] == '--help':
        usage()
    signal.signal(signal.SIGINT, sig_handler)
    mpd_set_my_id(myid='mpdkilljob')
    mpdid = ''
    if sys.argv[1] == '-a':
        jobalias = sys.argv[2]
        jobnum = '0'

    elif sys.argv[1] == '-V' or sys.argv[1] == '--version':
        vers = 'Version 5.0 Update 1  Build 20140709'
        print 'Intel(R) MPI Library for Linux* OS, 64-bit applications,',vers
        print 'Copyright (C) 2003-2014 Intel Corporation.  All rights reserved.\n'
        sys.exit(0)

    else:
        jobalias = ''
        jobid = sys.argv[1]
        sjobid = jobid.split('@')
        jobnum = sjobid[0]
        if len(sjobid) > 1:
            mpdid = sjobid[1]

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

    msgToSend = { 'cmd':'mpdkilljob', 'jobnum' : jobnum, 'mpdid' : mpdid,
                  'jobalias' : jobalias, 'username' : mpd_get_my_username() }
    conSock.send_dict_msg(msgToSend)
    msg = conSock.recv_dict_msg(timeout=5.0)
    if not msg:

        mpd_print(1,'no message received from the mpd daemon before timeout 5.0 sec')

        sys.exit(-1)
    if msg['cmd'] != 'mpdkilljob_ack':
        if msg['cmd'] == 'already_have_a_console':
            print 'mpd already has a console (e.g. for long ringtest); try later'
        else:
            print 'unexpected message from mpd: %s' % (msg)
        sys.exit(-1)
    if not msg['handled']:
        print 'job not found'
        sys.exit(-1)
    conSock.close()

def sig_handler(signum,frame):
    mpd_handle_signal(signum,frame)  # not nec since I exit next
    sys.exit(-1)

def usage():
    print __doc__
    sys.exit(-1)

if __name__ == '__main__':
    mpdkilljob()
