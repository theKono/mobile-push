#!/usr/bin/env python

# standard library imports

# third party related imports
import unittest2 as unittest

# local library imports
from mobile_push.db import Base, engine


class BaseTestCase(unittest.TestCase):

    def tearDown(self):

        connection = engine.connect()
        tran = connection.begin()

        for t in Base.metadata.sorted_tables:
            connection.execute(t.delete())

        tran.commit()
