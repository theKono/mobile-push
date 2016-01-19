#!/usr/bin/env python

# standard library imports

# third party related imports

# local library imports
from mobile_push.actors.create_gcm_token import CreateGcmTokenActor
from mobile_push.config import setting
from mobile_push.db import GcmToken, Session
from ..base import BaseTestCase
from ..factories.gcm_token import GcmTokenFactory


class TestIterApplicationArns(BaseTestCase):

    def setUp(self):

        self.actor = CreateGcmTokenActor()

    def test(self):

        self.assertEqual(
            list(self.actor.iter_application_arns()),
            [pair[1] for pair in setting.items('sns:gcm-applications')]
        )


class TestSaveEndpointArn(BaseTestCase):

    def setUp(self):

        self.actor = CreateGcmTokenActor()

    def test(self):

        self.actor.save_endpoint_arn('app-arn', 'token', 'qq', 'endpoint_arn')

        session = Session()
        gcm_token = session.query(GcmToken).first()

        self.assertEqual(gcm_token.token, 'token')
        self.assertEqual(gcm_token.application_arn, 'app-arn')
        self.assertEqual(gcm_token.endpoint_arn, 'endpoint_arn')
        self.assertEqual(gcm_token.user_data, 'qq')


class TestHasPlatformEndpoint(BaseTestCase):

    def setUp(self):

        self.actor = CreateGcmTokenActor()

    def test_when_gcm_token_exist(self):

        GcmTokenFactory.create(token='ttt', application_arn='aaa')
        self.assertTrue(self.actor.has_platform_endpoint('ttt', 'aaa'))

    def test_when_gcm_token_does_not_exist(self):

        self.assertFalse(self.actor.has_platform_endpoint('ttt', 'aaa'))
