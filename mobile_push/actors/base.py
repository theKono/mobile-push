#!/usr/bin/env python
# pylint: disable=missing-docstring

# standard library imports

# third party related imports
from boto.sns import connect_to_region

# local library imports
from mobile_push.config import setting


class BaseActor(object):

    def __init__(self):

        self._sns_conn = None

    def connect_sns(self):

        if self._sns_conn is not None:
            return self._sns_conn

        self._sns_conn = connect_to_region(setting.get('sns', 'region'))
        return self._sns_conn

    def run(self, message):

        raise NotImplementedError()
