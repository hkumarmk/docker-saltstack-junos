# -*- coding: utf-8 -*-
# DO NOT ALTER OR REMOVE COPYRIGHT NOTICES OR THIS FILE HEADER
#
# Copyright 2016 Juniper Networks, Inc.
# All rights reserved.
#
# Licensed under the Juniper Networks Script Software License (the "License").
# You may not use this script file except in compliance with the License, which is located at
# http://www.juniper.net/support/legal/scriptlicense/
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Please make sure to run this file as a root user

'''
Beacon to fire events at specific log messages. 

.. code-block:: yaml

'''

# Import Python libs
from __future__ import absolute_import
import os
import struct
import logging

# Import salt libs
import salt.utils


try:
    import re
    HAS_REGEX = True
except ImportError:
    HAS_REGEX = False

__virtualname__ = 'log'
LOC_KEY = 'log.loc'

log = logging.getLogger(__name__)


def __virtual__():
    if not salt.utils.is_windows() and HAS_REGEX:
        return __virtualname__
    return False


def _get_loc():
    '''
    return the active file location
    '''
    if LOC_KEY in __context__:
        return __context__[LOC_KEY]


def __validate__(config):
    '''
    Validate the beacon configuration
    '''
    # Configuration for log beacon should be a list of dicts
    if not isinstance(config, dict):
        return False, ('Configuration for log beacon must be a dictionary.')
    return True, 'Valid beacon configuration'


#TODO: match values should be returned in the event
def beacon(config):
    '''
    Read the log file and return match whole string

    .. code-block:: yaml

        beacons:
            log:
              file: <path>
	      <tag>:
		regex: <pattern>	
    '''
    ret = []

    if 'file' not in config:	
       event = {'tag': tag, 'match': 'no', 'raw': '', 'error': 'file not defined in config'}
       ret.append(event)
       return ret
       

    with salt.utils.fopen(config['file'], 'r') as fp_:
        loc = __context__.get(LOC_KEY, 0)
        if loc == 0:
            fp_.seek(0, 2)
            __context__[LOC_KEY] = fp_.tell()
            return ret
	
        fp_.seek(0, 2)
        __context__[LOC_KEY] = fp_.tell()
        fp_.seek(loc)

        txt = fp_.read()

        d = {}
        for tag in config:
	    if 'regex' not in config[tag]:
		continue
	    if len(config[tag]['regex']) < 1:
		continue
	    try:  
               d[tag] = re.compile(r'{0}'.format(config[tag]['regex']))
            except:
               event = {'tag': tag, 'match': 'no', 'raw': '', 'error': 'bad regex'}
               ret.append(event)

        for line in txt.splitlines():
            for tag, reg in d.items():
               try:
                  m = reg.match(line)
                  if m:
                      event = {'tag': tag, 'match': 'yes', 'raw': line, 'error': ''}
	              ret.append(event)
	       except:	  
                  event = {'tag': tag, 'match': 'no', 'raw':'', 'error': 'bad match'}
	          ret.append(event)
    return ret
