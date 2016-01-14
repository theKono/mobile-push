#!/usr/bin/env python

# standard library imports

# third party related imports
from mock import MagicMock

# local library imports
from mobile_push.actors.direct_publish import DirectPublishActor
from ..base import BaseTestCase


class TestCallSnsApi(BaseTestCase):

    def setUp(self):

        self.actor = DirectPublishActor()
        self.sns_conn = MagicMock()
        self.actor.connect_sns = MagicMock(return_value=self.sns_conn)

    def test(self):

        self.actor.call_sns_api('arn', 'message')
        self.sns_conn.publish.assert_called_with(
            message='message',
            message_structure='json',
            target_arn='arn'
        )


class TestRun(BaseTestCase):

    def setUp(self):

        self.actor = DirectPublishActor()
        self.actor.find_token_endpoint_arns = MagicMock(return_value=['arn'])
        self.actor.call_sns_api = MagicMock()

    def test(self):

        self.actor.run({'args': {'tokens': ['qq'], 'message': 'hello'}})
        self.actor.call_sns_api.assert_called_with('arn', 'hello')
