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
exec'd by mpdroot to verify the version of python before executing
a 'regular' mpd pgm, e.g. mpdallexit.
"""

from sys import version, exit
if version[0] == '1' and version[1] == '.':
    print "mpdchkpyver: your python version must be >= 2.2 ;"
    print "  current version is:", version
    exit(-1)

##  These must be after 1.x version check
from time import ctime
__author__ = "Ralph Butler and Rusty Lusk"
__date__ = ctime()
__version__ = "$Revision: 3984 $"
__credits__ = ""

from sys     import argv, exit
from os      import environ, execvpe
from mpdlib  import mpd_check_python_version

if __name__ == '__main__':
    if len(argv) == 1  or  argv[1] == '-h'  or  argv[1] == '--help':
        print __doc__
        exit(-1)
    else:
        vinfo = mpd_check_python_version()
        if vinfo:
            print "mpdchkpyver: your python version must be >= 2.2 ; current version is:", vinfo
            exit(-1)
        if len(argv) > 1:
            mpdpgm = argv[1] + '.py'
            # print "CHKPYVER: PGM=:%s: ARGV[1:]=:%s:" % (mpdpgm,argv[1:])
            try:
                execvpe(mpdpgm,argv[1:],environ)    # client
            except Exception, errinfo:
                print 'mpdchkpyver: failed to exec %s; info=%s' % (mpdpgm,errinfo)
                exit(-1)
