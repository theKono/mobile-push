#!/usr/bin/env python

# standard library imports

# third party related imports
import unittest2 as unittest

# local library imports
from mobile_push.message_router import MessageRouter


class TestGetActor(unittest.TestCase):

    def setUp(self):

        self.original_table = MessageRouter.TABLE
        self.message = {'action': 'kill'}

    def tearDown(self):

        MessageRouter.TABLE = self.original_table

    def test_when_no_matching_action(self):

        MessageRouter.TABLE = {}
        mr = MessageRouter(self.message)

        with self.assertRaises(MessageRouter.ActionError):
            mr.get_actor()

    def test_when_there_is_matching_action(self):

        class DumbActor(object):
            pass

        MessageRouter.TABLE = {'kill': DumbActor}
        mr = MessageRouter(self.message)
        self.assertIsInstance(mr.get_actor(), DumbActor)
