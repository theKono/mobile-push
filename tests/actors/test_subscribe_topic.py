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
        session.add(ApnsToken(
            token='qq',
            application_arn='app-arn',
            endpoint_arn='arn'
        ))
        session.commit()

        self.assertEqual(self.actor.find_token_endpoint_arns('qq'), ['arn'])

    def test_when_there_exists_a_gcm_token(self):

        session = Session()
        session.add(GcmToken(
            token='qq',
            application_arn='app-arn',
            endpoint_arn='arn'
        ))
        session.commit()

        self.assertEqual(self.actor.find_token_endpoint_arns('qq'), ['arn'])

    def test_when_there_is_no_such_token(self):

        self.assertEqual(self.actor.find_token_endpoint_arns('gg'), [])


class TestFindTopicArn(BaseTestCase):

    def setUp(self):

        self.actor = SubscribeTopicActor()

    def test_when_ther_exists_a_topic(self):

        session = Session()
        session.add(Topic(name='qq', arn='arn'))
        session.commit()

        self.assertEqual(self.actor.find_topic_arn('qq'), 'arn')

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


class TestRun(BaseTestCase):

    def setUp(self):

        self.actor = SubscribeTopicActor()
        self.actor.find_token_endpoint_arns = MagicMock()
        self.actor.find_topic_arn = MagicMock()
        self.actor.call_sns_api = MagicMock()
        self.actor.get_arn_from_response = MagicMock()
        self.actor.save_subscription = MagicMock()

    def test_when_token_is_not_present(self):

        message = {'args': {}}

        self.actor.run(message)
        self.assertFalse(self.actor.call_sns_api.called)

    def test_when_token_endpoint_arn_is_not_found(self):

        message = {'args': {'token': 'qq'}}

        self.actor.find_token_endpoint_arns.return_value = []
        self.actor.run(message)
        self.assertFalse(self.actor.call_sns_api.called)

    def test_when_topic_is_not_present(self):

        message = {'args': {'token': 'qq'}}

        self.actor.find_token_endpoint_arns.return_value = [True]
        self.actor.run(message)
        self.assertFalse(self.actor.call_sns_api.called)

    def test_when_topic_is_not_found(self):

        message = {'args': {'token': 'qq', 'topic': 'gg'}}

        self.actor.find_token_endpoint_arns.return_value = [True]
        self.actor.find_topic_arn.return_value = None
        self.actor.run(message)
        self.assertFalse(self.actor.call_sns_api.called)

    def test_when_everything_is_ok(self):

        message = {'args': {'token': 'qq', 'topic': 'gg'}}

        self.actor.find_token_endpoint_arns.return_value = ['endpoint-arn']
        self.actor.find_topic_arn.return_value = 'topic-arn'
        self.actor.call_sns_api.return_value = resp = MagicMock()
        self.actor.get_arn_from_response.return_value = 'subscription-arn'

        self.actor.run(message)

        self.actor.call_sns_api.assert_called_with('topic-arn', 'endpoint-arn')
        self.actor.get_arn_from_response.assert_called_with(resp)
        self.actor.save_subscription.assert_called_with(
            'topic-arn',
            'endpoint-arn',
            'subscription-arn'
        )
