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
This program is not to be executed from the command line.  It is 
exec'd by mpdman to support mpigdb.
"""

# workaround to suppress deprecated module warnings in python2.6
# see https://trac.mcs.anl.gov/projects/mpich2/ticket/362 for tracking
import warnings
warnings.filterwarnings('ignore', '.*the popen2 module is deprecated.*', DeprecationWarning)

from time import ctime
__author__ = "Ralph Butler and Rusty Lusk"
__date__ = ctime()
__version__ = "$Revision: 7737 $"
__credits__ = ""


from sys    import argv, exit, stdin, stdout, stderr
from os     import kill, getpid, write, strerror, environ


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
        from popen2 import Popen4
        subprocess_module_available = 0
else:
    try:
        from popen2 import Popen4
        subprocess_module_available = 0
    except:
        from subprocess import Popen, PIPE, STDOUT
        subprocess_module_available = 1


from signal import signal, SIGUSR1, SIGINT, SIGKILL
from errno  import EINTR
from select import select, error

from re     import findall, sub, split

from mpdlib import mpd_set_my_id, mpd_print

global appPid, gdbPID


def sig_handler(signum,frame):
    global appPid, gdbPID
    if signum == SIGINT:
        try:
            kill(appPid,SIGINT)
        except:
            pass
    elif signum == SIGUSR1:
        try:
            kill(gdbPid,SIGKILL)
        except:
            pass
        try:
            kill(appPid,SIGKILL)
        except:
            pass


if __name__ == '__main__':    # so I can be imported by pydoc
    signal(SIGINT,sig_handler)
    signal(SIGUSR1,sig_handler)
    mpd_set_my_id('mpdgdbdrv')
    
    # print "RMB:GDBDRV: ARGS=", argv

    if argv[1] == '-attach': 
        gdb_args = '%s %s' % (argv[2],argv[3])  # userpgm and userpid  
    else: 

#        if len(argv) > 2: 
#            mpd_print(1, "when using gdb, pass cmd-line args to user pgms via the 'run' cmd") 
#            exit(-1) 
        gdb_args = argv[1] 
        if len(argv) > 2:
            args = ' '.join(argv[2:])
        else:
            args = ''


    tmp_cmd = 'gdb -q %s' % (gdb_args)
    if subprocess_module_available:
        tmp_cmd = split(r'\s+', tmp_cmd)
        gdb_info = Popen(tmp_cmd, bufsize=0, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    else:
        gdb_info = Popen4(tmp_cmd, 0 )

#    gdb_info = Popen4('gdb -q %s %s' % (argv[1],args), 0 ) # orig line

    gdbPid = gdb_info.pid
    # print "PID=%d GDBPID=%d" % (getpid(),gdbPid) ; stdout.flush()

    if subprocess_module_available:
        gdb_sin = gdb_info.stdin
        gdb_sout_serr = gdb_info.stdout
    else:
        gdb_sin = gdb_info.tochild
        gdb_sout_serr = gdb_info.fromchild

    gdb_sin_fileno = gdb_sin.fileno()
    gdb_sout_serr_fileno = gdb_sout_serr.fileno()
    write(gdb_sin_fileno,'set prompt (gdb)\\n\n')
    gdb_line = gdb_sout_serr.readline() 
    # check if gdb reports any errors  
    if findall(r'.*: No such file or directory.',gdb_line) != []: 
        print gdb_line, ; stdout.flush() 
        exit(-1) 
    mpd_print(0000, "LINE1=|%s|" % (gdb_line.rstrip()))
    write(gdb_sin_fileno,'set confirm off\n')
    gdb_line = gdb_sout_serr.readline() 
    mpd_print(0000, "LINE2=|%s|" % (gdb_line.rstrip()))
    write(gdb_sin_fileno,'handle SIGUSR1 nostop noprint\n')
    gdb_line = gdb_sout_serr.readline() 
    mpd_print(0000, "LINE3=|%s|" % (gdb_line.rstrip()))
    write(gdb_sin_fileno,'handle SIGPIPE nostop noprint\n')
    gdb_line = gdb_sout_serr.readline() 
    mpd_print(0000, "LINE4=|%s|" % (gdb_line.rstrip()))
    write(gdb_sin_fileno,'set confirm on\n')
    gdb_line = gdb_sout_serr.readline() 
    mpd_print(0000, "LINE5=|%s|" % (gdb_line.rstrip()))
    write(gdb_sin_fileno,'echo hi1\n')
    gdb_line = gdb_sout_serr.readline() 
    # mpd_print(0000, "LINE6=|%s|" % (gdb_line.rstrip()))
    # gdb_line = ''
    while not gdb_line.startswith('hi1'):
        gdb_line = gdb_sout_serr.readline() 
        mpd_print(0000, "LINEx=|%s|" % (gdb_line.rstrip()))
    

    if argv[1] != '-attach':


        if args:
            write(gdb_sin_fileno, 'set args %s\n' % (args))
            gdb_line = gdb_sout_serr.readline()

        write(gdb_sin_fileno,'b main\n')
        gdb_line = ''
        while not gdb_line.startswith('Breakpoint'):
            try:
                (readyFDs,unused1,unused2) = select([gdb_sout_serr_fileno],[],[],10)
            except error, data:
                if data[0] == EINTR:    # interrupted by timeout for example
                    continue
                else:
                    print 'mpdgdb_drv: main loop: select error: %s' % strerror(data[0])
            if not readyFDs:
                mpd_print(1, 'timed out waiting for initial Breakpoint response')
                exit(-1)
            gdb_line = gdb_sout_serr.readline()  # drain breakpoint response
            gdb_line = gdb_line.strip()
            mpd_print(0000, "gdb_line=|%s|" % (gdb_line.rstrip()))
        if not gdb_line.startswith('Breakpoint'):
            mpd_print(1, 'expecting "Breakpoint", got :%s:' % (gdb_line) )
            exit(-1)
        gdb_line = gdb_sout_serr.readline()  # drain prompt
        mpd_print(0000, "gdb_line=|%s|" % (gdb_line.rstrip()))
        if not gdb_line.startswith('(gdb)'):
            mpd_print(1, 'expecting "(gdb)", got :%s:' % (gdb_line) )
            exit(-1)
    
    print '(gdb)\n', ; stdout.flush()    # initial prompt to user
    
    user_fileno = stdin.fileno()
    while 1:
        try:
            (readyFDs,unused1,unused2) = select([user_fileno,gdb_sout_serr_fileno],[],[],1)
        except error, data:
            if data[0] == EINTR:    # interrupted by timeout for example
                continue
            else:
                mpd_print(1, 'mpdgdbdrv: main loop: select error: %s' % strerror(data[0]))
        # print "READY=", readyFDs ; stdout.flush()
        for readyFD in readyFDs:
            if readyFD == gdb_sout_serr_fileno:
                gdb_line = gdb_sout_serr.readline()
                if not gdb_line:
                    print "MPIGDB ENDING" ; stdout.flush()
                    exit(0)
                # print "LINE |%s|" % (gdb_line.rstrip()) ; stdout.flush()
                print gdb_line, ; stdout.flush()
            elif readyFD == user_fileno:
                user_line = stdin.readline()
                # print "USERLINE=", user_line, ; stdout.flush()
                if not user_line:
                    mpd_print(1, 'mpdgdbdrv: problem: expected user input but got none')
                    exit(-1)
                if user_line.startswith('r'): 
                    write(gdb_sin_fileno,'show prompt\n')
                    gdb_line = gdb_sout_serr.readline()
                    gdb_prompt = findall(r'Gdb\'s prompt is "(.+)"\.',gdb_line)
                    if gdb_prompt == []: 
                        mpd_print(1, 'expecting gdb\'s prompt, got :%s:' % (gdb_line))
                        exit(-1) 
                    gdb_prompt = gdb_prompt[0] 
                    # cut everything after first escape character (including it) 
                    p = gdb_prompt.find("\\") 
                    if p > 0: 
                        gdb_prompt = gdb_prompt[0:p] 
                    gdb_line = gdb_sout_serr.readline() # drain one line 
                         
                    write(gdb_sin_fileno,'show confirm\n') 
                    gdb_line = gdb_sout_serr.readline() 
                    gdb_confirm = findall(r'Whether to confirm potentially dangerous operations is (on|off)\.',gdb_line)
                    if gdb_confirm == []: 
                        mpd_print(1, 'expecting gdb\'s confirm state, got :%s:' % (gdb_line))
                        exit(-1) 
                    gdb_confirm = gdb_confirm[0] 
                    gdb_line = gdb_sout_serr.readline() # drain one line  
 
                    # set confirm to 'on' to get 'Starting program' message  
                    write(gdb_sin_fileno,'set confirm on\n') 
                    gdb_line = gdb_sout_serr.readline() 
 
                    # we have already set breakpoint 1 in main  
                    write(gdb_sin_fileno,user_line) 
                    # ignore any warnings befor starting msg  
                    while 1: 
                        gdb_line = gdb_sout_serr.readline()  # drain one line  
                        if not gdb_line.startswith('warning:'): 
                            break 
                        else: 
                            print gdb_line, ; stdout.flush() 
                    # drain starting msg  
                    if not gdb_line.startswith('Starting program'): 
                        mpd_print(1, 'expecting "Starting program", got :%s:' % \
                                  (gdb_line)) 
                        exit(-1) 
                    while 1:    # drain to a prompt 
                        gdb_line = gdb_sout_serr.readline()  # drain one line  
                        if gdb_line.startswith(gdb_prompt): 
                            break 
                    # try to get the pid  
                    write(gdb_sin_fileno,'info pid\n')  # macosx  
                    gdb_line = gdb_sout_serr.readline().lstrip() 
                    if gdb_line.find('process ID') >= 0:  # macosx  
                        appPid = findall(r'.* has process ID (\d+)',gdb_line) 
                        appPid = int(appPid[0]) 
                    else: 
                        while 1:    # drain to a prompt  
                            gdb_line = gdb_sout_serr.readline()  # drain one line  
                            if gdb_line.startswith(gdb_prompt): 
                                break 
                        write(gdb_sin_fileno,'info program\n') 
                        gdb_line = gdb_sout_serr.readline().lstrip() 
                        if gdb_line.startswith('Using'): 
                            if gdb_line.find('process') >= 0: 
                                appPid = findall(r'Using .* image of child process (\d+)',gdb_line) 
                            elif gdb_line.find('Thread') >= 0:  # solaris  
                                appPid = findall(r'Using .* image of child .* \(LWP (\d+)\).',gdb_line) 
                            else: 
                                mpd_print(1, 'expecting process or thread line, got :%s:' % \
                                          (gdb_line)) 
                                exit(-1) 
                            appPid = int(appPid[0]) 
                        else: 
                            mpd_print(1, 'expecting line with "Using"; got :%s:' % (gdb_line)) 
                            exit(-1) 
                    while 1:    # drain to a prompt  
                        gdb_line = gdb_sout_serr.readline()  # drain one line  
                        if gdb_line.startswith(gdb_prompt): 
                            break 
                    write(gdb_sin_fileno,'c\n') 
                    # set confirm back to original state  
                    write(gdb_sin_fileno,'set confirm %s\n' % (gdb_confirm)) 
                else: 
                    write(gdb_sin_fileno,user_line)
