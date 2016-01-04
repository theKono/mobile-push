#!/usr/bin/env python

# standard library imports

# third party related imports
from mock import MagicMock

# local library imports
from mobile_push.actors.create_gcm_token import CreateGcmTokenActor
from mobile_push.config import setting
from ..base import BaseTestCase


class TestRun(BaseTestCase):

    def setUp(self):

        self.actor = CreateGcmTokenActor()
        self.actor.sns_conn = MagicMock()

    def test_when_token_is_not_present(self):

        self.actor.run({'args': {}})
        self.assertFalse(self.actor.sns_conn.create_platform_endpoint.called)

    def test_when_everything_is_ok(self):

        self.actor.sns_conn.create_platform_endpoint.return_value = {
            'CreatePlatformEndpointResponse': {
                'CreatePlatformEndpointResult': {'EndpointArn': 'an-arn'},
                'ResponseMetadata': {'RequestId': 'xxx'}
            }
        }

        self.actor.run({'args': {'token': 'qq', 'user_data': {}}})
        call_args = self.actor.sns_conn.create_platform_endpoint.call_args_list

        for ix, (_, arn) in enumerate(setting.items('sns:gcm-applications')):
            args, kwargs = call_args[ix]
            self.assertEqual(kwargs, {
                'platform_application_arn': arn,
                'token': 'qq',
                'custom_user_data': '{}'
            })

