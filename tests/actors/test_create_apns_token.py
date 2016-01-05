#!/usr/bin/env python

# standard library imports

# third party related imports
from mock import MagicMock

# local library imports
from mobile_push.actors.create_apns_token import CreateApnsTokenActor
from mobile_push.config import setting
from ..base import BaseTestCase


class TestIterApplicationArns(BaseTestCase):

    def setUp(self):

        self.actor = CreateApnsTokenActor()

    def test(self):

        self.assertEqual(
            list(self.actor.iter_application_arns()),
            [pair[1] for pair in setting.items('sns:apns-applications')]
        )


class TestCallSnsApi(BaseTestCase):

    def setUp(self):

        self.actor = CreateApnsTokenActor()
        self.actor.sns_conn = MagicMock()

    def test(self):

        app_arn = 'an-app-arn'
        token = 'a-token'
        user_data = 'this is user data'

        self.actor.sns_conn.create_platform_endpoint.return_value = True
        self.assertTrue(self.actor.call_sns_api(app_arn, token, user_data))
        self.actor.sns_conn.create_platform_endpoint.assert_called_with(
            platform_application_arn=app_arn,
            token=token,
            custom_user_data=user_data
        )


class TestRun(BaseTestCase):

    def setUp(self):

        self.actor = CreateApnsTokenActor()
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

        for ix, (_, arn) in enumerate(setting.items('sns:apns-applications')):
            args, kwargs = call_args[ix]
            self.assertEqual(kwargs, {
                'platform_application_arn': arn,
                'token': 'qq',
                'custom_user_data': '{}'
            })
