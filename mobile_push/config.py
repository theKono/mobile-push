#!/usr/bin/env python

# standard library imports
from ConfigParser import SafeConfigParser
import os.path
import sys

# third party related imports

# local library imports


__all__ = ['setting']
setting = SafeConfigParser()

if 'MOBILE_PUSH_CONFIG' not in os.environ:
    sys.exit('Environment variable MOBILE_PUSH_CONFIG is not set')

config_path = os.environ['MOBILE_PUSH_CONFIG']
os.path.exists(config_path) or sys.exit('Cannot find %s' % config_path)
setting.read(config_path)
