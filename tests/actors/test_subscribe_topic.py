#!/usr/bin/env python

# standard library imports

# third party related imports
from boto.exception import BotoServerError
from mock import MagicMock
import ujson

# local library imports
from mobile_push.actors.subscribe_topic import SubscribeTopicActor
from mobile_push.config import setting
from mobile_push.db import ApnsToken, GcmToken, Session, Subscription, Topic
from ..base import BaseTestCase


class TestFindTokenEndpointArns(BaseTestCase):

    def setUp(self):

        self.actor = SubscribeTopicActor()

    def test_when_there_exists_an_apns_token(self):

        session = Session()
        at = ApnsToken(
            token='qq',
            application_arn='app-arn',
            endpoint_arn='arn'
        )
        session.add(at)
        session.commit()

        self.assertEqual(self.actor.find_token_endpoint_arns('qq'), [at])

    def test_when_there_exists_a_gcm_token(self):

        session = Session()
        gt = GcmToken(
            token='qq',
            application_arn='app-arn',
            endpoint_arn='arn'
        )
        session.add(gt)
        session.commit()

        self.assertEqual(self.actor.find_token_endpoint_arns('qq'), [gt])

    def test_when_there_is_no_such_token(self):

        self.assertEqual(self.actor.find_token_endpoint_arns('gg'), [])


class TestFindTopicArn(BaseTestCase):

    def setUp(self):

        self.actor = SubscribeTopicActor()

    def test_when_ther_exists_a_topic(self):

        session = Session()
        t = Topic(name='qq', arn='arn')
        session.add(t)
        session.commit()

        self.assertEqual(self.actor.find_topic_arn('qq'), t)

    def test_when_there_is_no_such_topic(self):

        self.assertIsNone(self.actor.find_topic_arn('qq'))


class TestCallSnsApi(BaseTestCase):

    def setUp(self):

        self.actor = SubscribeTopicActor()
        self.actor.sns_conn = MagicMock()

    def test(self):

        self.actor.call_sns_api('topic-arn', 'endpoint-arn')
        self.actor.sns_conn.subscribe.assert_called_with(
            'topic-arn',
            'application',
            'endpoint-arn'
        )


class TestGetArnFromResponse(BaseTestCase):

    def setUp(self):

        self.actor = SubscribeTopicActor()

    def test(self):

        resp = {
            'SubscribeResponse': {
                'ResponseMetadata': {'RequestId': 'xxx'},
                'SubscribeResult': {'SubscriptionArn': 'arn'}
            }
        }
        self.assertEqual(self.actor.get_arn_from_response(resp), 'arn')


class TestSaveSubscription(BaseTestCase):

    def setUp(self):

        self.actor = SubscribeTopicActor()

    def test(self):

        self.actor.save_subscription('t-arn', 'e-arn', 's-arn')

        s = Session().query(Subscription).first()
        self.assertEqual(s.topic_arn, 't-arn')
        self.assertEqual(s.endpoint_arn, 'e-arn')
        self.assertEqual(s.subscription_arn, 's-arn')
