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
usage: mpd [--host=<host> --port=<portnum>] [--noconsole]
           [--trace] [--echo] [--daemon] [--bulletproof] --ncpus=<ncpus>
           [--ifhn=<interface-hostname>] [--listenport=<listenport>]
           [--pid=<pidfilename>] [--tmpdir=<tmpdir>] [-zc] [--debug] [--version]

Some long parameter names may be abbreviated to their first letters by using
  only one hyphen and no equal sign:
     mpd -h donner -p 4268 -n
  is equivalent to
     mpd --host=magpie --port=4268 --noconsole

--host and --port must be specified together; they tell the new mpd where
  to enter an existing ring;  if they are omitted, the new mpd forms a
  stand-alone ring that other mpds may enter later
--noconsole is useful for running 2 mpds on the same machine; only one of
  them will accept mpd commands
--trace yields lots of traces thru mpd routines; currently too verbose
--debug turns on some debugging prints; currently not verbose enough
--echo causes the mpd echo its listener port by which other mpds may connect
--daemon causes mpd to run backgrounded, with no controlling tty
--bulletproof says to turn bulletproofing on (experimental)
--ncpus indicates how many cpus are on the local host; used for starting processes
--ifhn specifies an alternate interface hostname for the host this mpd is running on;
  e.g. may be used to specify the alias for an interface other than default
--listenport specifies a port for this mpd to listen on; by default it will
  acquire one from the system
--conlistenport specifies a port for this mpd to listen on for console
  connections (only used when employing inet socket for console); by default it
  will acquire one from the system
--pid=filename writes the mpd pid into the specified file, or --pid alone
  writes it into /var/run/mpd.pid
--tmpdir=tmpdirname where mpd places temporary sockets, etc.
-zc is a purely EXPERIMENTAL option right now used to investigate zeroconf
  networking; it can be used to allow mpds to discover each other locally
  using multicast DNS; its usage may change over time
  Currently, -zc is specified like this:  -zc N
  where N specifies a 'level' in a startup set of mpds.  The first mpd in a ring
  must have 1 and it will establish a ring of one mpd.  Subsequent mpds can specify
  -zc 2 and will hook into the ring via the one at level 1.  Except for level 1, new
  mpds enter the ring via an mpd at level-1.
--version prints version information

A file named .mpd.conf file must be present in the user's home directory
  with read and write access only for the user, and must contain at least
  a line with MPD_SECRETWORD=<secretword>

To run mpd as root, install it while root and instead of a .mpd.conf file
use mpd.conf (no leading dot) in the /etc directory.' 

Copyright (C) 2003-2014 Intel Corporation.  All rights reserved.
"""
from  time    import  ctime
from  mpdlib  import  mpd_version
__author__ = "Ralph Butler and Rusty Lusk"
__date__ = ctime()
__version__ = "$Revision: 9831 $"
__version__ += "  " + str(mpd_version())
__credits__ = ""


import sys, os, signal, socket, stat


from glob     import glob

from  re          import  sub
from  atexit      import  register
from  cPickle     import  dumps
from  types       import  ClassType
from  random      import  seed, randrange, random
from  time        import  sleep

try:
    from hashlib      import md5 as md5new
except:
    from  md5         import  new as md5new

from  mpdlib      import  mpd_set_my_id, mpd_check_python_version, mpd_sockpair, \
                          mpd_print, mpd_get_my_username, mpd_close_zc, \
                          mpd_get_groups_for_username, mpd_uncaught_except_tb, \
                          mpd_set_procedures_to_trace, mpd_trace_calls, mpd_which, \
                          mpd_dbg_level, mpd_set_dbg_level, mpd_set_tmpdir, \
                          MPDSock, MPDListenSock, MPDConListenSock, \
                          MPDStreamHandler, MPDRing, MPDParmDB
from  mpdman      import  MPDMan

from errno import ENOENT


# fix for ticket #753 where the set() builtin isn't available in python2.3
try:
    set
except NameError:
    from sets import Set as set


try:
    import pwd
    pwd_module_available = 1
except:
    pwd_module_available = 0
try:
    import  syslog
    syslog_module_available = 1
except:
    syslog_module_available = 0
try:
    import  subprocess
    subprocess_module_available = 1
except:
    subprocess_module_available = 0


# MPD pinning support functions.

#################################
# Add two lists by members
#
def pin_Add_list(l1,l2,space):
    list = []
    l1j = pin_Justify_list(l1,space)
    l2j = pin_Justify_list(l2,space)
    for i in xrange(space):
        list.append(l1j[i]+l2j[i])

    return list

#################################
# Join three lists by members
#
def pin_Join_list(l1,l2,l3,space):
    list = []
    l1j = pin_Justify_list(l1,space)
    l2j = pin_Justify_list(l2,space)
    l3j = pin_Justify_list(l3,space)
    for i in xrange(space):
        list.append(l1j[i]+l2j[i]+l3j[i])

    return list

#################################
# Justify list to right
#
def pin_Justify_list(lin,space):
    s = len(lin[space-1])
    for i in xrange(space-1):
        if s < len(lin[i]): s = len(lin[i])
    
    list = []
    for i in xrange(space):
        list.append(lin[i].rjust(s))

    return list

#################################
# Create list of unique member index of non-empty list
#
def pin_Uni_index_list(list,space):
    ulist = []
    for i in xrange(space):
        if (list[i] == '*'):
            continue
        if list.index(list[i]) == i:
            ulist.append(i) 

    return ulist

#################################
# Create list of unique member index of non-empty list
#
def pin_Uni_index_list_ordered(list,space,n):
    ulist = []
    for j in range(n):
        for i in xrange(space):
            if (list[i] == '*'):
                continue
            if (list.index(list[i]) == i) and (list[i] == j):
                ulist.append(i) 

    return ulist

#################################
# Determine # of unique members of non-empty list
#
def pin_Uni_num(list,space):
    num = 0
    for i in xrange(space):
        if list.index(list[i]) == i:
            num += 1 

    return num

#################################
# Determine # of unique members of two non-empty lists
#
def pin_Uni_num2(l1,l2,space):
    list = pin_Add_list(l1,l2,space)
    num = pin_Uni_num(list,space)

    return num

#################################
# Determine current pinning mode
#
def pin_Mode(env,case,space):
    # do we have ehough space?
    if space < 2:
        return 'na'

    if env.has_key('I_MPI_PIN'):
        pin = env['I_MPI_PIN']
        if pin == 'disable' or pin == 'off' or pin == 'no' or pin == '0':
            return 'off'

    if env.has_key('I_MPI_PIN_MODE'):
        # mode defined by user
        mode = env['I_MPI_PIN_MODE']
        if mode == 'lib':
            pass
        elif mode == 'mpd':
            mode = case
        else:
            mode = 'off'
    # mode by default
    elif case == 'sgi3' or case == 'sgi4':
        mode = case
    else:
        mode = 'lib'

    return mode

#################################
# PinOption 
#
def pin_Option(env,case,info,nrank):
    option = {
        'case'       : '',
        'space'      : 0,
        'ncore'      : 1,
        'nrank'      : 1,
        'kind'       : 'multi',
        'meth'       : 'generic',
        'omp'        : '',
        'mode'       : 'lib',
        'disp'       : 'compact',
        'cell'       : '',
        'grain'      : 1,
        'offset'     : 0,
        'shift'      : 1,
        'shape'      : '0',
        'size'       : 1,
        'u_ord'      : [],
        'c_ord'      : [],
        'domain'     : '',
        'list'       : 'map=spread',
        'ords'       : {},
        }

    option['case']  = case
    option['space'] = info['lcpu']
    option['ncore'] = info['cores']
    option['nrank'] = nrank
    option['mode']  = pin_Mode(env,case,info['lcpu'])
    option['ords']  = pin_Ordering(info, option['space'])
    
    if env.has_key('I_MPI_PIN_PROCS'):
        option['kind'] = 'single'
        option['list'] = env['I_MPI_PIN_PROCS']

    if env.has_key('I_MPI_PIN_PROCESSOR_LIST'):
        option['kind'] = 'single'
        option['list'] = env['I_MPI_PIN_PROCESSOR_LIST']

    if env.has_key('I_MPI_PIN_DOMAIN'):
        option['domain'] =  env['I_MPI_PIN_DOMAIN']
    elif 2*nrank <= option['space']:
        option['domain'] = 'auto'

    if env.has_key('OMP_NUM_THREADS'):
        option['omp'] = env['OMP_NUM_THREADS']

    if env.has_key('I_MPI_PIN_ORDER'):
        option['disp'] =  env['I_MPI_PIN_ORDER']

    if env.has_key('I_MPI_PIN_CELL'):
        option['cell'] =  env['I_MPI_PIN_CELL']

    if env.has_key('I_MPI_PIN_OFFSET'):
        offset = env['I_MPI_PIN_OFFSET']
        if offset.isdigit():
            option['offset'] = int(offset)
        else:
            mpd_print(1,'MPD: incorrect I_MPI_PIN_OFFSET setting: %s. Assume 0' % (offset))

    return option

### build the domain
def pin_domain_build(blist,clist,space):
    domset = {}
    for i in xrange(len(blist)):
        base = clist[blist[i]]
        domset[i] = []
        for p in xrange(space):
            if clist[p] == base:
                domset[i].append(str(p))

    return domset
####

#################################
# Prepare set of domains
#
def pin_DomainSet(option,info):
    if option['case'] == 'sgi3' or option['case'] == 'sgi4':
        return {}
    if not option['space']:
        return {}
    if option['kind'] == 'single':
        return {}

    dom = option['domain']
    if not dom:
        return {}

    space = option['space']

    if dom[0] == '[' and dom.find(']') != -1:
    # Special case - Explicit domain mask
        ml = dom[1:dom.find(']')].split(',')
        clist = []
        # init clist
        for i in xrange(space):
            clist.append(len(ml))
        try:
            for i in xrange(len(ml)):
                m = int(ml[i],16)
                for p in xrange(space):
                    if not m: break
                    if m & 1:
                        clist[p] = i
                    m = m >> 1
        except Exception:
            mpd_print(1,'MPD: incorrect I_MPI_PIN_DOMAIN setting: %s' % (ml[i]))
            return {}

        blist = pin_Uni_index_list_ordered(clist,space,len(ml))
        return pin_domain_build(blist,clist,space)
    # Special case - end
    
    idx = dom.find(':')
    if idx == -1:   # singular value
        arg = dom
        layout = 'compact'
    else:           # size:layout value
        arg = dom[:idx]
        layout = dom[idx+1:]
        if arg == 'omp' or arg == 'auto' or arg.isdigit(): pass
        else:
            mpd_print(1,'MPD: incorrect I_MPI_PIN_DOMAIN setting: %s' % (dom))

### Indirect domain definition
    if arg == 'omp':        # OMP interpretation
        arg = option['omp']
        if not arg:
            arg = 'node'
    elif arg == 'auto':     # AUTO interpretation
        if option['nrank'] == 0:
            arg = 'node'
        else:
            if (option['cell'] == 'core'):
                scale = option['ncore']
            else:
                scale = space
            arg = str(scale/option['nrank'])
    elif arg == 'cache':    # CACHE interpretation
        n = min(info['cache1'],info['cache2'],info['cache3'])        
        if n == info['cache1']:   arg = 'cache1'
        elif n == info['cache2']: arg = 'cache2'
        else:                     arg = 'cache3'
    elif arg == 'cell':    # CELL interpretation
        if (option['cell'] == 'core'): arg = 'core'
        else:                          arg = 'unit'
    else: pass

    # clist init
    clist = []
    for i in xrange(space):
        clist.append('*')

    # cell setting check
    if (option['cell'] == 'core'):
        order = option['ords']['nub']
    else:
        order = option['ords']['log']

    lord = len(order)

### Direct domain definition
    if arg.isdigit():
    # domain=size:layout
        d = int(arg)
        if d < 1 or d > space: d = space

        if layout == 'compact':
            ordlay = order
        elif layout == 'scatter':
            ordlay = pin_Scatter(order, info, lord)
        else:
            ordlay = range(lord)

        for i in xrange(lord):
            clist[ordlay[i]] = i/d

    else:
    # Multi-core shape
        if arg == 'unit':
            list = pin_Join_list(info['pack_id'],info['core_id'],info['thread_id'],space)
        elif arg == 'core':
            list = pin_Add_list(info['pack_id'],info['core_id'],space)
        elif arg == 'cache1':
            list = info['cache1_id']
        elif arg == 'cache2':
            list = info['cache2_id']
        elif arg == 'cache3':
            list = info['cache3_id']
        elif arg == 'sock' or arg == 'socket':
            list = info['pack_id']
        elif arg == 'node':
            list = []
            for i in xrange(space):
                list.append('0')
        else:
            mpd_print(1,'MPD: incorrect I_MPI_PIN_DOMAIN setting: %s' % (arg))
            return {}

        # build clist for multi-core
        for i in xrange(lord):
            clist[order[i]] = list[order[i]]

    # build list of uni indexes
    blist = pin_Uni_index_list(clist,space)
    # build set of domains
    domset = pin_domain_build(blist,clist,space)

    if option['disp'] == 'compact':
        ordmap = order;
    elif option['disp'] == 'scatter':
        ordmap = pin_Scatter(order, info, lord)
    elif option['disp'] == 'range':
        ordmap = range(lord)
    else:
        mpd_print(1,'MPD: incorrect I_MPI_PIN_ORDER setting: %s. Assume "range"' % (disp))
        return domset
    
    domval = domset.values()
    domlen = len(blist)
    j = (domlen-option['offset']%domlen)%domlen
    for p in xrange(len(ordmap)):
        base = ordmap[p]
        for i in xrange(domlen):
            if (int(domval[i][0]) == base):
                domset[j] = domval[i]
                j = (j+1)%domlen

    return domset
# pin_DomainSet
#################################

#################################
# Prepare list of CPUs for pinning
#
def pin_CpuList(option,info):
    space = option['space']
    nrank = option['nrank']
    arg   = option['list']

    if not space or nrank <=0:
        return []

    if arg[0].isdigit(): return pin_DigitList(arg,space)

#### environment variable value parsing
    clist = arg.split(':')
    if len(clist) == 2:
        key = clist[0]
        arg = clist[1]
    elif len(clist) == 1:
        if clist[0] == 'all' or clist[0] == 'allcores' or clist[0] == 'allsocks':
            key = clist[0]
            arg = ''
        else:
            arg = clist[0]
            if option['cell'] == 'core':
                key = 'allcores'
            elif option['cell'] == 'unit':
                key = 'all'
            else: # default cell
                if nrank > info['cores']:
                    key = 'all'
                elif nrank > info['packs']:
                    key = 'allcores'
                else:
                    key = 'allsocks'
    else:
        mpd_print(1, 'MPD: incorrect I_MPI_PIN_PROCESSOR_LIST subset: %s' % (arg))
#        print 'MPD: incorrect I_MPI_PIN_PROCESSOR_LIST setting: %s' % (arg)
        return []

#### 'preoffset=' parameter
    val = ['0']  # default value
    idx = arg.find('preoffset=')
    if idx == 0:
        val = arg[10:].split(',')
    elif idx > 0:
        if arg[idx-1] == ',':
            val = arg[idx+10:].split(',')
    spre = val[0]

#### 'postoffset=' parameter
    val = ['0']  # default value
    idx = arg.find('offset=')
    idy = arg.find('postoffset=')
    if idx >= 0 or idy >= 0:
        if idy == 0:
            val = arg[11:].split(',')
        elif idy > 0:
            if arg[idy-1] == ',':
                val = arg[idy+11:].split(',')
        elif idx == 0:
            val = arg[7:].split(',')
        elif idx > 0:
            if arg[idx-1] == ',':
                val = arg[idx+7:].split(',')
    spost = val[0]

#### 'shift=' parameter
    val = ['fine']
    idx = arg.find('shift=')
    if idx == 0:
        val = arg[6:].split(',')
    elif idx > 0:
        if arg[idx-1] == ',':
            val = arg[idx+6:].split(',')
    sshift = val[0]

#### 'grain=' parameter
    val = ['fine']
    idx = arg.find('grain=')
    if idx == 0:
        val = arg[6:].split(',')
    elif idx > 0:
        if arg[idx-1] == ',':
            val = arg[idx+6:].split(',')
    sgrain = val[0]

#### 'map=' parameter
    idx = arg.find('map=')
    if idx != -1:
        smap = arg[idx+4:]
    else:
        smap = ''

#### create tree ordered lists
#    ords = pin_Ordering(info, space)
    ords = option['ords']

    if key == 'all':        # procset = all logical CPUs
        nres = 5
        scale = info['lcpu']
        order = ords['log']
    elif key == 'allcores': # procset = all cores
        nres = 4
        scale = info['cores']
        order = ords['nub']
#        corelist = pin_Add_list(ords['pack'], ords['core'], space)
#        ind = pin_Uni_index_list(corelist,space)
#        order = []
#        for i in xrange(len(ind)):
#            order.append(ords['log'][ind[i]])
    elif key == 'allsocks': # procset = all sockets
        nres = 1
        scale = info['packs']
        ind = pin_Uni_index_list(ords['pack'],space)
        order = []
        for i in xrange(len(ind)):
            order.append(ords['log'][ind[i]])
    else:
        mpd_print(1, 'MPD: incorrect I_MPI_PIN_PROCESSOR_LIST subset: %s' % (key))
#        print 'MPD: incorrect I_MPI_PIN_PROCESSOR_LIST subset: %s' % (key)
        return []

#### map interface
    if   smap == 'spread':  return pin_Spread(order, info, scale, nrank, nres)
    elif smap == 'bunch':   return pin_Bunch(order, info, scale, nrank)
    elif smap == 'scatter': return pin_Scatter(order, info, scale)

#### grain/shift/offset interface
    sockgrain = scale/info['packs']

    grain = pin_Parsing(sgrain,1,sockgrain+1,scale,info)
    if scale % grain:
        mpd_print(1, 'MPD: incorrect grain value: %d, should be multiple of %d' % (grain, scale))
#        print 'MPD: incorrect grain value: %d, should be multiple of %d' % (grain, scale)
        grain = 1

    grainamount = scale/grain
    shift      = pin_Parsing(sshift,1,grainamount+1,grainamount,info)
    preoffset  = pin_Parsing(spre,0,grainamount,grainamount,info)
    postoffset = pin_Parsing(spost,0,grainamount,grainamount,info)

    return pin_Offset(pin_Shift(pin_Offset(order, grain, preoffset), grain, shift), grain, postoffset)

# pin_CpuList
#################################

#################################
# grain/shift/offset parsing
#
def pin_Parsing(arg,minarg,maxarg,maxq,info):
    if not arg: return minarg

    if arg.isdigit() and len(arg) < 5: iarg = int(arg)
    else:
        if   arg == 'fine':   quant = maxq
        elif arg == 'core':   quant = info['cores']
        elif arg == 'cache1': quant = info['cache1']
        elif arg == 'cache2': quant = info['cache2']
        elif arg == 'cache3': quant = info['cache3']
        elif arg == 'cache':  quant = min(info['cache1'],info['cache2'],info['cache3'])
        elif arg == 'socket' or arg == 'sock': quant = info['packs']
        # socket pieces
        elif arg == 'half'   or arg == 'mid' : quant = 2*info['packs']
        elif arg == 'third':  quant = 3*info['packs']
        elif arg == 'quater': quant = 4*info['packs']
        elif arg == 'octavo': quant = 8*info['packs']
        # fine granularity
        else: return minarg
        iarg = maxq/quant

    iarg = iarg % maxarg
    if iarg < minarg: iarg = minarg

    return iarg
# pin_Parsing
#################################

#################################
# Round robin shift of a list
#
def pin_Shift(list,grain,shift):
    if not list or shift <= 1:
        return list

    end = len(list)
    out = []
    j = 0
    beg = j
    stride = grain*shift
    for i in xrange(0,end,grain):
        out.extend(list[j:j+grain])
        j = j + stride
        if j + grain > end:
            j = beg + grain
            beg = j
    return out
# pin_Shift
#################################

#################################
# Cyclic shift of a list
#
def pin_Offset(list,grain,offset):
    if not list or offset <= 0:
        return list

    offs = offset*grain
    if offs:
        dup = list
        list = []
        list.extend(dup[offs:])
        list.extend(dup[:offs])
    return list
# pin_Offset
##################################

#################################
# Ordered lists build
#
def pin_Ordering(info, space):
    ords = {'log': [], 'nub': [], 'proc': [], 'core': [], 'pack': []}
#    pid = pin_Justify_list(info['pack_id'],space)
#    cid = pin_Justify_list(info['core_id'],space)
#    tid = pin_Justify_list(info['thread_id'],space)
#    ids = pin_Join_list(pid,cid,tid,space)
    ids = pin_Join_list(info['pack_id'],info['core_id'],info['thread_id'],space)
    ordids = []
    ordids.extend(ids)
    ordids.sort()
    for i in xrange(space):
        for j in xrange(space):
            if ids[j] == ordids[i]: break
        ords['log'].append(j)
        ords['proc'].append(info['thread_id'][j])
        ords['core'].append(info['core_id'][j])
        ords['pack'].append(info['pack_id'][j])

    corelist = pin_Add_list(ords['pack'], ords['core'], space)
    ind = pin_Uni_index_list(corelist,space)
    for i in xrange(len(ind)):
        ords['nub'].append(ords['log'][ind[i]])

    return ords
# pin_Ordering
#################################

#################################
# build scatter list
#
def pin_Scatter(order, info, scale):
    if scale == info['packs'] or info['stat'] != 'ok':
        return order

    per_pack = scale/info['packs']
    per_cache3 = scale/info['cache3']
    per_cache2 = scale/info['cache2']
    per_core = scale/info['cores']

    list = []
    for it in xrange(per_core):
        for ic in xrange(0,per_cache2,per_core):
            for ich2 in xrange(0,per_cache3,per_cache2):
                for ich3 in xrange(0,per_pack,per_cache3):
                    for ip in xrange(0,scale,per_pack):
                        j = ip + ich3 + ich2 + ic + it
                        list.append(order[j])

    return list
# pin_Scatter
#################################

#################################
# build bunch list
#
def pin_Bunch(order,info,scale,nrank):
    if nrank >= scale:
        return order

    j = 0
    list = []
    base = nrank/info['packs']
    extra = nrank%info['packs']
    step = scale/info['packs']

    if extra:
        for i in xrange(extra):
            list.extend(order[j:j+base+1])
            j = j + step
    if base:
        for i in xrange(extra,info['packs']):
            list.extend(order[j:j+base])
            j = j + step

    return list

# pin_Bunch
#################################

#################################
# build spread list
#
def pin_Spread(order,info,scale,procs,nres):
    if scale == info['packs'] or info['stat'] != 'ok':
        return order

    if procs > scale: procs = scale
    per_pack = procs/info['packs']
    extra_per_pack = procs%info['packs']
    scale_per_pack = scale/info['packs']

    res = range(5)
    res[0] = 1
    res[1] = info['cache3']/info['packs']
    res[2] = info['cache2']/info['packs']
    res[3] = info['cores']/info['packs']
    res[4] = info['lcpu']/info['packs']
    for i in xrange(1,5):
        if res[i-1] > res[i]:
            return order
#    res.sort()
    offs = 0
    list = []

    if extra_per_pack:
        for i in xrange(extra_per_pack):    # packs with extra rank
            list.extend(pin_SpreadExtent(res, nres, per_pack+1, scale_per_pack, order, offs))
            offs += scale_per_pack

    if per_pack:
        for i in xrange(extra_per_pack,info['packs']):
            list.extend(pin_SpreadExtent(res, nres, per_pack, scale_per_pack, order, offs))
            offs += scale_per_pack

    return list

# pin_Spread
#################################

#################################
# Next spread list extent
#
def pin_SpreadExtent(res, nres, pos, pack, lord, beg):
    if pos == res[nres-1]:  # full loading of the pack with current granularity. exact value
        nbox = res[nres-1]
        step = 1
    else:
        for r in xrange(1,nres):
            if res[r-1] <= pos and pos < res[r]: break
        else:
            mpd_print(1, 'MPD: internal topology error #1')
#            print 'Internal Error: No1', r, nres, pos
            return []

        nbox = res[r-1]
        step = pack/res[r]

    base = pos/nbox
    extra = pos%nbox
    stride = pack/nbox

    start = beg
    list = []
    if extra:
        for k in xrange(extra): # by base+1
            j = start
            for m in xrange(base+1):
                list.append(lord[j])
                j = j + step
            start = start + stride
    if base:
        for k in xrange(extra,nbox): # by base
            j = start
            for m in xrange(base):
                list.append(lord[j])
                j = j + step
            start = start + stride

    return list
# pin_SpreadExtent
#################################

#################################
# Digit list of CPUs for pinning
#
def pin_DigitList(arg,space):
    cpulist = []
    clist = arg.split(',')
    try:
        for item in clist:
            unit = item.split('-')
            clen = len(unit)
            if clen == 1:
                beg = end = int(unit[0])
            elif clen == 2:
                beg = int(unit[0])
                end = int(unit[1])
                if beg < end:
                    step = 1
                else:
                    step = -1
            else:
                raise Exception

            if beg >= space or end >= space:
                raise Exception
            if beg == end:
                cpulist.append(beg)
            else:
                cpulist.extend(range(beg,(end+step),step))
    except Exception:
        mpd_print(1, 'MPD: incorrect I_MPI_PIN_PROCESSOR_LIST setting: %s' % (item))
#        print 'MPD: incorrect I_MPI_PIN_PROCESSOR_LIST setting: %s' % (item)
        cpulist = []

    return cpulist
# pin_DigitList
#################################

#################################
# Check processor topology
#
def pin_Cpuinfo_status(info):
    if info['cores'] != info['packs']*(info['cores']/info['cache2'])*(info['cache2']/info['cache3'])*(info['cache3']/info['packs']):
#        mpd_print(1, 'MPD: incorrect processor topology ratio')
        status = 'ratio'
    elif info['packs']>info['cache3'] or info['cache3']>info['cache2'] or info['cache2']>info['cache1'] or info['cache1']>info['cores'] or info['cores']>info['lcpu']:
#        mpd_print(1, 'MPD: incorrect processor topology order')
        status = 'order'
    else:
        status = 'ok'

    return status
# pin_Cpuinfo_status
#################################

#################################
# Execute shell command
#
def pin_Exec(cmd):
    child = os.popen(cmd)
    reps=0
    while reps < 3:
        try:
            data = child.read()
        except Exception:
            reps += 1
            continue
        else:
            break
    else:
    #    print 'MPD:Unable to execute cmd: %s ' % cmd

        data=''

    return data
# pin_Exec
#################################

#################################
# Arch determination
#
def pin_Arch():
    return pin_Exec('uname -m | tr -d "\n"')
# pin_Arch
#################################

#################################
# Flat socket topology
#
def pin_Sock_topology(ncpu):
    cpu = str(ncpu)
    # number of logical processors
    data = 'CPU#:' + cpu + '\n'
    # number of physical packages
    data += 'P#:' + cpu + '\n'
    # number of cores
    data += 'C#:' + cpu + '\n'
    # number of threads
    data += 'T#:' + cpu + '\n'

    # thread identification
    data += 'TID:' + ' 0'*ncpu + '\n'
    # core identification
    data += 'CID:' + ' 0'*ncpu + '\n'
    # package identification
    data += 'PID:'
    for i in xrange(ncpu):
        data += ' ' + str(i)
    data += '\n'

    return data
# pin_Sock_topology
#################################

#################################
# SGI Topology
#
def pin_SGI_topology(case):
    # Altix specific for IA32 and IPF
    if case == 'sgi3':
        cpuset = pin_Exec('/usr/bin/cpuset -C 2> /dev/null')
        if cpuset:
            cpuset = cpuset[cpuset.find('[')+1:cpuset.find(']')]
            cmd = "/usr/bin/cpuset -q " + cpuset + " -Q | grep ' CPU\[' | wc -l"
            cpu = pin_Exec(cmd)
        else:
            cpu = ''
    else: # case == 'sgi4'
        cpu = pin_Exec('/usr/bin/cpuset -z `cpuset -w 0`')

    # number of logical cpus
    if not cpu:
#        mpd_print(1,'MPD warning. CPUs were not detected')
        cpu = '0'

    ncpu = int(cpu)
    if ncpu < 1: ncpu = 1

    return pin_Sock_topology(ncpu)
# pin_SGI_topology
#################################

#################################
# /proc/cpuinfo topology
#
def pin_Proc_topology():
    # scan /proc/cpuinfo
    cpu = pin_Exec('grep processor /proc/cpuinfo | wc -l')
    if not cpu:
#        mpd_print(1,'MPD warning. CPUs were not detected')
        cpu = '0'
    space = int(cpu)
    if not space:
        return pin_Sock_topology(1)

    s_list = pin_Exec('grep -e "physical id" /proc/cpuinfo | tr -cd " "0-9')
    c_list = pin_Exec('grep -e "core id" /proc/cpuinfo | tr -cd " "0-9')
    t_list = pin_Exec('grep -e "thread id" /proc/cpuinfo | tr -cd " "0-9')

    if (s_list and len(s_list.split()) != space) or (c_list and len(c_list.split()) != space) or (t_list and len(t_list.split()) != space):
#        mpd_print(1,'MPD warning. /proc/cpuinfo file is corrupted')
        return pin_Sock_topology(space)

    # number of logical cpu per socket
    sib = pin_Exec('grep -e "siblings" /proc/cpuinfo | tr -cd "\n"0-9')
    if sib: nsib = int(sib.split('\n')[0])
    else:   nsib = 0

    # number of cores per socket
    cor = pin_Exec('grep -e "cpu cores" /proc/cpuinfo | tr -cd "\n"0-9')
    if cor: ncore = int(cor.split('\n')[0])
    else :  ncore = 0

    # number of logical processors
    data = 'CPU#:' + cpu + '\n'
    # number of threads
    data += 'T#:' + cpu + '\n'

    #1. socks by list, cores, thread by siblings
    if s_list and not c_list and not t_list:
        nsock = pin_Uni_num(s_list.split(),space)
        if not ncore and not nsib:
            nsib = space / nsock
            ncore = nsib
            nt = 1
        elif not ncore and nsib:
            ncore = 1
            nt = nsib
        elif ncore and not nsib:
            nsib = ncore
            nt = 1
        else: # ncore and nsib
            nt = nsib / ncore

        if not nt: nt = 1
        if not ncore: ncore = 1

        # number of physical packages
        data += 'P#:' + str(nsock) + '\n'
        # number of cores
        data += 'C#:' + str(ncore*nsock) + '\n'

        # thread identification
        data += 'TID:'
        for i in xrange(space):
            data += ' ' + str(i % nt)
        data += '\n'
        # core identification
        data += 'CID:'
        for i in xrange(space):
            data += ' ' + str(i % ncore)
        data += '\n'
        # package identification
        data += 'PID:' + s_list + '\n'

    #2. socks by list, 1 core per sock, thread by list 
    elif s_list and not c_list and t_list:
        nsock = pin_Uni_num(s_list.split(),space)
        # number of physical packages
        data += 'P#:' + str(nsock) + '\n'
        # number of cores
        data += 'C#:' + str(nsock) + '\n'

        # thread identification
        data += 'TID:' + t_list + '\n'
        # core identification
        data += 'CID:' + ' 0'*space + '\n'
        # package identification
        data += 'PID:' + s_list + '\n'

    #3. socks, cores by list, nsock/ncore thread per core 
    elif s_list and c_list and not t_list:
        nsock = pin_Uni_num(s_list.split(),space)
        ncore = pin_Uni_num2(s_list.split(),c_list.split(),space)
        nt = space / ncore
        if not nt: nt = 1
        # number of physical packages
        data += 'P#:' + str(nsock) + '\n'
        # number of cores
        data += 'C#:' + str(ncore) + '\n'

        # thread identification
        data += 'TID:'
        for i in xrange(space):
            data += ' ' + str(i % nt)
        data += '\n'
        # core identification
        data += 'CID:' + c_list + '\n'
        # package identification
        data += 'PID:' + s_list + '\n'

    #4. socks, cores, threads by list 
    elif s_list and c_list and t_list:
        nsock = pin_Uni_num(s_list.split(),space)
        ncore = pin_Uni_num2(s_list.split(),c_list.split(),space)
        # number of physical packages
        data += 'P#:' + str(nsock) + '\n'
        # number of cores
        data += 'C#:' + str(ncore) + '\n'

        # thread identification
        data += 'TID:' + t_list + '\n'
        # core identification
        data += 'CID:' + c_list + '\n'
        # package identification
        data += 'PID:' + s_list + '\n'

    #5. 1 sock, 1 core per sock, N thread per core 
    elif not s_list and not c_list and t_list:
        # number of physical packages
        data += 'P#:1\n'
        # number of cores
        data += 'C#:1\n'

        # thread identification
        data += 'TID:' + t_list + '\n'
        # core identification
        data += 'CID:' + ' 0'*space + '\n'
        # package identification
        data += 'PID:' + ' 0'*space + '\n'

    #6. 1 sock, cores by list, 1 thread per core 
    elif not s_list and c_list and not t_list:
        ncore = pin_Uni_num(c_list.split(),space)
        # number of physical packages
        data += 'P#:1\n'
        # number of cores
        data += 'C#:' + str(ncore) + '\n'

        # thread identification
        data += 'TID:' + ' 0'*space + '\n'
        # core identification
        data += 'CID:' + c_list + '\n'
        # package identification
        data += 'PID:' + ' 0'*space + '\n'

    #7. 1 sock, cores, threads by list 
    elif not s_list and c_list and t_list:
        ncore = pin_Uni_num(c_list.split(),space)       
        # number of physical packages
        data += 'P#:1\n'
        # number of cores
        data += 'C#:' + str(ncore) + '\n'

        # thread identification
        data += 'TID:' + t_list + '\n'
        # core identification
        data += 'CID:' + c_list + '\n'
        # package identification
        data += 'PID:' + ' 0'*space + '\n'

    #8. N socks, 1 core per sock, 1 thread per core 
    else:
        data = pin_Sock_topology(space)

    return data
# pin_Proc_topology
#################################

#################################
# Topology gathering
#
def pin_Topology(case,arch):
    if os.environ.has_key('I_MPI_CPUINFO'):
        src = os.environ['I_MPI_CPUINFO']
#        print('os src= '+src)
        if src != 'cpuid' and src != 'proc': src = 'auto'
    else:
        src = 'auto'

    if src == 'auto':
        if (arch != 'x86_64' and (case == 'sgi3' or case == 'sgi4')):
            # SGI cpuset source
            src = 'sgi'
        elif arch == 'ia64':
            # /proc file system source
            src = 'proc'
        else:
            # cpuinfo source (cpuid instruction)
            src = 'cpuid'
        
    if src == 'cpuid':
        if mpd_which('cpuinfo'):
            cpuinfo_cmd = 'cpuinfo'
        else:
            mpibindir = os.path.abspath(os.path.split(sys.argv[0])[0])
            cpuinfo_cmd = os.path.join(mpibindir, 'cpuinfo')


        data = pin_Exec('"%s" p' % (cpuinfo_cmd))

        if data:
#            mpd_print(1,'MPD warning. Cpuinfo utility on place')
            idx = data.find('T#:')
            if idx != -1:
                if int(data[idx+3:data.find('\n',idx)]) > 0: return data
            src = 'proc'
        else:
            src = 'proc'
#            mpd_print(1,'MPD warning. Cpuinfo utility was not found')

    if src == 'sgi':
        return pin_SGI_topology(case)
    if src == 'proc':
        return pin_Proc_topology()
    else:
#        mpd_print(1,'MPD warning. Singular topology is assumed')
        return pin_Sock_topology(1)
# pin_Topology
#################################

#################################
# Cpuinfo obtainment
#
def pin_Cpuinfo(case,arch):
    info = {
        'stat'       : '',
        'arch'       : '',
        'sign'       : '',
        'mode'       : '0',
        'vend'       : '0',
        'ff_b'       : '0',
        'ff_c'       : '0',
        'ff_d'       : '0',
        'desc'       : '0',
        'brnd'       : '',
        'snum'       : '0',
        'cnam'       : '',
        'packs'      : 0,
        'cache3'     : 0,
        'cache2'     : 0,
        'cache1'     : 0,
        'cores'      : 0,
        'lcpu'       : 0,
        'pack_id'    : [],
        'core_id'    : [],
        'thread_id'  : [],
        'caches'     : '',
        'share'      : [],
        'size'       : [],
        'cache1_id'  : [],
        'cache2_id'  : [],
        'cache3_id'  : [],
        }

    data = pin_Topology(case,arch)

### required fields
    # arch token
    info['arch']  = arch
    # number of logical processors
    idx = data.find('CPU#:')
    info['lcpu']  = int(data[idx+5:data.find('\n',idx)])
    # number of physical packages
    idx = data.find('P#:')
    info['packs'] = int(data[idx+3:data.find('\n',idx)])
    # number of cores
    idx = data.find('C#:')
    info['cores'] = int(data[idx+3:data.find('\n',idx)])
    # thread ids
    idx = data.find('TID:')
    info['thread_id'] = data[idx+4:data.find('\n',idx)].split()
    # core ids
    idx = data.find('CID:')
    info['core_id']   = data[idx+4:data.find('\n',idx)].split()
    # package ids
    idx = data.find('PID:')
    info['pack_id']   = data[idx+4:data.find('\n',idx)].split()

### optional fields
    #   signature
    idx = data.find('SIGN:')
    if idx != -1:
        info['sign'] = data[idx+5:data.find('\n',idx)]
    else:
        info['sign'] = '0'
    #   mode
    idx = data.find('MODE:')
    if idx != -1:
        info['mode'] = data[idx+5:data.find('\n',idx)]
    else:
        info['mode'] = '0'
    #   vendor
    idx = data.find('VEND:')
    if idx != -1:
        info['vend'] = data[idx+5:data.find('\n',idx)]
    else:
        info['vend'] = '0'
    #   B feature flags
    idx = data.find('FLGB:')
    if idx != -1:
        info['ff_b'] = data[idx+5:data.find('\n',idx)]
    else:
        info['ff_b'] = '0'
    #   C feature flags
    idx = data.find('FLGC:')
    if idx != -1:
        info['ff_c'] = data[idx+5:data.find('\n',idx)]
    else:
        info['ff_c'] = '0'
    #   D feature flags
    idx = data.find('FLGD:')
    if idx != -1:
        info['ff_d'] = data[idx+5:data.find('\n',idx)]
    else:
        info['ff_d'] = '0'
    #   descriptor
    idx = data.find('DESC:')
    if idx != -1:
        info['desc'] = data[idx+5:data.find('\n',idx)]
    else:
        info['desc'] = '0'
    #   brand name
    idx = data.find('BRND:')
    if idx != -1:
        info['brnd'] = data[idx+5:data.find('\n',idx)]
    else:
        info['brnd'] = 'unk'
    #   model number
    idx = data.find('SNUM:')
    if idx != -1:
        info['snum'] = data[idx+5:data.find('\n',idx)]
    else:
        info['snum'] = '0'
    #   code name
    idx = data.find('CNAM:')
    if idx != -1:
        info['cnam'] = data[idx+5:data.find('\n',idx)]
    else:
        info['cnam'] = 'unk'
    #   number of caches
    idx = data.find('LMAX:')
    if idx != -1:
        info['caches'] = data[idx+5:data.find('\n',idx)]
    else:
        info['caches'] = '3'
    #   cache width
    idx = data.find('SHR:')
    if idx != -1:
        ent = data[idx+4:data.find('\n',idx)]
    else:
        ent = '1 1 1'
    info['share'] = ent.split()
    #   cache size
    idx = data.find('SIZ:')
    if idx != -1:
        ent = data[idx+4:data.find('\n',idx)]
    else:
        ent = '1 1 1'
    info['size'] = ent.split()

    #   cache level 1
    idx = data.find('L1:')
    if idx != -1:
        ent = data[idx+3:data.find('\n',idx)]
        info['cache1_id'] = ent.split()
    else:
        for i in xrange(info['lcpu']):
            info['cache1_id'].append(info['pack_id'][i] + info['core_id'][i])
    idx = data.find('L1#:')
    if idx != -1:
        info['cache1'] = int(data[idx+4:data.find('\n',idx)])
    else:
        info['cache1'] = pin_Uni_num(info['cache1_id'], info['lcpu'])

    #   cache level 2
    idx = data.find('L2:')
    if idx != -1:
        ent = data[idx+3:data.find('\n',idx)]
        info['cache2_id'] = ent.split()
    else:
        for i in xrange(len(info['cache1_id'])):
            info['cache2_id'].append(info['cache1_id'][i])
    idx = data.find('L2#:')
    if idx != -1:
        info['cache2'] = int(data[idx+4:data.find('\n',idx)])
    else:
        info['cache2'] = pin_Uni_num(info['cache2_id'], info['lcpu'])

    #   cache level 3
    idx = data.find('L3:')
    if idx != -1:
        ent = data[idx+3:data.find('\n',idx)]
        info['cache3_id'] = ent.split()
    else:
        for i in xrange(len(info['cache2_id'])):
            info['cache3_id'].append(info['cache2_id'][i])
    idx = data.find('L3#:')
    if idx != -1:
        info['cache3'] = int(data[idx+4:data.find('\n',idx)])
    else:
        info['cache3'] = pin_Uni_num(info['cache3_id'], info['lcpu'])

    # check topology
    info['stat'] = pin_Cpuinfo_status(info)

    return info
# pin_Cpuinfo
#################################

#################################
# Determine environment case
#
def pin_Case(arch):
    if glob('/etc/sgi-release') and arch != 'x86_64':
    # Altix and ia64 or i686 arch
        sysstr = pin_Exec('cat /etc/sgi-release')
        where = sysstr.find('ProPack ')
        vers = int(sysstr[where+8:where+9])
        if vers >= 4: # ProPack 4 or higher
            case = 'sgi4'
        elif vers == 3: # ProPack 3
            case = 'sgi3'
        else:
            case = 'na'
    else:
    # Use taskset facility for x86_64 arch or for any non Altix
        if glob('/usr/bin/taskset'):
            cmd = '/usr/bin/taskset'
        elif glob('/bin/taskset'):
            cmd = '/bin/taskset'
        else:
            return 'na'

        m = pin_Exec('%s -c 0 echo "MPI" 2> /dev/null' % cmd)
        if m[0:3] == 'MPI': case = 'std'
        else:               case = 'na'

    return case
# pin_Case
#################################

# MPD pinning support functions


def sigchld_handler(signum,frame):
    done = 0
    while not done:
        try:
            (pid,status) = os.waitpid(-1,os.WNOHANG)
            if pid == 0:    # no existing child process is finished
                done = 1
        except:    # no more child processes to be waited for
            done = 1
            
class MPD(object):
    def __init__(self):
        self.myHost = socket.gethostname()
        try:
            hostinfo = socket.gethostbyname_ex(self.myHost)
            self.myIfhn = hostinfo[2][0]    # chgd below when I get the real value
        
        # Needed to avoid bad system configuration
        # hostname localhost 127.0.0.1
            self.myIP = hostinfo[2][0]    # chgd below when I get the real value
            if self.myIfhn.startswith('127'):
                self.myIfhn = self.myHost
        

        except Exception, errmsg:
            #print 'mpd failed: gethostbyname_ex failed for %s because of %s. Probably your DHCP/DNS servers misconfigured.' % (self.myHost, errmsg)
            self.myIfhn = self.myHost

            #sys.exit(-1)
    def run(self):
        if syslog_module_available:
            syslog.openlog("mpd",0,syslog.LOG_DAEMON)
            syslog.syslog(syslog.LOG_INFO,"mpd starting; no mpdid yet")
        sys.excepthook = mpd_uncaught_except_tb
        self.spawnQ = []
        self.spawnInProgress = 0
        self.parmdb = MPDParmDB(orderedSources=['cmdline','xml','env','rcfile','thispgm'])
        self.parmsToOverride = {
                                 'MPD_SECRETWORD'       :  '',

                                 'MPD_MY_HOST'          :  self.myIfhn,
                                 'MPD_MY_IFHN'          :  '',
                                 'MPD_MY_IP'            :  '',


                                 'MPD_ENTRY_IFHN'       :  '',
                                 'MPD_ENTRY_PORT'       :  0,
                                 'MPD_NCPUS'            :  1,
                                 'MPD_LISTEN_PORT'      :  0,
                                 'MPD_TRACE_FLAG'       :  0,
                                 'MPD_CONSOLE_FLAG'     :  1,
                                 'MPD_ECHO_PORT_FLAG'   :  0,
                                 'MPD_DAEMON_FLAG'      :  0,
                                 'MPD_BULLETPROOF_FLAG' :  0,
                                 'MPD_PID_FILENAME'     :  '',
                                 'MPD_ZC'               :  0,
                                 'MPD_LOGFILE_TRUNC_SZ' :  4000000,  # -1 -> don't trunc

                                 'MPD_MAX_RING_SIZE'    : -1, # -1 means unknown

                                 'MPD_PORT_RANGE'       :  0,

                                 'TMPDIR'               :  '',
                                 'MPD_TMPDIR'           :  '/tmp',
                                 'I_MPI_MPD_TMPDIR'     :  '',


                                 'I_MPI_MPD_CLEAN_LOG'  :  '0',

                               }
        for (k,v) in self.parmsToOverride.items():
            self.parmdb[('thispgm',k)] = v
        if os.environ.has_key('MPD_CON_EXT'):
            self.conExt = '_'  + os.environ['MPD_CON_EXT']
        else:
            self.conExt = ''
        if os.environ.has_key('I_MPI_JOB_CONTEXT'):
            self.conExt = '_'  + os.environ['I_MPI_JOB_CONTEXT']
        self.logFilename = '/tmp/mpd2.logfile_' + mpd_get_my_username() + self.conExt
        self.tmpdir_error_message = ''
        self.right_tmpdir = 0

        self.tmpdir=self.parmdb['MPD_TMPDIR']
        if os.environ.has_key('TMPDIR'):
            if os.path.exists(os.environ['TMPDIR']):
                self.logFilename = '%s/mpd2.logfile_' % (os.environ['TMPDIR']) + self.myHost + '_' + mpd_get_my_username() + self.conExt
                self.right_tmpdir = 1
                self.parmdb[('env','MPD_TMPDIR')] = os.environ['TMPDIR']
                self.tmpdir = os.environ['TMPDIR']
            else:
                if not os.environ.has_key('MPD_TMPDIR') and not os.environ.has_key('I_MPI_MPD_TMPDIR'):
                    self.tmpdir_error_message = 'Warning: the directory pointed by TMPDIR (%s) does not exist! /tmp will be used.' % (os.environ['TMPDIR'])
        if os.environ.has_key('MPD_TMPDIR'):
            if os.path.exists(os.environ['MPD_TMPDIR']):
                self.logFilename = '%s/mpd2.logfile_' % (os.environ['MPD_TMPDIR']) + self.myHost + '_' + mpd_get_my_username() + self.conExt
                self.right_tmpdir = 2
                self.parmdb[('env','MPD_TMPDIR')] = os.environ['MPD_TMPDIR']
                self.tmpdir = os.environ['MPD_TMPDIR']
            else:
                if not os.environ.has_key('I_MPI_MPD_TMPDIR'):
                    if self.right_tmpdir:
                        self.tmpdir_error_message = 'Warning: the directory pointed by MPD_TMPDIR (%s) does not exist! %s will be used.' % (os.environ['MPD_TMPDIR'], os.environ['TMPDIR'])
                    else:
                        self.tmpdir_error_message = 'Warning: the directory pointed by MPD_TMPDIR (%s) does not exist! /tmp will be used.' % (os.environ['MPD_TMPDIR'])
        if os.environ.has_key('I_MPI_MPD_TMPDIR'):
            if os.path.exists(os.environ['I_MPI_MPD_TMPDIR']):
                self.logFilename = '%s/mpd2.logfile_' % (os.environ['I_MPI_MPD_TMPDIR']) + self.myHost + '_' + mpd_get_my_username() + self.conExt            
                self.parmdb[('env','MPD_TMPDIR')] = os.environ['I_MPI_MPD_TMPDIR']
                self.tmpdir = os.environ['I_MPI_MPD_TMPDIR']
            else:
                if self.right_tmpdir == 2:
                    self.tmpdir_error_message = 'Warning: the directory pointed by I_MPI_MPD_TMPDIR (%s) does not exist! %s will be used.' % (os.environ['I_MPI_MPD_TMPDIR'], os.environ['MPD_TMPDIR'])
                elif self.right_tmpdir == 1:
                    self.tmpdir_error_message = 'Warning: the directory pointed by I_MPI_MPD_TMPDIR (%s) does not exist! %s will be used.' % (os.environ['I_MPI_MPD_TMPDIR'], os.environ['TMPDIR'])
                else:
                    self.tmpdir_error_message = 'Warning: the directory pointed by I_MPI_MPD_TMPDIR (%s) does not exist! /tmp will be used.' % (os.environ['I_MPI_MPD_TMPDIR'])

        self.get_parms_from_cmdline()

        self.parmdb.get_parms_from_rcfile(self.parmsToOverride,errIfMissingFile=0)

        self.parmdb.get_parms_from_env(self.parmsToOverride)

        self.myIfhn = self.parmdb['MPD_MY_HOST']    # variable for convenience
        if self.parmdb['MPD_MY_IFHN'] :
            self.myIfhn = self.parmdb['MPD_MY_IFHN']    # variable for convenience
        if self.parmdb['MPD_MY_IP'] :
           self.myIP = self.parmdb['MPD_MY_IP']    # variable for convenience


        self.ncpusTable = {}
        self.ncpusEquality = 0

#
        self.Arch = pin_Arch()
        self.PinRank = 0
        self.PinCase = pin_Case(self.Arch)
        self.CpuInfo = pin_Cpuinfo(self.PinCase,self.Arch)
        self.PinSpace = self.CpuInfo['lcpu']
        self.PinCores = self.CpuInfo['cores']
#
        self.myPid = os.getpid()
        if self.parmdb['MPD_PORT_RANGE']:
            os.environ['MPICH_PORT_RANGE'] = self.parmdb['MPD_PORT_RANGE']
        mpd_set_tmpdir(self.tmpdir)
        self.listenSock = MPDListenSock(name='ring_listen_sock',
                                        port=self.parmdb['MPD_LISTEN_PORT'])
        self.parmdb[('thispgm','MPD_LISTEN_PORT')] = self.listenSock.sock.getsockname()[1]
        self.myId = '%s_%d' % (self.myHost,self.parmdb['MPD_LISTEN_PORT'])
        mpd_set_my_id(myid=self.myId)
        self.streamHandler = MPDStreamHandler()

        self.ring = MPDRing(streamHandler=self.streamHandler,
                            secretword=self.parmdb['MPD_SECRETWORD'],
                            listenSock=self.listenSock,
                            myIfhn=self.myIfhn,
                            myIP=self.myIP,
                            entryIfhn=self.parmdb['MPD_ENTRY_IFHN'],

                            entryPort=self.parmdb['MPD_ENTRY_PORT'],
                            zcMyLevel=self.parmdb['MPD_ZC'])
        # setup tracing if requested via args
        if self.parmdb['MPD_TRACE_FLAG']:
            proceduresToTrace = []
            import inspect
            symbolsAndTypes = globals().items() + \
                              inspect.getmembers(self) + \
                              inspect.getmembers(self.ring) + \
                              inspect.getmembers(self.streamHandler)
            for (symbol,symtype) in symbolsAndTypes:
                if symbol == '__init__':  # a problem to trace
                    continue
                if inspect.isfunction(symtype)  or  inspect.ismethod(symtype):
                    # print symbol
                    proceduresToTrace.append(symbol)
            mpd_set_procedures_to_trace(proceduresToTrace)
            sys.settrace(mpd_trace_calls)
        if syslog_module_available:
            syslog.syslog(syslog.LOG_INFO,"mpd has mpdid=%s (port=%d)" % \
                          (self.myId,self.parmdb['MPD_LISTEN_PORT']) )
        vinfo = mpd_check_python_version()
        if vinfo:
            print "mpd: your python version must be >= 2.2 ; current version is:", vinfo
            sys.exit(-1)

        # need to close both object and underlying fd (ticket #963)
        sys.stdin.close()
        os.close(0)

        self.fileUnlinkError = ""
        file_count = 1
        logFilename_ori = self.logFilename
        file_found = 0
        while file_count <= 10:
            unlink_error = 0
            try:
                os.unlink(self.logFilename)
                file_found = 1
                break
            except Exception, errmsg:
                if errmsg[0] != ENOENT:
                    unlink_error = 1
                    if self.fileUnlinkError:
                        self.fileUnlinkError += '\nUnlink error: %s' % (errmsg)
                    else:
                        self.fileUnlinkError = 'Unlink error: %s' % (errmsg)
                else:
                    file_found = 1
                    break
            if unlink_error:
                self.logFilename = logFilename_ori + '_%d' % (file_count)    
                file_count += 1
                continue
        if not file_found:
            print 'Error creating a logfile:\n%s' % (self.fileUnlinkError)
            sys.exit(-1)

        if self.parmdb['MPD_ECHO_PORT_FLAG']:    # do this before becoming a daemon

            print self.parmdb['MPD_LISTEN_PORT'] # backward compatibility

            if os.environ.has_key('I_MPI_JOB_TAGGED_PORT_OUTPUT') and os.environ['I_MPI_JOB_TAGGED_PORT_OUTPUT'] in ['1', 'on', 'yes', 'enable']:


                print '<I_MPI_MPD_PORT>%d</I_MPI_MPD_PORT>' % (self.parmdb['MPD_LISTEN_PORT'])


            sys.stdout.flush()
            ##### NEXT 2 for debugging
            ## print >>sys.stderr, self.parmdb['MPD_LISTEN_PORT']
            ## sys.stderr.flush()
        self.myRealUsername = mpd_get_my_username()
        self.currRingSize = 1    # default
        self.currRingNCPUs = 1   # default

        self.maxRingSize = self.parmdb['MPD_MAX_RING_SIZE']


#         if os.environ.has_key('MPD_CON_EXT'):
#             self.conExt = '_'  + os.environ['MPD_CON_EXT']
#         else:
#             self.conExt = ''
#         if os.environ.has_key('I_MPI_JOB_CONTEXT'):
#             self.conExt = '_'  + os.environ['I_MPI_JOB_CONTEXT']
#         self.logFilename = '/tmp/mpd2.logfile_' + mpd_get_my_username() + self.conExt

#         self.tmpdir_error_message = ''
#         self.right_tmpdir = 0
#         if os.environ.has_key('TMPDIR'):
#             if os.path.exists(os.environ['TMPDIR']):
#                 self.logFilename = '%s/mpd2.logfile_' % (os.environ['TMPDIR']) + self.myHost + '_' + mpd_get_my_username() + self.conExt
#                 self.right_tmpdir = 1
#             else:
#                 if not os.environ.has_key('I_MPI_MPD_TMPDIR'):
#                     self.tmpdir_error_message = 'Warning: the directory pointed by TMPDIR (%s) does not exist! /tmp will be used.' % (os.environ['TMPDIR'])
#         if os.environ.has_key('I_MPI_MPD_TMPDIR'):
#             if os.path.exists(os.environ['I_MPI_MPD_TMPDIR']):
#                 self.logFilename = '%s/mpd2.logfile_' % (os.environ['I_MPI_MPD_TMPDIR']) + self.myHost + '_' + mpd_get_my_username() + self.conExt
#             else:
#                 if self.right_tmpdir:
#                     self.tmpdir_error_message = 'Warning: the directory pointed by I_MPI_MPD_TMPDIR (%s) does not exist! %s will be used.' % (os.environ['I_MPI_MPD_TMPDIR'], os.environ['TMPDIR'])
#                 else:
#                     self.tmpdir_error_message = 'Warning: the directory pointed by I_MPI_MPD_TMPDIR (%s) does not exist! /tmp will be used.' % (os.environ['I_MPI_MPD_TMPDIR'])


        if self.parmdb['MPD_PID_FILENAME']:  # may overwrite it below
            pidFile = open(self.parmdb['MPD_PID_FILENAME'],'w')
            print >>pidFile, "%d" % (os.getpid())
            pidFile.close()

        self.conListenSock = 0    # don't want one when I do cleanup for forked daemon procs
        if self.parmdb['MPD_DAEMON_FLAG']:      # see if I should become a daemon with no controlling tty
            rc = os.fork()
            if rc != 0:   # parent exits; child in background
                sys.exit(0)
            os.setsid()  # become session leader; no controlling tty
            signal.signal(signal.SIGHUP,signal.SIG_IGN)  # make sure no sighup when leader ends
            ## leader exits; svr4: make sure do not get another controlling tty
            rc = os.fork()
            if rc != 0:
                sys.exit(0)
            if self.parmdb['MPD_PID_FILENAME']:  # overwrite one above before chg usmask
                pidFile = open(self.parmdb['MPD_PID_FILENAME'],'w')
                print >>pidFile, "%d" % (os.getpid())
                pidFile.close()
            os.chdir("/")  # free up filesys for umount
            
            if os.getuid() == 0:
                os.umask(0)
            
            try:    os.unlink(self.logFilename)
            except: pass
            logFileFD = os.open(self.logFilename,os.O_CREAT|os.O_WRONLY|os.O_EXCL,0600)
            self.logFile = os.fdopen(logFileFD,'w',0)
            sys.stdout = self.logFile
            sys.stderr = self.logFile

            if self.fileUnlinkError:
                print >> sys.stdout, 'Warning: the original logfile %s could not be created:\n%s' % (logFilename_ori,self.fileUnlinkError)

            print >>sys.stdout, 'logfile for mpd with pid %d' % os.getpid()
            sys.stdout.flush()
            os.dup2(self.logFile.fileno(),sys.__stdout__.fileno())
            os.dup2(self.logFile.fileno(),sys.__stderr__.fileno())

            if self.tmpdir_error_message:
                mpd_print(1, self.tmpdir_error_message)

        if self.parmdb['MPD_CONSOLE_FLAG']:
            self.conListenSock = MPDConListenSock(secretword=self.parmdb['MPD_SECRETWORD'])
            self.streamHandler.set_handler(self.conListenSock,
                                           self.handle_console_connection)
        register(self.cleanup)
        seed()
        self.nextJobInt    = 1
        self.activeJobs    = {}
        self.conSock       = 0
        self.allExiting    = 0    # for mpdallexit (for first loop for graceful exit)
        self.exiting       = 0    # for mpdexit or mpdallexit
        self.kvs_cntr      = 0    # for mpdman
        self.pulse_cntr    = 0
        rc = self.ring.enter_ring(lhsHandler=self.handle_lhs_input,
                                  rhsHandler=self.handle_rhs_input)
        if rc < 0:

            mpd_print(1,"the daemon failed to enter the mpd ring")

            sys.exit(-1)
        self.pmi_published_names = {}
        if hasattr(signal,'SIGCHLD'):
            signal.signal(signal.SIGCHLD,sigchld_handler)
        if not self.parmdb['MPD_BULLETPROOF_FLAG']:
            #    import profile ; profile.run('self.runmainloop()')
            self.runmainloop()
        else:
            try:
                from threading import Thread
            except:

                print 'mpd terminated due to'
                print 'bulletproof option must be able to import Thread function from the threading python module; check python installation'

                sys.exit(-1)
            # may use SIG_IGN on all but SIGCHLD and SIGHUP (handled above)
            while 1:
                mpdtid = Thread(target=self.runmainloop)
                mpdtid.start()
                # signals must be handled in main thread; thus we permit timeout of join
                while mpdtid.isAlive():
                    mpdtid.join(2)   # come out sometimes and handle signals
                if self.exiting:
                    break
                if self.conSock:
                    msgToSend = { 'cmd' : 'restarting_mpd' }

#                    self.conSock,msgToSend.send_dict_msg(msgToSend)
                    self.conSock.send_dict_msg(msgToSend)

                    self.streamHandler.del_handler(self.conSock)
                    self.conSock.close()
                    self.conSock = 0


        # remove log file
        if self.parmdb['I_MPI_MPD_CLEAN_LOG'].lower() in ["1", "on", "yes", "enable"]:
            try:
                os.unlink(self.logFilename)
            except Exception, errmsg:
                print 'Error unlink a logfile:\n%s' % (errmsg)
                sys.exit(-1)

    def runmainloop(self):
        # Main Loop
        while 1:
            if self.spawnQ  and  not self.spawnInProgress:
                self.ring.rhsSock.send_dict_msg(self.spawnQ[0])
                self.spawnQ = self.spawnQ[1:]
                self.spawnInProgress = 1
                continue
            rv = self.streamHandler.handle_active_streams(timeout=8.0)
            if rv[0] < 0:
                if type(rv[1]) == ClassType  and  rv[1] == KeyboardInterrupt: # ^C
                    sys.exit(-1)
            if self.exiting:
                break
            if rv[0] == 0:
                if self.pulse_cntr == 0  and  self.ring.rhsSock:
                    self.ring.rhsSock.send_dict_msg({'cmd':'pulse'})
                self.pulse_cntr += 1
            if self.pulse_cntr >= 3:
                if self.ring.rhsSock:  # rhs must have disappeared
                    self.streamHandler.del_handler(self.ring.rhsSock)
                    self.ring.rhsSock.close()
                    self.ring.rhsSock = 0
                if self.ring.lhsSock:
                    self.streamHandler.del_handler(self.ring.lhsSock)
                    self.ring.lhsSock.close()
                    self.ring.lhsSock = 0
                mpd_print(1,'no pulse_ack from rhs; re-entering ring')
                rc = self.ring.reenter_ring(lhsHandler=self.handle_lhs_input,
                                            rhsHandler=self.handle_rhs_input,
                                            ntries=16)
                if rc == 0:
                    mpd_print(1,'back in ring')
                else:
                    mpd_print(1,'failed to reenter ring')
                    sys.exit(-1)
                self.pulse_cntr = 0
        mpd_close_zc()  # only does something if we have zc
    def usage(self):
        print __doc__
        #print "This version of mpd is", mpd_version()
        sys.exit(-1)
    def cleanup(self):
        try:
            mpd_print(0, "CLEANING UP" )
            if syslog_module_available:
                syslog.syslog(syslog.LOG_INFO,"mpd ending mpdid=%s (inside cleanup)" % \
                              (self.myId) )
                syslog.closelog()
            if self.conListenSock:    # only del if I created
                os.unlink(self.conListenSock.conFilename)
        except:
            pass
    def get_parms_from_cmdline(self):
        global mpd_dbg_level
        argidx = 1
        while argidx < len(sys.argv):
            if sys.argv[argidx] == '--help':
                self.usage()
                argidx += 1
            elif sys.argv[argidx] == '-h':
                if len(sys.argv) < 3:
                    self.usage()
                self.parmdb[('cmdline','MPD_ENTRY_IFHN')] = sys.argv[argidx+1]
                argidx += 2
            elif sys.argv[argidx].startswith('--host'):
                try:
                    entryHost = sys.argv[argidx].split('=',1)[1]
                except:
                    print 'failed to parse --host option'
                    self.usage()
                self.parmdb[('cmdline','MPD_ENTRY_IFHN')] = entryHost
                argidx += 1
            elif sys.argv[argidx] == '-p':
                if argidx >= (len(sys.argv)-1):

                    print 'missing arg for -p option'

                    sys.exit(-1)
                if not sys.argv[argidx+1].isdigit():
                    print 'invalid port %s ; must be numeric' % (sys.argv[argidx+1])
                    sys.exit(-1)
                self.parmdb[('cmdline','MPD_ENTRY_PORT')] = int(sys.argv[argidx+1])
                argidx += 2
            elif sys.argv[argidx].startswith('--port'):
                try:
                    entryPort = sys.argv[argidx].split('=',1)[1]
                except:
                    print 'failed to parse --port option'
                    self.usage()
                if not entryPort.isdigit():
                    print 'invalid port %s ; must be numeric' % (entryPort)
                    sys.exit(-1)
                self.parmdb[('cmdline','MPD_ENTRY_PORT')] = int(entryPort)
                argidx += 1
            elif sys.argv[argidx].startswith('--ncpus'):
                try:
                    NCPUs = sys.argv[argidx].split('=',1)[1]
                except:
                    print 'failed to parse --ncpus option'
                    self.usage()
                if not NCPUs.isdigit():
                    print 'invalid ncpus %s ; must be numeric' % (NCPUs)
                    sys.exit(-1)
                self.parmdb[('cmdline','MPD_NCPUS')] = int(NCPUs)
                argidx += 1
            elif sys.argv[argidx].startswith('--pid'):
                try:
                    splitPid = sys.argv[argidx].split('=')
                except:
                    print 'failed to parse --pid option'
                    self.usage()
                if len(splitPid) == 1  or  not splitPid[1]:
                    pidFilename = '/var/run/mpd.pid'
                else:
                    pidFilename = splitPid[1]
                self.parmdb[('cmdline','MPD_PID_FILENAME')] = pidFilename
                argidx += 1
            elif sys.argv[argidx].startswith('--tmpdir'):
                try:
                    splitTmpdir = sys.argv[argidx].split('=')
                except:
                    print 'failed to parse --tmpdir option'
                    self.usage()
                if len(splitTmpdir) == 1  or  not splitTmpdir[1]:
                    tmpdirName = '/tmp'
                else:
                    tmpdirName = splitTmpdir[1]
                self.parmdb[('cmdline','MPD_TMPDIR')] = tmpdirName
                argidx += 1
            elif sys.argv[argidx].startswith('--ifhn'):
                try:
                    ifhn = sys.argv[argidx].split('=',1)[1]
                except:
                    print 'failed to parse --ifhn option'
                    self.usage()
                try:
                    hostinfo = socket.gethostbyname_ex(ifhn)
                    ifhn = hostinfo[2][0]
                except:
                    print 'mpd failed: gethostbyname_ex failed for %s' % (ifhn)
                    sys.exit(-1)
                self.parmdb[('cmdline','MPD_MY_IFHN')] = ifhn
                argidx += 1

            elif sys.argv[argidx].startswith('--myhost'):
                try:
                    self.myHost = sys.argv[argidx].split('=',1)[1]
                except:
                    print 'failed to parse --myhost option'
                    self.usage()
                try:
                    hostinfo = socket.gethostbyname_ex(self.myHost)
                    self.myIP = hostinfo[2][0]
                except:
                    print 'mpd failed: gethostbyname_ex failed for %s' % (self.myIP)
                    sys.exit(-1)
                if self.myIP.startswith('127'):
                   self.parmdb[('cmdline','MPD_MY_HOST')] = self.myHost
                else:
                   self.parmdb[('cmdline','MPD_MY_HOST')] = self.myIP
                argidx += 1
            elif sys.argv[argidx].startswith('--myip'):
                try:
                    ip = sys.argv[argidx].split('=',1)[1]
                except:
                    print 'failed to parse --myip option'
                    self.usage()
                self.parmdb[('cmdline','MPD_MY_IP')] = ip
                argidx += 1

            elif sys.argv[argidx] == '-l':
                if argidx >= (len(sys.argv)-1):

                    print 'missing arg for -l option'

                    sys.exit(-1)
                if not sys.argv[argidx+1].isdigit():
                    print 'invalid listenport %s ; must be numeric' % (sys.argv[argidx+1])
                    sys.exit(-1)
                self.parmdb[('cmdline','MPD_LISTEN_PORT')] = int(sys.argv[argidx+1])
                argidx += 2
            elif sys.argv[argidx].startswith('--listenport'):
                try:
                    myListenPort = sys.argv[argidx].split('=',1)[1]
                except:
                    print 'failed to parse --listenport option'
                    self.usage()
                if not myListenPort.isdigit():
                    print 'invalid listenport %s ; must be numeric' % (myListenPort)
                    sys.exit(-1)
                self.parmdb[('cmdline','MPD_LISTEN_PORT')] = int(myListenPort)
                argidx += 1
            elif sys.argv[argidx] == '-hp':
                if argidx >= (len(sys.argv)-1):

                    print 'missing arg for -hp option'

                    sys.exit(-1)
                try:
                    (entryIfhn,entryPort) = sys.argv[argidx+1].split('_')
                except:
                    print 'invalid entry host: %s' % (sys.argv[argidx+1])
                    sys.exit(-1)
                if not entryPort.isdigit():
                    print 'invalid port %s ; must be numeric' % (sys.argv[argidx+1])
                    sys.exit(-1)
                self.parmdb[('cmdline','MPD_ENTRY_IFHN')] = entryIfhn
                self.parmdb[('cmdline','MPD_ENTRY_PORT')] = int(entryPort)
                argidx += 2
            elif sys.argv[argidx] == '-t'  or  sys.argv[argidx] == '--trace':
                self.parmdb[('cmdline','MPD_TRACE_FLAG')] = 1
                argidx += 1
            elif sys.argv[argidx] == '--debug':
                mpd_set_dbg_level(1)
                argidx += 1
            elif sys.argv[argidx] == '-n'  or  sys.argv[argidx] == '--noconsole':
                self.parmdb[('cmdline','MPD_CONSOLE_FLAG')] = 0
                argidx += 1
            elif sys.argv[argidx] == '-e'  or  sys.argv[argidx] == '--echo':
                self.parmdb[('cmdline','MPD_ECHO_PORT_FLAG')] = 1 
                argidx += 1
            elif sys.argv[argidx] == '-d'  or  sys.argv[argidx] == '--daemon':
                self.parmdb[('cmdline','MPD_DAEMON_FLAG')] = 1 
                argidx += 1
            elif sys.argv[argidx] == '-b'  or  sys.argv[argidx] == '--bulletproof':
                self.parmdb[('cmdline','MPD_BULLETPROOF_FLAG')] = 1 
                argidx += 1

            elif sys.argv[argidx] == '-s':
                try:
                    self.parmdb[('cmdline', 'MPD_MAX_RING_SIZE')] = int(sys.argv[argidx + 1])
                except Exception, errmsg:
                    print 'Can\'t convert the parameter %s into integer: %s' % (sys.argv[argidx + 1], errmsg)
                argidx += 2


            elif sys.argv[argidx] == '-V' or sys.argv[argidx] == '--version':
                vers = 'Version 5.0 Update 1  Build 20140709'
                print 'Intel(R) MPI Library for Linux* OS, 64-bit applications,',vers
                print 'Copyright (C) 2003-2014 Intel Corporation.  All rights reserved.\n'
                if len(sys.argv) < 3:
                    sys.exit(0)

            elif sys.argv[argidx] == '-zc':
                if argidx >= (len(sys.argv)-1):
                    print 'missing arg for -zc'
                    sys.exit(-1)
                if not sys.argv[argidx+1].isdigit():
                    print 'invalid arg for -zc %s ; must be numeric' % (sys.argv[argidx+1])
                    sys.exit(-1)
                intarg = int(sys.argv[argidx+1])
                if intarg < 1:
                    print 'invalid arg for -zc %s ; must be >= 1' % (sys.argv[argidx+1])
                    sys.exit(-1)
                self.parmdb[('cmdline','MPD_ZC')] = intarg
                argidx += 2
            else:
                print 'unrecognized arg: %s' % (sys.argv[argidx])
                sys.exit(-1)
        if (self.parmdb['MPD_ENTRY_IFHN']  and  not self.parmdb['MPD_ENTRY_PORT']) \
        or (self.parmdb['MPD_ENTRY_PORT']  and  not self.parmdb['MPD_ENTRY_IFHN']):
            print 'host and port must be specified together'
            sys.exit(-1)
    def handle_console_connection(self,sock):
        if not self.conSock:
            (self.conSock,newConnAddr) = sock.accept()
            if hasattr(socket,'AF_UNIX')  and  sock.family == socket.AF_UNIX:
                line = self.conSock.recv_char_msg().rstrip()
                if not line:  # caller went away (perhaps another mpd seeing if I am here)
                    self.streamHandler.del_handler(self.conSock)
                    self.conSock.close()
                    self.conSock = 0
                    return
                errorMsg = ''
                try:
                    (kv1,kv2) = line.split(' ',1)  # 'realusername=xxx secretword=yyy'
                except:
                    errorMsg = 'failed to split this msg on " ": %s' % line
                if not errorMsg:
                    try:
                        (k1,self.conSock.realUsername) = kv1.split('=',1)
                    except:
                        errorMsg = 'failed to split first kv pair on "=": %s' % line
                if not errorMsg:
                    try:
                        (k2,secretword) = kv2.split('=',1)
                    except:
                        errorMsg = 'failed to split second kv pair on "=": %s' % line
                if not errorMsg  and  k1 != 'realusername':
                    errorMsg = 'first key is not realusername'
                if not errorMsg  and  k2 != 'secretword':
                    errorMsg = 'second key is not secretword'
                if not errorMsg  and  os.getuid() == 0  and  secretword != self.parmdb['MPD_SECRETWORD']:
                    errorMsg = 'invalid secretword to root mpd'
                if errorMsg:
                    try:
                        self.conSock.send_dict_msg({'error_msg': errorMsg})
                    except:
                        pass
                    self.streamHandler.del_handler(self.conSock)
                    self.conSock.close()
                    self.conSock = 0
                    return
                self.conSock.beingChallenged = 0
            else:
                msg = self.conSock.recv_dict_msg()
                if not msg:    # caller went away (perhaps another mpd seeing if I am here)
                    self.streamHandler.del_handler(self.conSock)
                    self.conSock.close()
                    self.conSock = 0
                    return
                if not msg.has_key('cmd')  or  msg['cmd'] != 'con_init':

                    mpd_print(1, 'console sent bad message :%s:' % (msg) )

                    try:  # try to let console know
                        self.conSock.send_dict_msg({'cmd':'invalid_msg_received_from_you'})
                    except:
                        pass
                    self.streamHandler.del_handler(self.conSock)
                    self.conSock.close()
                    self.conSock = 0
                    return
                self.streamHandler.set_handler(self.conSock,self.handle_console_input)
                self.conSock.beingChallenged = 1
                self.conSock.name = 'console'
                randNum = randrange(1,10000)
                randVal = sock.secretword + str(randNum)
                self.conSock.expectedResponse = md5new(randVal).digest()
                self.conSock.send_dict_msg({'cmd' : 'con_challenge', 'randnum' : randNum })
                self.conSock.realUsername = mpd_get_my_username()
            self.streamHandler.set_handler(self.conSock,self.handle_console_input)
            self.conSock.name = 'console'
        else:
            return  ## postpone it; hope the other one frees up soon
    def handle_console_input(self,sock):
        msg = self.conSock.recv_dict_msg()
        if not msg:
            mpd_print(0000, 'console has disappeared; closing it')
            self.streamHandler.del_handler(self.conSock)
            self.conSock.close()
            self.conSock = 0
            return
        if not msg.has_key('cmd'):

            mpd_print(1, 'console sent bad message :%s:' % msg)

            try:  # try to let console know
                self.conSock.send_dict_msg({ 'cmd':'invalid_msg_received_from_you' })
            except:
                pass
            self.streamHandler.del_handler(self.conSock)
            self.conSock.close()
            self.conSock = 0
            return
        if self.conSock.beingChallenged  and  msg['cmd'] != 'con_challenge_response':

            mpd_print(1, 'console did not respond to the con_challenge request; got msg=:%s:' % msg)

            try:  # try to let console know
                self.conSock.send_dict_msg({ 'cmd':'expected_con_challenge_response' })
            except:
                pass
            self.streamHandler.del_handler(self.conSock)
            self.conSock.close()
            self.conSock = 0
            return
        if msg['cmd'] == 'con_challenge_response':
            self.conSock.beingChallenged = 0
            self.conSock.realUsername = msg['realusername']
            if not msg.has_key('response'):
                try:  # try to let console know
                    self.conSock.send_dict_msg({ 'cmd':'missing_response_in_msg' })
                except:
                    pass
                self.streamHandler.del_handler(self.conSock)
                self.conSock.close()
                self.conSock = 0
                return
            elif msg['response'] != self.conSock.expectedResponse:
                try:  # try to let console know
                    self.conSock.send_dict_msg({ 'cmd':'invalid_response' })
                except:
                    pass
                self.streamHandler.del_handler(self.conSock)
                self.conSock.close()
                self.conSock = 0
                return
            self.conSock.send_dict_msg({ 'cmd':'valid_response' })
        elif msg['cmd'] == 'mpdrun':
            # permit anyone to run but use THEIR own username
            #   thus, override any username specified by the user
            if self.conSock.realUsername != 'root':
                msg['username'] = self.conSock.realUsername
                msg['users'] = { (0,msg['nprocs']-1) : self.conSock.realUsername }
            #
            msg['mpdid_mpdrun_start'] = self.myId
            msg['nstarted_on_this_loop'] = 0
            msg['first_loop'] = 1
            msg['ringsize'] = 0
            msg['ring_ncpus'] = 0
            
            self.PinRank = 0
            
            # maps rank => hostname
            msg['process_mapping'] = {}
            if msg.has_key('try_1st_locally'):
                self.do_mpdrun(msg)
            else:
                self.ring.rhsSock.send_dict_msg(msg)
            # send ack after job is going
        elif msg['cmd'] == 'get_mpdrun_values':
            msgToSend = { 'cmd' : 'response_get_mpdrun_values',
                          'mpd_version' : mpd_version(),
                          'mpd_ifhn' : self.myIfhn }
#            self.conSock.send_dict_msg(msgToSend)

            if self.maxRingSize != -1:
                msgToSend['max_size'] = self.maxRingSize
                self.conSock.send_dict_msg(msgToSend)
            else:
                msgToSend = { 'cmd' : 'calc_max_ring_size_and_ncpus',
                              'dest' : self.myId,
                              'max_size' : 1,

                              'ncpus_table' : { self.myHost : self.parmdb['MPD_NCPUS'] }

                            }
                self.ring.rhsSock.send_dict_msg(msgToSend)


        elif msg['cmd'] == 'get_ncpus_table':
            msgToSend = { 'cmd' : 'collect_ncpus_table', 'dest' : self.myId, 'ncpus_table' : { self.myHost : self.parmdb['MPD_NCPUS'] } }
            self.ring.rhsSock.send_dict_msg(msgToSend)
        elif msg['cmd'] == 'set_ncpus_equality':
            self.ncpusEquality = 1
            msgToSend = { 'cmd' : 'set_ncpus_equality', 'dest' : self.myId }
            self.ring.rhsSock.send_dict_msg(msgToSend)


        elif msg['cmd'] == 'get_mpd_hostname':
            msgToSend = { 'cmd' : 'mpd_hostname_response', 'mpd_hostname' : self.myHost}
            self.conSock.send_dict_msg(msgToSend)
        elif msg['cmd'] == 'get_mpd_ip':
            msgToSend = { 'cmd' : 'mpd_ip_response', 'mpd_ip' : self.ring.myIP}
            self.conSock.send_dict_msg(msgToSend)

        elif msg['cmd'] == 'mpdtrace':
            msgToSend = { 'cmd'     : 'mpdtrace_info',
                          'dest'    : self.myId,
                          'id'      : self.myId,
                          'ifhn'    : self.myIfhn,
                          'lhsport' : '%s' % (self.ring.lhsPort),
                          'lhsifhn' : '%s' % (self.ring.lhsIfhn),
                          'rhsport' : '%s' % (self.ring.rhsPort),
                          'rhsifhn' : '%s' % (self.ring.rhsIfhn) }
            self.ring.rhsSock.send_dict_msg(msgToSend)
            msgToSend = { 'cmd'  : 'mpdtrace_trailer', 'dest' : self.myId }
            self.ring.rhsSock.send_dict_msg(msgToSend)
            # do not send an ack to console now; will send trace info later
        elif msg['cmd'] == 'mpdallexit':
            if self.conSock.realUsername != self.myRealUsername:
                msgToSend = { 'cmd':'invalid_username_to_make_this_request' }
                self.conSock.send_dict_msg(msgToSend)
                self.streamHandler.del_handler(self.conSock)
                self.conSock.close()
                self.conSock = 0
                return
            # self.allExiting = 1  # doesn't really help here
            self.ring.rhsSock.send_dict_msg( {'cmd' : 'mpdallexit', 'src' : self.myId} )
            self.conSock.send_dict_msg( {'cmd' : 'mpdallexit_ack'} )
        elif msg['cmd'] == 'mpdexit':
            if self.conSock.realUsername != self.myRealUsername:
                msgToSend = { 'cmd':'invalid_username_to_make_this_request' }
                self.conSock.send_dict_msg(msgToSend)
                self.streamHandler.del_handler(self.conSock)
                self.conSock.close()
                self.conSock = 0
                return
            if msg['mpdid'] == 'localmpd':
                msg['mpdid'] = self.myId
            self.ring.rhsSock.send_dict_msg( {'cmd' : 'mpdexit', 'src' : self.myId,
                                              'done' : 0, 'dest' : msg['mpdid']} )
        elif msg['cmd'] == 'mpdringtest':
            msg['src'] = self.myId
            self.ring.rhsSock.send_dict_msg(msg)
            # do not send an ack to console now; will send ringtest info later
        elif msg['cmd'] == 'mpdlistjobs':
            msgToSend = { 'cmd'  : 'local_mpdid', 'id' : self.myId }
            self.conSock.send_dict_msg(msgToSend)
            for jobid in self.activeJobs.keys():
                for manPid in self.activeJobs[jobid]:
                    msgToSend = { 'cmd' : 'mpdlistjobs_info',
                                  'dest' : self.myId,
                                  'jobid' : jobid,
                                  'username' : self.activeJobs[jobid][manPid]['username'],
                                  'host' : self.myHost,
                                  'ifhn' : self.myIfhn,
                                  'clipid' : str(self.activeJobs[jobid][manPid]['clipid']),
                                  'sid' : str(manPid),  # may chg to actual sid later
                                  'pgm'  : self.activeJobs[jobid][manPid]['pgm'],
                                  'rank' : self.activeJobs[jobid][manPid]['rank'] }
                    self.conSock.send_dict_msg(msgToSend)
            msgToSend = { 'cmd'  : 'mpdlistjobs_trailer', 'dest' : self.myId }
            self.ring.rhsSock.send_dict_msg(msgToSend)
            # do not send an ack to console now; will send listjobs info later
        elif msg['cmd'] == 'mpdkilljob':
            # permit anyone to kill but use THEIR own username
            #   thus, override any username specified by the user
            if self.conSock.realUsername != 'root':
                msg['username'] = self.conSock.realUsername
            msg['src'] = self.myId
            msg['handled'] = 0
            if msg['mpdid'] == '':
                msg['mpdid'] = self.myId
            self.ring.rhsSock.send_dict_msg(msg)
            # send ack to console after I get this msg back and do the kill myself
        elif msg['cmd'] == 'mpdsigjob':
            # permit anyone to sig but use THEIR own username
            #   thus, override any username specified by the user
            if self.conSock.realUsername != 'root':
                msg['username'] = self.conSock.realUsername
            msg['src'] = self.myId
            msg['handled'] = 0
            if msg['mpdid'] == '':
                msg['mpdid'] = self.myId
            self.ring.rhsSock.send_dict_msg(msg)
            # send ack to console after I get this msg back
        elif msg['cmd'] == 'verify_hosts_in_ring':
            msgToSend = { 'cmd'  : 'verify_hosts_in_ring', 'dest' : self.myId,
                          'host_list' : msg['host_list'] }
            self.ring.rhsSock.send_dict_msg(msgToSend)
            # do not send an ack to console now; will send trace info later
        else:
            msgToSend = { 'cmd' : 'invalid_msg_received_from_you' }
            self.conSock.send_dict_msg(msgToSend)

            badMsg = 'invalid message received from the console: %s' % (str(msg))

            mpd_print(1, badMsg)
            if syslog_module_available:
                syslog.syslog(syslog.LOG_ERR,badMsg)
    def handle_man_input(self,sock):
        msg = sock.recv_dict_msg()
        if not msg:
            for jobid in self.activeJobs.keys():
                deleted = 0
                for manPid in self.activeJobs[jobid]:
                    if sock == self.activeJobs[jobid][manPid]['socktoman']:
                        mpd_print(mpd_dbg_level,\
                                  "Deleting %s %d" % (str(jobid),manPid))
                        del self.activeJobs[jobid][manPid]
                        if len(self.activeJobs[jobid]) == 0:
                            del self.activeJobs[jobid]
                        deleted = 1
                        break
                if deleted:
                    break
            self.streamHandler.del_handler(sock)
            sock.close()
            return
        if not msg.has_key('cmd'):

            mpd_print(1, 'invalid message from the mpdman daemon. msg=:%s:' % (msg) )

            msgToSend = { 'cmd' : 'invalid_msg' }
            sock.send_dict_msg(msgToSend)
            self.streamHandler.del_handler(sock)
            sock.close()
            return
	# Who asks, and why?  
        # We have a failure that deletes the spawnerManPid from the
	# activeJobs[jobid] variable.   The temporary work-around is
        # to ignore this request if the target process is no longer 
	# in the activeJobs table.
        if msg['cmd'] == 'client_info':
            jobid = msg['jobid']
            manPid = msg['manpid']
            self.activeJobs[jobid][manPid]['clipid'] = msg['clipid']
            if msg['spawner_manpid']  and  msg['rank'] == 0:
                if msg['spawner_mpd'] == self.myId:
                    spawnerManPid = msg['spawner_manpid']
                    mpd_print(mpd_dbg_level,\
                       "About to check %s:%s" % (str(jobid),str(spawnerManPid)))

                    if not self.activeJobs[jobid].has_key(spawnerManPid):
                        mpd_print(0,"Missing %d in %s" % (spawnerManPid,str(jobid)))
                    elif not self.activeJobs[jobid][spawnerManPid].has_key('socktoman'):
                        mpd_print(0,"Missing socktoman!")
                    else:
                        spawnerManSock = self.activeJobs[jobid][spawnerManPid]['socktoman']
                        msgToSend = { 'cmd' : 'spawn_done_by_mpd', 'rc' : 0, 'reason' : '' }
                        spawnerManSock.send_dict_msg(msgToSend)
                else:
                    self.ring.rhsSock.send_dict_msg(msg)
        elif msg['cmd'] == 'spawn':
            msg['mpdid_mpdrun_start'] = self.myId
            msg['spawner_mpd'] = self.myId
            msg['nstarted_on_this_loop'] = 0
            msg['first_loop'] = 1
            msg['jobalias'] = ''
            msg['stdin_dest'] = '0'
            msg['ringsize'] = 0
            msg['ring_ncpus'] = 0

            msg['job_abort_signal'] = 9 # SIGKILL by default

            msg['gdb'] = 0
            msg['gdba'] = ''
            msg['totalview'] = 0
            msg['ifhns'] = {}
            # maps rank => hostname
            msg['process_mapping'] = {}
            self.spawnQ.append(msg)
        elif msg['cmd'] == 'publish_name':
            self.pmi_published_names[msg['service']] = msg['port']
            msgToSend = { 'cmd' : 'publish_result', 'info' : 'ok' }
            sock.send_dict_msg(msgToSend)
        elif msg['cmd'] == 'lookup_name':
            if self.pmi_published_names.has_key(msg['service']):
                msgToSend = { 'cmd' : 'lookup_result', 'info' : 'ok',
                              'port' : self.pmi_published_names[msg['service']] }
                sock.send_dict_msg(msgToSend)
            else:
                msg['cmd'] = 'pmi_lookup_name'    # add pmi_
                msg['src'] = self.myId
                msg['port'] = 0    # invalid
                self.ring.rhsSock.send_dict_msg(msg)
        elif msg['cmd'] == 'unpublish_name':
            if self.pmi_published_names.has_key(msg['service']):
                del self.pmi_published_names[msg['service']]
                msgToSend = { 'cmd' : 'unpublish_result', 'info' : 'ok' }
                sock.send_dict_msg(msgToSend)
            else:
                msg['cmd'] = 'pmi_unpublish_name'    # add pmi_
                msg['src'] = self.myId
                self.ring.rhsSock.send_dict_msg(msg)
        else:

            mpd_print(1, 'invalid request from the mpdman daemon. msg=:%s:' % (msg) )

            msgToSend = { 'cmd' : 'invalid_request' }
            sock.send_dict_msg(msgToSend)

    def calculate_process_mapping(self,mapping_dict):
        # mapping_dict maps ranks => hostnames
        ranks = list(mapping_dict.keys())
        ranks.sort()

        # assign node ids based in first-come-first-serve order when iterating
        # over the ranks in increasing order
        next_id = 0
        node_ids = {}
        for rank in ranks:
            host = mapping_dict[rank]
            if not node_ids.has_key(host):
                node_ids[host] = next_id
                next_id += 1


        # maps {node_id_A: set([rankX,rankY,...]), node_id_B:...}
        node_to_ranks = {}
        for rank in ranks:
            node_id = node_ids[mapping_dict[rank]]
            if not node_to_ranks.has_key(node_id):
                node_to_ranks[node_id] = set([])
            node_to_ranks[node_id].add(rank)

        # we only handle two cases for now:
        # 1. block regular
        # 2. round-robin regular
        # we do handle "remainder nodes" that might not be full
        delta = -1
        max_ranks_per_node = 0
        for node_id in node_to_ranks.keys():
            last_rank = -1
            if len(node_to_ranks[node_id]) > max_ranks_per_node:
                max_ranks_per_node = len(node_to_ranks[node_id])
            ranks = list(node_to_ranks[node_id])
            ranks.sort()
            for rank in ranks:
                if last_rank != -1:
                    if delta == -1:
                        if node_id == 0:
                            delta = rank - last_rank
                        else:
                            # irregular case detected such as {0:A,1:B,2:B}
                            mpd_print(1, "irregular case A detected")
                            return ''
                    elif (rank - last_rank) != delta:
                        # irregular such as {0:A,1:B,2:A,3:A,4:B}
                        mpd_print(1, "irregular case B detected")
                        return ''
                last_rank = rank

        # another check (case caught in ticket #905) for layouts like {0:A,1:A,2:B,3:B,4:B}
        if len(node_to_ranks.keys()) > 1:
            first_size = len(node_to_ranks[0])
            last_size  = len(node_to_ranks[len(node_to_ranks.keys())-1])
            if (last_size > first_size):
                mpd_print(1, "irregular case C1 detected")
                return ''
            in_remainder = False
            node_ids = node_to_ranks.keys()
            node_ids.sort()
            for node_id in node_ids:
                node_size = len(node_to_ranks[node_id])
                if not in_remainder:
                    if node_size == first_size:
                        pass # OK
                    elif node_size == last_size:
                        in_remainder = True
                    else:
                        mpd_print(1, "irregular case C2 detected")
                        return ''
                else: # in_remainder
                    if node_size != last_size:
                        mpd_print(1, "irregular case C3 detected")
                        return ''

        num_nodes = len(node_to_ranks.keys())
        if delta == 1:
            return '(vector,(%d,%d,%d))' % (0,num_nodes,max_ranks_per_node)
        else:
            # either we are round-robin-regular (delta > 1) or there is only one
            # process per node (delta == -1), either way results in the same
            # mapping spec
            return '(vector,(%d,%d,%d))' % (0,num_nodes,1)

    def handle_lhs_input(self,sock):
        msg = self.ring.lhsSock.recv_dict_msg()
        if not msg:    # lost lhs; don't worry
            mpd_print(0, "CLOSING self.ring.lhsSock ", self.ring.lhsSock )
            self.streamHandler.del_handler(self.ring.lhsSock)
            self.ring.lhsSock.close()
            self.ring.lhsSock = 0
            return
        if msg['cmd'] == 'mpdrun'  or  msg['cmd'] == 'spawn':
            if  msg.has_key('mpdid_mpdrun_start')  \
            and msg['mpdid_mpdrun_start'] == self.myId:
                if msg['first_loop']:
                    self.currRingSize = msg['ringsize']
                    self.currRingNCPUs = msg['ring_ncpus']
                if msg['nstarted'] == msg['nprocs']:
                    
                    self.PinRank = 0
                    
                    # we have started all processes in the job, tell the
                    # requester this and stop forwarding the mpdrun/spawn
                    # message around the loop
                    if msg['cmd'] == 'spawn':
                        self.spawnInProgress = 0
                    if self.conSock:
                        msgToSend = { 'cmd' : 'mpdrun_ack',
                                      'ringsize' : self.currRingSize,
                                      'ring_ncpus' : self.currRingNCPUs}
                        self.conSock.send_dict_msg(msgToSend)
                    # Tell all MPDs in the ring the final process mapping.  In
                    # turn, they will inform all of their child mpdmans.
                    # Only do this in the case of a regular mpdrun.  The spawn
                    # case it too complicated to handle this way right now.
#                    if msg['cmd'] == 'mpdrun':
#                        process_mapping_str = self.calculate_process_mapping(msg['process_mapping'])
#                        msgToSend = { 'cmd' : 'process_mapping',
#                                      'jobid' : msg['jobid'],
#                                      'mpdid_mpdrun_start' : self.myId,
#                                      'process_mapping' : process_mapping_str }
#                        self.ring.rhsSock.send_dict_msg(msgToSend)
                    return
                if not msg['first_loop']  and  msg['nstarted_on_this_loop'] == 0:
                    if msg.has_key('jobid'):
                        if msg['cmd'] == 'mpdrun':
                            msgToSend = { 'cmd' : 'abortjob', 'src' : self.myId,
                                          'jobid' : msg['jobid'],
                                          'reason' : 'some_procs_not_started' }
                            self.ring.rhsSock.send_dict_msg(msgToSend)
                        else:  # spawn
                            msgToSend = { 'cmd' : 'startup_status', 'rc' : -1,
                                          'reason' : 'some_procs_not_started' }
                            jobid = msg['jobid']
                            manPid = msg['spawner_manpid']
                            manSock = self.activeJobs[jobid][manPid]['socktoman']
                            manSock.send_dict_msg(msgToSend)
                    if self.conSock:
                        msgToSend = { 'cmd' : 'job_failed',
                                      'reason' : 'some_procs_not_started',
                                      'remaining_hosts' : msg['hosts'] }
                        self.conSock.send_dict_msg(msgToSend)
                    return

# Aborting is executed using standard mpd job aborting procedure.
                if msg['nstarted_on_this_loop'] == -1:
                    if msg.has_key('jobid'):
                        msgToSend = {'cmd' : 'abortjob', 'src' : self.myId,
                                     'jobid' : msg['jobid'],
                                     'reason' : 'system limit of maximum number of open files has exceeded. Too many open files'}
                        self.ring.rhsSock.send_dict_msg(msgToSend)
                    if self.conSock:
                        msgToSend = {'cmd' : 'job_failed',
                                     'reason' : 'system limit of maximum number of open files has exceeded. Too many open files'}
                        self.conSock.send_dict_msg(msgToSend)
                    return

                msg['first_loop'] = 0
                msg['nstarted_on_this_loop'] = 0
            self.do_mpdrun(msg)

        elif msg['cmd'] == 'calc_max_ring_size_and_ncpus':
            if msg['dest'] == self.myId:
                msgToSend = { 'cmd' : 'set_max_ring_size_and_ncpus',
                              'max_size' : msg['max_size'],
                              'dest' : self.myId,
                              'ncpus_table' : msg['ncpus_table']
                              }
                self.ring.rhsSock.send_dict_msg(msgToSend)
            else:
                msg['max_size'] += 1
                msg['ncpus_table'][self.myHost] = self.parmdb['MPD_NCPUS']
                self.ring.rhsSock.send_dict_msg(msg)
        elif msg['cmd'] == 'set_max_ring_size_and_ncpus':
            if msg['dest'] == self.myId:
                self.maxRingSize = msg['max_size']
                self.ncpusTable = msg['ncpus_table']
                msgToSend = { 'cmd' : 'response_get_mpdrun_values',
                          'mpd_version' : mpd_version(),
                          'mpd_ifhn' : self.myIfhn,
                          'max_size' :  self.maxRingSize}
                self.conSock.send_dict_msg(msgToSend)
            else:
                self.maxRingSize = msg['max_size']
                self.ncpusTable = msg['ncpus_table']
                self.ring.rhsSock.send_dict_msg(msg)


        elif msg['cmd'] == 'collect_ncpus_table':
            if msg['dest'] == self.myId:
                msgToSend = { 'cmd' : 'set_ncpus_table', 'dest' : self.myId, 'ncpus_table' : msg['ncpus_table'] }
                self.ring.rhsSock.send_dict_msg(msgToSend)
            else:
                msg['ncpus_table'][self.myHost] = self.parmdb['MPD_NCPUS']
                self.ring.rhsSock.send_dict_msg(msg)
        elif msg['cmd'] == 'set_ncpus_table':
            if msg['dest'] == self.myId:
                self.ncpusTable = msg['ncpus_table']
                msgToSend = { 'cmd' : 'get_ncpus_table_response', 'ncpus_table' : msg['ncpus_table'] }
                self.conSock.send_dict_msg(msgToSend)
            else:
                self.ncpusTable = msg['ncpus_table']
                self.ring.rhsSock.send_dict_msg(msg)
        elif msg['cmd'] == 'set_ncpus_equality':
            if msg['dest'] == self.myId:
                msgToSend = { 'cmd' : 'set_ncpus_equality_response' }
                self.conSock.send_dict_msg(msgToSend)
            else:
                self.ncpusEquality = 1
                self.ring.rhsSock.send_dict_msg(msg)

#        elif msg['cmd'] == 'process_mapping':
#            # message transmission terminates once the message has made it all
#            # the way around the loop once
#            if msg['mpdid_mpdrun_start'] != self.myId:
#                self.ring.rhsSock.send_dict_msg(msg) # forward it on around
#
#            # send to all mpdman's for the jobid embedded in the msg
#            jobid = msg['jobid']
#
#            # there may be no entry for jobid in the activeJobs table if there
#            # weren't any processes from that job actually launched on our host
#            if self.activeJobs.has_key(jobid):
#                for manPid in self.activeJobs[jobid].keys():
#                    manSock = self.activeJobs[jobid][manPid]['socktoman']
#                    manSock.send_dict_msg(msg)
        elif msg['cmd'] == 'mpdtrace_info':
            if msg['dest'] == self.myId:
                if self.conSock:
                    self.conSock.send_dict_msg(msg)
            else:
                self.ring.rhsSock.send_dict_msg(msg)
        elif msg['cmd'] == 'mpdtrace_trailer':
            if msg['dest'] == self.myId:
                if self.conSock:
                    self.conSock.send_dict_msg(msg)
            else:
                msgToSend = { 'cmd'     : 'mpdtrace_info',
                              'dest'    : msg['dest'],
                              'id'      : self.myId,
                              'ifhn'    : self.myIfhn,
                              'lhsport' : '%s' % (self.ring.lhsPort),
                              'lhsifhn' : '%s' % (self.ring.lhsIfhn),
                              'rhsport' : '%s' % (self.ring.rhsPort),
                              'rhsifhn' : '%s' % (self.ring.rhsIfhn) }
                self.ring.rhsSock.send_dict_msg(msgToSend)
                self.ring.rhsSock.send_dict_msg(msg)
        elif msg['cmd'] == 'mpdlistjobs_info':
            if msg['dest'] == self.myId:
                if self.conSock:
                    self.conSock.send_dict_msg(msg)
            else:
                self.ring.rhsSock.send_dict_msg(msg)
        elif msg['cmd'] == 'mpdlistjobs_trailer':
            if msg['dest'] == self.myId:
                if self.conSock:
                    self.conSock.send_dict_msg(msg)
            else:
                for jobid in self.activeJobs.keys():
                    for manPid in self.activeJobs[jobid]:
                        msgToSend = { 'cmd' : 'mpdlistjobs_info',
                                      'dest' : msg['dest'],
                                      'jobid' : jobid,
                                      'username' : self.activeJobs[jobid][manPid]['username'],
                                      'host' : self.myHost,
                                      'ifhn' : self.myIfhn,
                                      'clipid' : str(self.activeJobs[jobid][manPid]['clipid']),
                                      'sid' : str(manPid),  # may chg to actual sid later
                                      'pgm' : self.activeJobs[jobid][manPid]['pgm'],
                                      'rank' : self.activeJobs[jobid][manPid]['rank'] }
                        self.ring.rhsSock.send_dict_msg(msgToSend)
                self.ring.rhsSock.send_dict_msg(msg)
        elif msg['cmd'] == 'mpdallexit':
            if self.allExiting:   # already seen this once
                self.exiting = 1  # set flag to exit main loop
            self.allExiting = 1
            self.ring.rhsSock.send_dict_msg(msg)
        elif msg['cmd'] == 'mpdexit':
            if msg['dest'] == self.myId:
                msg['done'] = 1    # do this first
            if msg['src'] == self.myId:    # may be src and dest
                if self.conSock:
                    if msg['done']:
                        self.conSock.send_dict_msg({'cmd' : 'mpdexit_ack'})
                    else:
                        self.conSock.send_dict_msg({'cmd' : 'mpdexit_failed'})
            else:
                self.ring.rhsSock.send_dict_msg(msg)
            if msg['dest'] == self.myId:
                self.exiting = 1
                self.ring.lhsSock.send_dict_msg( { 'cmd'     : 'mpdexiting',
                                                   'rhsifhn' : self.ring.rhsIfhn,
                                                   'rhsport' : self.ring.rhsPort })
        elif msg['cmd'] == 'mpdringtest':
            if msg['src'] != self.myId:
                self.ring.rhsSock.send_dict_msg(msg)
            else:
                numLoops = msg['numloops'] - 1
                if numLoops > 0:
                    msg['numloops'] = numLoops
                    self.ring.rhsSock.send_dict_msg(msg)
                else:
                    if self.conSock:    # may have closed it if user did ^C at console
                        self.conSock.send_dict_msg({'cmd' : 'mpdringtest_done' })
        elif msg['cmd'] == 'mpdsigjob':
            forwarded = 0
            if msg['handled']  and  msg['src'] != self.myId:
                self.ring.rhsSock.send_dict_msg(msg)
                forwarded = 1
            handledHere = 0
            for jobid in self.activeJobs.keys():
                sjobid = jobid.split('  ')  # jobnum and mpdid
                if (sjobid[0] == msg['jobnum']  and  sjobid[1] == msg['mpdid'])  \
                or (msg['jobalias']  and  sjobid[2] == msg['jobalias']):
                    for manPid in self.activeJobs[jobid].keys():
                        if self.activeJobs[jobid][manPid]['username'] == msg['username']  \
                        or msg['username'] == 'root':
                            manSock = self.activeJobs[jobid][manPid]['socktoman']
                            manSock.send_dict_msg( { 'cmd' : 'signal_to_handle',
                                                     's_or_g' : msg['s_or_g'],
                                                     'sigtype' : msg['sigtype'] } )
                            handledHere = 1
            if handledHere:
                msg['handled'] = 1
            if not forwarded  and  msg['src'] != self.myId:
                self.ring.rhsSock.send_dict_msg(msg)
            if msg['src'] == self.myId:
                if self.conSock:
                    self.conSock.send_dict_msg( {'cmd' : 'mpdsigjob_ack',
                                                 'handled' : msg['handled'] } )
        elif msg['cmd'] == 'mpdkilljob':
            forwarded = 0
            if msg['handled'] and msg['src'] != self.myId:
                self.ring.rhsSock.send_dict_msg(msg)
                forwarded = 1
            handledHere = 0
            for jobid in self.activeJobs.keys():
                sjobid = jobid.split('  ')  # jobnum and mpdid
                if (sjobid[0] == msg['jobnum']  and  sjobid[1] == msg['mpdid'])  \
                or (msg['jobalias']  and  sjobid[2] == msg['jobalias']):
                    for manPid in self.activeJobs[jobid].keys():
                        if self.activeJobs[jobid][manPid]['username'] == msg['username']  \
                        or msg['username'] == 'root':
                            try:
                                pgrp = manPid * (-1)  # neg manPid -> group
                                os.kill(pgrp,signal.SIGKILL)
                                cliPid = self.activeJobs[jobid][manPid]['clipid']
                                pgrp = cliPid * (-1)  # neg Pid -> group
                                os.kill(pgrp,signal.SIGKILL)  # neg Pid -> group
                                handledHere = 1
                            except:
                                pass
                    # del self.activeJobs[jobid]  ## handled when child goes away
            if handledHere:
                msg['handled'] = 1
            if not forwarded  and  msg['src'] != self.myId:
                self.ring.rhsSock.send_dict_msg(msg)
            if msg['src'] == self.myId:
                if self.conSock:
                    self.conSock.send_dict_msg( {'cmd' : 'mpdkilljob_ack',
                                                 'handled' : msg['handled'] } )
        elif msg['cmd'] == 'abortjob':
            if msg['src'] != self.myId:
                self.ring.rhsSock.send_dict_msg(msg)
            for jobid in self.activeJobs.keys():
                if jobid == msg['jobid']:
                    for manPid in self.activeJobs[jobid].keys():
                        manSocket = self.activeJobs[jobid][manPid]['socktoman']
                        if manSocket:
                            manSocket.send_dict_msg(msg)
                            sleep(0.5)  # give man a brief chance to deal with this
                        try:
                            pgrp = manPid * (-1)  # neg manPid -> group
                            os.kill(pgrp,signal.SIGKILL)
                            cliPid = self.activeJobs[jobid][manPid]['clipid']
                            pgrp = cliPid * (-1)  # neg Pid -> group
                            os.kill(pgrp,signal.SIGKILL)  # neg Pid -> group
                        except:
                            pass
                    # del self.activeJobs[jobid]  ## handled when child goes away
        elif msg['cmd'] == 'pulse':
            self.ring.lhsSock.send_dict_msg({'cmd':'pulse_ack'})
        elif msg['cmd'] == 'verify_hosts_in_ring':
            while self.myIfhn in msg['host_list']  or  self.myHost in msg['host_list']:
                if self.myIfhn in msg['host_list']:
                    msg['host_list'].remove(self.myIfhn)
                elif self.myHost in msg['host_list']:
                    msg['host_list'].remove(self.myHost)
            if msg['dest'] == self.myId:
                msgToSend = { 'cmd' : 'verify_hosts_in_ring_response',
                              'host_list' : msg['host_list'] }
                self.conSock.send_dict_msg(msgToSend)
            else:
                self.ring.rhsSock.send_dict_msg(msg)
        elif msg['cmd'] == 'pmi_lookup_name':
            if msg['src'] == self.myId:
                if msg.has_key('port') and msg['port'] != 0:
                    msgToSend = msg
                    msgToSend['cmd'] = 'lookup_result'
                    msgToSend['info'] = 'ok'
                else:
                    msgToSend = { 'cmd' : 'lookup_result', 'info' : 'unknown_service',
                                  'port' : 0}
                jobid = msg['jobid']
                manPid = msg['manpid']
                manSock = self.activeJobs[jobid][manPid]['socktoman']
                manSock.send_dict_msg(msgToSend)
            else:
                if self.pmi_published_names.has_key(msg['service']):
                    msg['port'] = self.pmi_published_names[msg['service']]
                self.ring.rhsSock.send_dict_msg(msg)
        elif msg['cmd'] == 'pmi_unpublish_name':
            if msg['src'] == self.myId:
                if msg.has_key('done'):
                    msgToSend = msg
                    msgToSend['cmd'] = 'unpublish_result'
                    msgToSend['info'] = 'ok'
                else:
                    msgToSend = { 'cmd' : 'unpublish_result', 'info' : 'unknown_service' }
                jobid = msg['jobid']
                manPid = msg['manpid']
                manSock = self.activeJobs[jobid][manPid]['socktoman']
                manSock.send_dict_msg(msgToSend)
            else:
                if self.pmi_published_names.has_key(msg['service']):
                    del self.pmi_published_names[msg['service']]
                    msg['done'] = 1
                self.ring.rhsSock.send_dict_msg(msg)
        elif msg['cmd'] == 'client_info':
            if msg['spawner_manpid']  and  msg['rank'] == 0:
                if msg['spawner_mpd'] == self.myId:
                    jobid = msg['jobid']
                    spawnerManPid = msg['spawner_manpid']
                    if self.activeJobs[jobid].has_key(spawnerManPid):
                        spawnerManSock = self.activeJobs[jobid][spawnerManPid]['socktoman']
                        msgToSend = { 'cmd' : 'spawn_done_by_mpd', 'rc' : 0, 'reason' : '' }
                        spawnerManSock.send_dict_msg(msgToSend)
                else:
                    self.ring.rhsSock.send_dict_msg(msg)
        else:

            mpd_print(1, 'unrecognized command from the left neighboring mpd daemon in the ring: %s' % (msg) )

    def handle_rhs_input(self,sock):
        if self.allExiting:
            return
        msg = sock.recv_dict_msg()
        if not msg:    # lost rhs; re-knit the ring
            if sock == self.ring.rhsSock:
                needToReenter = 1
            else:
                needToReenter = 0
            if sock == self.ring.rhsSock  and self.ring.lhsSock:
                self.streamHandler.del_handler(self.ring.lhsSock)
                self.ring.lhsSock.close()
                self.ring.lhsSock = 0
            if sock == self.ring.rhsSock  and self.ring.rhsSock:
                self.streamHandler.del_handler(self.ring.rhsSock)
                self.ring.rhsSock.close()
                self.ring.rhsSock = 0
            if needToReenter:

                mpd_print(1,'connection with the right neighboring mpd daemon was lost; attempting to re-enter the mpd ring')

                rc = self.ring.reenter_ring(lhsHandler=self.handle_lhs_input,
                                            rhsHandler=self.handle_rhs_input,
                                            ntries=16)
                if rc == 0:

                    mpd_print(1,'the daemon successfully reentered the mpd ring')

                else:

                    mpd_print(1,'the daemon failed to reenter the mpd ring')

                    sys.exit(-1)
            return
        if msg['cmd'] == 'pulse_ack':
            self.pulse_cntr = 0
        elif msg['cmd'] == 'mpdexiting':    # for mpdexit
            if self.ring.rhsSock:
                self.streamHandler.del_handler(self.ring.rhsSock)
                self.ring.rhsSock.close()
                self.ring.rhsSock = 0
            # connect to new rhs
            self.ring.rhsIfhn = msg['rhsifhn']
            self.ring.rhsPort = int(msg['rhsport'])
            if self.ring.rhsIfhn == self.myIfhn  and  self.ring.rhsPort == self.parmdb['MPD_LISTEN_PORT']:
                rv = self.ring.connect_rhs(rhsHost=self.ring.rhsIfhn,
                                           rhsPort=self.ring.rhsPort,
                                           rhsHandler=self.handle_rhs_input,
                                           numTries=3)
                if rv[0] <=  0:  # connect did not succeed; may try again

                    mpd_print(1,"the daemon failed to connect to the right neighboring mpd daemon")

                    sys.exit(-1)
                return
            self.ring.rhsSock = MPDSock(name='rhs')
            self.ring.rhsSock.connect((self.ring.rhsIfhn,self.ring.rhsPort))
            self.pulse_cntr = 0
            if not self.ring.rhsSock:

                mpd_print(1,'the handle_rhs_input function failed to obtain a socket for the right neighbouring mpd daemon')

                return
            msgToSend = { 'cmd' : 'request_to_enter_as_lhs', 'host' : self.myHost,
                          'ifhn' : self.myIfhn, 'port' : self.parmdb['MPD_LISTEN_PORT'] }
            self.ring.rhsSock.send_dict_msg(msgToSend)
            msg = self.ring.rhsSock.recv_dict_msg()
            if (not msg) or  \
               (not msg.has_key('cmd')) or  \
               (msg['cmd'] != 'challenge') or (not msg.has_key('randnum')):

                mpd_print(1, 'failed to receive challenge from the right neighboring mpd daemon; msg=:%s:' % (msg) )

            response = md5new(''.join([self.parmdb['MPD_SECRETWORD'],
                                       msg['randnum']])).digest()
            msgToSend = { 'cmd' : 'challenge_response',
                          'response' : response,
                          'host' : self.myHost, 'ifhn' : self.myIfhn,
                          'port' : self.parmdb['MPD_LISTEN_PORT'] }
            self.ring.rhsSock.send_dict_msg(msgToSend)
            msg = self.ring.rhsSock.recv_dict_msg()
            if (not msg) or  \
               (not msg.has_key('cmd')) or  \
               (msg['cmd'] != 'OK_to_enter_as_lhs'):

                mpd_print(1, 'failed to enter the mpd ring; msg=:%s:' % (msg) )

            mpd_print(0000,"GOT CONN TO %s %s" % (self.ring.rhsIfhn,self.ring.rhsPort))
#                mpd_print(1, 'NOT OK to enter ring; msg=:%s:' % (msg) )
            self.streamHandler.set_handler(self.ring.rhsSock,self.handle_rhs_input)
        else:

            mpd_print(1, 'unexpected message from the right neighboring mpd daemon; msg=:%s:' % (msg) )

        return

    def do_mpdrun(self,msg):

#        self.RanksToBeRunHere = [] # making it empty before starting the task

        if self.parmdb['MPD_LOGFILE_TRUNC_SZ'] >= 0:
            try:
                logSize = os.stat(self.logFilename)[stat.ST_SIZE]
                if logSize > self.parmdb['MPD_LOGFILE_TRUNC_SZ']:
                    self.logFile.truncate(self.parmdb['MPD_LOGFILE_TRUNC_SZ'])
            except:
                pass

        if msg.has_key('jobid'):
            jobid = msg['jobid']
        else:
            jobid = str(self.nextJobInt) + '  ' + self.myId + '  ' + msg['jobalias']
            self.nextJobInt += 1
            msg['jobid'] = jobid
        if msg['nstarted'] >= msg['nprocs']:
            
            self.PinRank = 0;
            
            self.ring.rhsSock.send_dict_msg(msg)  # forward it on around
            return

        if msg.has_key('nolocal') and self.myHost == msg['conhost']:
            self.ring.rhsSock.send_dict_msg(msg)  # forward it on around
            return
        handled = 0
        perhost = self.parmdb['MPD_NCPUS']
        if msg.has_key('perhost'):
            perhost = int(msg['perhost'])
# perhost redefinition 
        elif msg.has_key('impiperhost'):
            phv =  msg['impiperhost']
            if phv == 'allcores':
                perhost = self.PinCores
            elif phv == 'all':
                perhost = self.PinSpace
            elif phv.isdigit():
                perhost = int(phv)
            else:
                perhost = 0

            if perhost <= 0:
                perhost = self.parmdb['MPD_NCPUS']

        hosts = msg['hosts']


        max_rsize = self.maxRingSize

        if msg.has_key('nolocal'):

            max_rsize -= 1

        if msg['first_loop']:
            self.RanksToBeRunHere = [] # making it empty before starting the task

            self.PinRank = 0

            if self.ring.myIP in hosts.values():
                hostsKeys = msg['hosts'].keys()
                hostsKeys.sort()
                for ranks in hostsKeys:
                    if hosts[ranks] == self.ring.myIP:
                        (lorank,hirank) = ranks
                        for i in xrange(lorank, hirank+1):
                            self.RanksToBeRunHere.append(i)
            if '_any_' in hosts.values():
                hostsKeys = msg['hosts'].keys()
                hostsKeys.sort()
                done = 0
                if msg['ringsize'] == 0:
                    firstLocalRank = 0
                else:
                    firstLocalRank = msg['first_local_rank']
                msg['first_local_rank'] = firstLocalRank + perhost
                currLocalRank = firstLocalRank
                while not done:
                    for i in xrange(currLocalRank, currLocalRank+perhost):
                        if i >= msg['nprocs']:
                            done = 1
                            break
                        self.RanksToBeRunHere.append(i)
                    if msg.has_key('perhost') or self.ncpusEquality: # in this case local ncpus don't matter or they are 1

                        currLocalRank += perhost*max_rsize

                    else:
                        total_perhost = 0
                        for value in self.ncpusTable.values():
                            total_perhost += value    
                        currLocalRank += total_perhost
                    if currLocalRank >= msg['nprocs']:
                        done = 1
# FIXME: I am not sure whether we should perform 'any_from_pool'
# Here the self.RanksToBeRunHere is ready contains all the ranks to be started on this host


        if self.ring.myIP in hosts.values():

            hostsKeys = hosts.keys()
            hostsKeys.sort()
            for ranks in hostsKeys:

                if hosts[ranks] == self.ring.myIP:

                    (lorank,hirank) = ranks
                    for rank in range(lorank,hirank+1):

#                        self.run_one_cli(rank,msg)
                        rv = self.run_one_cli(rank,msg)
                        if rv == -1:
                            msg['nstarted_on_this_loop'] = -1
                            break

                        # we use myHost under the assumption that there is only
                        # one mpd per user on a given host.  The ifhn only
                        # affects how the MPDs communicate with each other, not
                        # which host they are on
                        msg['process_mapping'][rank] = self.myHost
                        msg['nstarted'] += 1
                        msg['nstarted_on_this_loop'] += 1
                    del msg['hosts'][ranks]
        elif '_any_from_pool_' in hosts.values():
            hostsKeys = hosts.keys()
            hostsKeys.sort()
            for ranks in hostsKeys:
                if hosts[ranks] == '_any_from_pool_':
                    (lorank,hirank) = ranks
                    hostSpecPool = msg['host_spec_pool']
                    if self.myIfhn in hostSpecPool  or  self.myHost in hostSpecPool:

#                        self.run_one_cli(lorank,msg)
                        rv = self.run_one_cli(lorank,msg)
                        if rv == -1:
                            msg['nstarted_on_this_loop'] = -1
                            break

                        msg['process_mapping'][lorank] = self.myHost
                        msg['nstarted'] += 1
                        msg['nstarted_on_this_loop'] += 1
                        del msg['hosts'][ranks]
                        if lorank < hirank:
                            msg['hosts'][(lorank+1,hirank)] = '_any_from_pool_'
                    break
        elif '_any_' in hosts.values():
            done = 0
            while not done:
                hostsKeys = hosts.keys()
                hostsKeys.sort()
                for ranks in hostsKeys:
                    if hosts[ranks] == '_any_':
                        (lorank,hirank) = ranks

#                        self.run_one_cli(lorank,msg)
                        rv = self.run_one_cli(lorank,msg)
                        if rv == -1:
                            msg['nstarted_on_this_loop'] = -1
                            done = 1
                            break

                        msg['process_mapping'][lorank] = self.myHost
                        msg['nstarted'] += 1
                        handled += 1
                        msg['nstarted_on_this_loop'] += 1
                        del msg['hosts'][ranks]
                        if lorank < hirank:
                            msg['hosts'][(lorank+1,hirank)] = '_any_'
                        # self.activeJobs maps:
                        # { jobid => { mpdman_pid => {...} } }
                        procsHereForJob = len(self.activeJobs[jobid].keys())
                        if handled >= perhost:
                            break  # out of for loop
                # if no more to start via any or enough started here
                if '_any_' not in hosts.values() \
                or handled >= perhost:
                    done = 1
        if msg['first_loop']:
            msg['ringsize'] += 1
            msg['ring_ncpus'] += self.parmdb['MPD_NCPUS']
        
        if msg['nstarted'] >= msg['nprocs']:
            self.PinRank = 0
        
        self.ring.rhsSock.send_dict_msg(msg)  # forward it on around
    def run_one_cli(self,currRank,msg):
        users = msg['users']
        for ranks in users.keys():
            (lo,hi) = ranks
            if currRank >= lo  and  currRank <= hi:
                username = users[ranks]
                break
        execs = msg['execs']
        for ranks in execs.keys():
            (lo,hi) = ranks
            if currRank >= lo  and  currRank <= hi:
                pgm = execs[ranks]
                break

        pathForExec = msg['paths']['global']
        paths = msg['paths']
        for ranks in paths.keys():
            if ranks == 'global':
                continue
            (lo,hi) = ranks
            if currRank >= lo  and  currRank <= hi:
                pathForExec = paths[ranks]
                break

        args = msg['args']
        for ranks in args.keys():
            (lo,hi) = ranks
            if currRank >= lo  and  currRank <= hi:
                pgmArgs = dumps(args[ranks])
                break
        
        envvars = msg['envvars']


        envalls = msg['envall']
    
        gl_envvars = {}

        local_envall = 0
        local_envuser = 0

        for ranks in envalls.keys():
            (lo,hi) = ranks
            if currRank >= lo  and  currRank <= hi:
                if envalls[ranks]:
                    gl_envvars = msg['gl_envvars'].copy()

                    if msg['envexcl'].has_key(ranks):
                        for exvar in msg['envexcl'][ranks]:
                            if gl_envvars.has_key(exvar):
                                del gl_envvars[exvar]
                if envalls[ranks] == 2:
                    local_envall = 1
                if envalls[ranks] == 3:
                    local_envuser = 1

                break
        if msg.has_key('MPICH_ifhn'):
            gl_envvars['MPICH_INTERFACE_HOSTNAME'] = msg['MPICH_ifhn']
        else:
            gl_envvars['MPICH_INTERFACE_HOSTNAME'] = self.myIfhn


        for ranks in envvars.keys():
            (lo,hi) = ranks
            if currRank >= lo  and  currRank <= hi:
                for k,v in envvars[ranks].items():
                    gl_envvars[k] = v
                break                                                                           


        pgmEnvVars = dumps(gl_envvars)

                                                                                    
        limits = msg['limits']
        for ranks in limits.keys():
            (lo,hi) = ranks
            if currRank >= lo  and  currRank <= hi:
                pgmLimits = dumps(limits[ranks])
                break

        cwd = msg['cwds']['global']
        cwds = msg['cwds']
        for ranks in cwds.keys():
            if ranks == 'global':
                continue
            (lo,hi) = ranks
            if currRank >= lo  and  currRank <= hi:
                cwd = cwds[ranks]
                break

        umasks = msg['umasks']
        for ranks in umasks.keys():
            (lo,hi) = ranks
            if currRank >= lo  and  currRank <= hi:
                pgmUmask = umasks[ranks]
                break
        man_env = {}
        if msg['ifhns'].has_key(currRank):
            man_env['MPICH_INTERFACE_HOSTNAME'] = msg['ifhns'][currRank]
        else:
            man_env['MPICH_INTERFACE_HOSTNAME'] = self.myIfhn
        man_env.update(os.environ)    # may only want to mov non-MPD_ stuff
        man_env['MPDMAN_MYHOST'] = self.myHost
        man_env['MPDMAN_MYIFHN'] = self.myIfhn

        man_env['MPDMAN_MYIP'] = self.ring.myIP

        man_env['MPDMAN_JOBID'] = msg['jobid']
        man_env['MPDMAN_CLI_PGM'] = pgm
        man_env['MPDMAN_CLI_PATH'] = pathForExec
        man_env['MPDMAN_PGM_ARGS'] = pgmArgs
        man_env['MPDMAN_PGM_ENVVARS'] = pgmEnvVars
        man_env['MPDMAN_PGM_LIMITS'] = pgmLimits
        man_env['MPDMAN_CWD'] = cwd
        man_env['MPDMAN_UMASK'] = pgmUmask
        man_env['MPDMAN_SPAWNED'] = str(msg['spawned'])
        if msg.has_key('spawner_manpid'):
            man_env['MPDMAN_SPAWNER_MANPID'] = str(msg['spawner_manpid'])
        else:
            man_env['MPDMAN_SPAWNER_MANPID'] = '0'
        if msg.has_key('spawner_mpd'):
            man_env['MPDMAN_SPAWNER_MPD'] = msg['spawner_mpd']
        else:
            man_env['MPDMAN_SPAWNER_MPD'] = ''
        man_env['MPDMAN_NPROCS'] = str(msg['nprocs'])
        man_env['MPDMAN_MPD_LISTEN_PORT'] = str(self.parmdb['MPD_LISTEN_PORT'])
        man_env['MPDMAN_MPD_CONF_SECRETWORD'] = self.parmdb['MPD_SECRETWORD']
        man_env['MPDMAN_CONHOST'] = msg['conhost']
        man_env['MPDMAN_CONIFHN'] = msg['conifhn']
        man_env['MPDMAN_CONPORT'] = str(msg['conport'])

        if not local_envall:
            man_env['MPDMAN_GENVUSER'] = str(msg['genvuser'])
        if local_envuser:
            man_env['MPDMAN_GENVUSER'] = '1'


        if msg.has_key('ordered_output'):
            man_env['MPDMAN_ORDERED_OUTPUT'] = str(msg['ordered_output'])
        else:
            man_env['MPDMAN_ORDERED_OUTPUT'] = 0
        if msg.has_key('mpd_output_chunk_size'):
            man_env['MPDMAN_OUTPUT_CHUNK_SIZE'] = str(msg['mpd_output_chunk_size'])


        man_env['MPDMAN_JOB_FAST_STARTUP'] = str(msg['job_fast_startup'])

        
        if self.PinRank == 0:
            self.PinOption = pin_Option(gl_envvars, self.PinCase, self.CpuInfo,len(self.RanksToBeRunHere))
            self.PinMode = pin_Mode(gl_envvars, self.PinCase, self.PinSpace)
#            self.PinMode = self.PinOption['mode']
            self.PinList = pin_CpuList(self.PinOption, self.CpuInfo)
            self.DomainSet = pin_DomainSet(self.PinOption, self.CpuInfo)
            self.PinRange = len(self.PinList)
            self.DomRange = len(self.DomainSet)
            self.PinCpu = -1
        # 
        if self.PinMode == 'off':
            pass
        elif not self.PinRange or self.PinMode == 'na':
            self.PinMode = 'off'
        else:
            self.PinCpu = self.PinList[(self.PinRank % self.PinRange)]
        man_env['MPDMAN_PINMODE'] = self.PinMode
        man_env['MPDMAN_PINCPU'] = str(self.PinCpu)
        
        if self.PinMode != 'off' and self.PinCpu != -1:
            r_list = []
            s_size = len(self.RanksToBeRunHere)
            if self.DomainSet:
                for i in xrange(s_size):
                    r_list.append(str(self.RanksToBeRunHere[i]) + " " + self.DomainSet[(i % self.DomRange)][0])
            else:
                for i in xrange(s_size):
                    r_list.append(str(self.RanksToBeRunHere[i]) + " " + str(self.PinList[(i % self.PinRange)]))
            s_list = ",".join(r_list)
        else:
            s_size = 0
            s_list = "0"
        man_env['MPDMAN_PINMAP'] = s_list
        man_env['MPDMAN_PINMAPSIZE'] = str(s_size)
        
        
        man_env['MPDMAN_CPUINFO'] = dumps(self.CpuInfo)
        if self.DomainSet and self.PinMode != 'off':
            man_env['MPDMAN_DOMAIN'] = ','.join(self.DomainSet[(self.PinRank % len(self.DomainSet))])
        else:
            man_env['MPDMAN_DOMAIN'] = ''
        
        
        if gl_envvars.has_key('I_MPI_RANK_MULTIPLIER'):
    	    man_env['MPDMAN_RANK_MULTIPLIER'] = gl_envvars['I_MPI_RANK_MULTIPLIER']
        else:
    	    man_env['MPDMAN_RANK_MULTIPLIER'] = '1'
        man_env['MPDMAN_RANK'] = str(currRank)
        man_env['MPDMAN_POS_IN_RING'] = str(msg['nstarted'])
        man_env['MPDMAN_STDIN_DEST'] = msg['stdin_dest']
        man_env['MPDMAN_TOTALVIEW'] = str(msg['totalview'])
        man_env['MPDMAN_GDB'] = str(msg['gdb'])

        man_env['MPDMAN_JOB_ABORT_SIGNAL'] = msg['job_abort_signal']


        if msg.has_key('gdba'):
            man_env['MPDMAN_GDBA'] = str(msg['gdba'])  # for attach to running pgm
        else:
            man_env['MPDMAN_GDBA'] = ''

        fullDirName = os.path.abspath(os.path.split(sys.argv[0])[0])  # normalize
        man_env['MPDMAN_FULLPATHDIR'] = fullDirName    # used to find gdbdrv
        man_env['MPDMAN_SINGINIT_PID']  = str(msg['singinitpid'])
        man_env['MPDMAN_SINGINIT_PORT'] = str(msg['singinitport'])
        man_env['MPDMAN_LINE_LABELS_FMT'] = msg['line_labels']
        if msg.has_key('rship'):
            man_env['MPDMAN_RSHIP'] = msg['rship']
            man_env['MPDMAN_MSHIP_HOST'] = msg['mship_host']
            man_env['MPDMAN_MSHIP_PORT'] = str(msg['mship_port'])
        if msg.has_key('doing_bnr'):
            man_env['MPDMAN_DOING_BNR'] = '1'
        else:
            man_env['MPDMAN_DOING_BNR'] = '0'
        if msg['nstarted'] == 0:
            manKVSTemplate = '%s_%s_%d' % \
                             (self.myHost,self.parmdb['MPD_LISTEN_PORT'],self.kvs_cntr)
            manKVSTemplate = sub('\.','_',manKVSTemplate)  # chg magpie.cs to magpie_cs
            manKVSTemplate = sub('\-','_',manKVSTemplate)  # chg node-0 to node_0
            self.kvs_cntr += 1
            msg['kvs_template'] = manKVSTemplate
        man_env['MPDMAN_KVS_TEMPLATE'] = msg['kvs_template']
        msg['username'] = username
        if hasattr(os,'fork'):
            (manPid,toManSock) = self.launch_mpdman_via_fork(msg,man_env)
            if not manPid:
                print '**** mpd: launch_client_via_fork_exec failed; exiting'
        elif subprocess_module_available:
            (manPid,toManSock) = self.launch_mpdman_via_subprocess(msg,man_env)
        else:

            mpd_print(1,'neither fork nor subprocess python module is available, check python installation')

            sys.exit(-1)

        if not manPid and not toManSock:
            return -1

        
        self.PinRank += 1
        
        jobid = msg['jobid']
        if not self.activeJobs.has_key(jobid):
            self.activeJobs[jobid] = {}
        self.activeJobs[jobid][manPid] = { 'pgm' : pgm, 'rank' : currRank,
                                           'username' : username,
                                           'clipid' : -1,    # until report by man
                                           'socktoman' : toManSock }

        return 0

    def launch_mpdman_via_fork(self,msg,man_env):
        man_env['MPDMAN_HOW_LAUNCHED'] = 'FORK'
        currRank = int(man_env['MPDMAN_RANK'])
        manListenSock = MPDListenSock('',0,name='tempsock')
        manListenPort = manListenSock.getsockname()[1]
        if msg['nstarted'] == 0:
            manEntryIfhn = ''
            manEntryPort = 0
            msg['pos0_host'] = self.myHost
            msg['pos0_ifhn'] = self.myIfhn
            msg['pos0_port'] = str(manListenPort)
            man_env['MPDMAN_POS0_IFHN'] = self.myIfhn
            man_env['MPDMAN_POS0_PORT'] = str(manListenPort)
        else:
            manEntryIfhn = msg['entry_ifhn']
            manEntryPort = msg['entry_port']
            man_env['MPDMAN_POS0_IFHN'] = msg['pos0_ifhn']
            man_env['MPDMAN_POS0_PORT'] = msg['pos0_port']
        man_env['MPDMAN_LHS_IFHN']  = manEntryIfhn
        man_env['MPDMAN_LHS_PORT'] = str(manEntryPort)
        man_env['MPDMAN_MY_LISTEN_FD'] = str(manListenSock.fileno())
        man_env['MPDMAN_MY_LISTEN_PORT'] = str(manListenPort)
        mpd_print(mpd_dbg_level,"About to get sockpair for mpdman")
        (toManSock,toMpdSock) = mpd_sockpair()

        if not toManSock and not toMpdSock:
            return (0,0)

        toManSock.name = 'to_man'
        toMpdSock.name = 'to_mpd'  ## to be used by mpdman below
        man_env['MPDMAN_TO_MPD_FD'] = str(toMpdSock.fileno())
        self.streamHandler.set_handler(toManSock,self.handle_man_input)
        msg['entry_host'] = self.myHost
        msg['entry_ifhn'] = self.myIfhn
        msg['entry_port'] = manListenPort
        maxTries = 6
        numTries = 0
        while numTries < maxTries:
            try:
                manPid = os.fork()
                errinfo = 0
            except OSError, errinfo:
                pass  ## could check for errinfo.errno == 35 (resource unavailable)
            if errinfo:
                sleep(1)
                numTries += 1
            else:
                break
        if numTries >= maxTries:
            return (0,0)
        if manPid == 0:
            self.conListenSock = 0    # don't want to clean up console if I am manager
            self.myId = '%s_man_%d' % (self.myHost,self.myPid)
            mpd_set_my_id(self.myId)
            self.streamHandler.close_all_active_streams()
            os.setpgrp()
            os.environ = man_env
            if hasattr(os,'getuid')  and  os.getuid() == 0  and  pwd_module_available:
                username = msg['username']
                try:
                    pwent = pwd.getpwnam(username)
                except:
                    mpd_print(1,'invalid username :%s: on %s' % (username,self.myHost))
                    msgToSend = {'cmd' : 'job_failed', 'reason' : 'invalid_username',
                                 'username' : username, 'host' : self.myHost }
                    self.conSock.send_dict_msg(msgToSend)
                    return
                uid = pwent[2]
                gid = pwent[3]
                os.setgroups(mpd_get_groups_for_username(username))
                os.setregid(gid,gid)
                try:
                    os.setreuid(uid,uid)
                except OSError, errmsg1:
                    try:
                        os.setuid(uid)
                    except OSError, errmsg2:
                        mpd_print(1,"unable to perform setreuid or setuid")
                        sys.exit(-1)
            import atexit    # need to use full name of _exithandlers
            atexit._exithandlers = []    # un-register handlers in atexit module
            # import profile
            # print 'profiling the manager'
            # profile.run('mpdman()')
            mpdman = MPDMan()
            mpdman.run()
            sys.exit(0)  # do NOT do cleanup (eliminated atexit handlers above)
        # After the fork, if we're the parent, close the other side of the
        # mpdpair sockets, as well as the listener socket
        manListenSock.close()
        toMpdSock.close()
        return (manPid,toManSock)
    def launch_mpdman_via_subprocess(self,msg,man_env):
        man_env['MPDMAN_HOW_LAUNCHED'] = 'SUBPROCESS'
        currRank = int(man_env['MPDMAN_RANK'])
        if msg['nstarted'] == 0:
            manEntryIfhn = ''
            manEntryPort = 0
        else:
            manEntryIfhn = msg['entry_ifhn']
            manEntryPort = msg['entry_port']
            man_env['MPDMAN_POS0_IFHN'] = msg['pos0_ifhn']
            man_env['MPDMAN_POS0_PORT'] = msg['pos0_port']
        man_env['MPDMAN_LHS_IFHN']  = manEntryIfhn
        man_env['MPDMAN_LHS_PORT'] = str(manEntryPort)
        tempListenSock = MPDListenSock()
        man_env['MPDMAN_MPD_PORT'] = str(tempListenSock.getsockname()[1])
        # python_executable = '\Python24\python.exe'
        python_executable = 'python2.4'
        fullDirName = man_env['MPDMAN_FULLPATHDIR']
        manCmd = os.path.join(fullDirName,'mpdman.py')
        runner = subprocess.Popen([python_executable,'-u',manCmd],  # only one 'python' arg
                                  bufsize=0,
                                  env=man_env,
                                  close_fds=False)
                                  ### stdin=subprocess.PIPE,stdout=subprocess.PIPE,
                                  ### stderr=subprocess.PIPE)
        manPid = runner.pid
        oldTimeout = socket.getdefaulttimeout()
        socket.setdefaulttimeout(8)
        try:
            (toManSock,toManAddr) = tempListenSock.accept()
        except Exception, errmsg:
            toManSock = 0
        socket.setdefaulttimeout(oldTimeout)
        tempListenSock.close()
        if not toManSock:

            mpd_print(1,'failed to receive message from the launched mpdman daemon')

            return (0,0)
        msgFromMan = toManSock.recv_dict_msg()
        if not msgFromMan  or  not msgFromMan.has_key('man_listen_port'):
            toManSock.close()

            mpd_print(1,'invalid message from the launched mpdman daemon')

            return (0,0)
        manListenPort = msgFromMan['man_listen_port']
        if currRank == 0:
            msg['pos0_host'] = self.myHost
            msg['pos0_ifhn'] = self.myIfhn
            msg['pos0_port'] = str(manListenPort)
        msg['entry_host'] = self.myHost
        msg['entry_ifhn'] = self.myIfhn
        msg['entry_port'] = manListenPort
        return (manPid,toManSock)

# code for testing
if __name__ == '__main__':
    mpd = MPD()
    mpd.run()
