#!/usr/bin/env python

# standard library imports

# third party related imports
from mock import MagicMock

# local library imports
from mobile_push.actors.subscribe_topic import SubscribeTopicActor
from mobile_push.db import Session, Subscription
from ..base import BaseTestCase
from ..factories.subscription import SubscriptionFactory


class TestCallSnsApi(BaseTestCase):

    def setUp(self):

        self.actor = SubscribeTopicActor()
        self.sns_conn = MagicMock()
        self.actor.connect_sns = MagicMock(return_value=self.sns_conn)

    def test(self):

        self.actor.call_sns_api('topic-arn', 'endpoint-arn')
        self.sns_conn.subscribe.assert_called_with(
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


class TestHasSubscription(BaseTestCase):

    def setUp(self):

        self.actor = SubscribeTopicActor()

    def test_when_subscription_exists(self):

        SubscriptionFactory.create(topic_arn='ttt', endpoint_arn='eee')
        self.assertTrue(self.actor.has_subscription('ttt', 'eee'))

    def test_when_subscription_does_not_exist(self):

        self.assertFalse(self.actor.has_subscription('ttt', 'eee'))


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

    def test_when_subscription_exists(self):

        message = {'args': {'token': 'qq', 'topic': 'gg'}}

        self.actor.find_token_endpoint_arns.return_value = ['eee']
        self.actor.find_topic_arn.return_value = 'ttt'
        self.actor.has_subscription = MagicMock(return_value=True)
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
