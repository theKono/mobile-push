#!/usr/bin/env python

# standard library imports
from ConfigParser import SafeConfigParser
import os.path

# third party related imports

# local library imports


__all__ = ['setting']


setting = SafeConfigParser()
env = os.environ.get('MOBILE_PUSH_ENV', 'development')
cwd = os.path.dirname(os.path.abspath(__file__))
setting.read(os.path.join(cwd, '..', env + '.ini'))
