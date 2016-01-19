#!/usr/bin/env python

# standard library imports

# third party related imports
from boto.exception import BotoServerError
from mock import MagicMock
import ujson

# local library imports
from mobile_push.actors.create_apns_token import CreateApnsTokenActor
from mobile_push.config import setting
from mobile_push.db import ApnsToken, Session
from ..base import BaseTestCase
from ..factories.apns_token import ApnsTokenFactory


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
        self.sns_conn = MagicMock()
        self.actor.connect_sns = MagicMock(return_value=self.sns_conn)

    def test(self):

        app_arn = 'an-app-arn'
        token = 'a-token'
        user_data = 'this is user data'

        self.sns_conn.create_platform_endpoint.return_value = True
        self.assertTrue(self.actor.call_sns_api(app_arn, token, user_data))
        self.sns_conn.create_platform_endpoint.assert_called_with(
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

        err = Exception(ujson.dumps({
            'Error': {
                'Code': 'InvalidParameter',
                'Message': (
                    'Invalid parameter: Token Reason: Endpoint xxx already '
                    'exists with the same Token, but different attributes.'
                ),
                'Type': 'Sender'
            },
            'RequestId': 'ooxx'
        }))

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


class TestHasPlatformEndpoint(BaseTestCase):

    def setUp(self):

        self.actor = CreateApnsTokenActor()

    def test_when_apns_token_exist(self):

        ApnsTokenFactory.create(token='ttt', application_arn='aaa')
        self.assertTrue(self.actor.has_platform_endpoint('ttt', 'aaa'))

    def test_when_apns_token_does_not_exist(self):

        self.assertFalse(self.actor.has_platform_endpoint('ttt', 'aaa'))


class TestRun(BaseTestCase):

    def setUp(self):

        self.actor = CreateApnsTokenActor()
        self.actor.connect_sns = MagicMock(return_value=MagicMock())

    def test_when_token_is_not_present(self):

        self.actor.call_sns_api = MagicMock()
        self.actor.run({'args': {}})
        self.assertFalse(self.actor.call_sns_api.called)

    def test_when_platform_endpoint_exist(self):

        self.actor.has_platform_endpoint = MagicMock(return_value=True)
        self.actor.call_sns_api = MagicMock()
        self.actor.run({'args': {'token': 'qq', 'user_data': {}}})
        self.assertFalse(self.actor.call_sns_api.called)

    def test_when_sns_api_raises_boto_server_error(self):

        err = BotoServerError(403, 'qq')

        self.actor.iter_application_arns = MagicMock(return_value=['app-arn'])
        self.actor.call_sns_api = MagicMock(side_effect=err)
        self.actor.get_endpoint_arn_from_error_message = \
            MagicMock(return_value='arn')
        self.actor.save_endpoint_arn = MagicMock()

        self.actor.run({'args': {'token': 'qq', 'user_data': {}}})

        self.actor.call_sns_api.assert_called_with('app-arn', 'qq', '{}')
        self.actor.get_endpoint_arn_from_error_message.assert_called_with(err)
        self.actor.save_endpoint_arn.assert_called_with(
            'app-arn',
            'qq',
            '{}',
            'arn'
        )

    def test_when_everything_is_ok(self):

        api_response = MagicMock()
        self.actor.iter_application_arns = MagicMock(return_value=['app-arn'])
        self.actor.call_sns_api = MagicMock(return_value=api_response)
        self.actor.get_endpoint_arn_from_response = \
            MagicMock(return_value='arn')
        self.actor.save_endpoint_arn = MagicMock()

        self.actor.run({'args': {'token': 'qq', 'user_data': {}}})

        self.actor.call_sns_api.assert_called_with('app-arn', 'qq', '{}')
        self.actor.get_endpoint_arn_from_response.assert_called_with(
            api_response
        )
        self.actor.save_endpoint_arn.assert_called_with(
            'app-arn',
            'qq',
            '{}',
            'arn'
        )
