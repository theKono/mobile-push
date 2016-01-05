#!/usr/bin/env python

# standard library imports

# third party related imports
from mock import MagicMock
import ujson

# local library imports
from mobile_push.actors.create_apns_token import CreateApnsTokenActor
from mobile_push.config import setting
from mobile_push.db import ApnsToken, Session
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


class TestGetEndpointArnFromResponse(BaseTestCase):

    def setUp(self):

        self.actor = CreateApnsTokenActor()

    def test(self):

        api_response = {
            'CreatePlatformEndpointResponse': {
                'CreatePlatformEndpointResult': {'EndpointArn': 'an-arn'},
                'ResponseMetadata': {'RequestId': 'xxx'}
            }
        }
        self.assertEqual(
            self.actor.get_endpoint_arn_from_response(api_response),
            'an-arn'
        )


class TestGetEndpointArnFromErrorMessage(BaseTestCase):

    def setUp(self):

        self.actor = CreateApnsTokenActor()

    def test(self):

        message = ujson.dumps({
            'Error': {
                'Code': 'InvalidParameter',
                'Message': (
                    'Invalid parameter: Token Reason: Endpoint xxx already '
                    'exists with the same Token, but different attributes.'
                ),
                'Type': 'Sender'
            },
            'RequestId': 'ooxx'
        })
        err = Exception(message)

        self.assertEqual(
            self.actor.get_endpoint_arn_from_error_message(err),
            'xxx'
        )


class TestSaveEndpointArn(BaseTestCase):

    def setUp(self):

        self.actor = CreateApnsTokenActor()

    def test(self):

        self.actor.save_endpoint_arn('app-arn', 'token', 'qq', 'endpoint_arn')

        session = Session()
        apns_token = session.query(ApnsToken).first()

        self.assertEqual(apns_token.token, 'token')
        self.assertEqual(apns_token.application_arn, 'app-arn')
        self.assertEqual(apns_token.endpoint_arn, 'endpoint_arn')
        self.assertEqual(apns_token.user_data, 'qq')


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
