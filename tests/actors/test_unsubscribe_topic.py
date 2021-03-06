#!/usr/bin/env python

# standard library imports

# third party related imports
from mock import MagicMock

# local library imports
from mobile_push.actors.unsubscribe_topic import UnsubscribeTopicActor
from mobile_push.db import Session, Subscription
from ..base import BaseTestCase
from ..factories.subscription import SubscriptionFactory


class TestFindSubscriptions(BaseTestCase):

    def setUp(self):

        self.actor = UnsubscribeTopicActor()

    def test(self):

        s = Subscription(topic_arn='t', endpoint_arn='e', subscription_arn='s')
        session = Session()
        session.add(s)
        session.commit()

        subscriptions = self.actor.find_subscriptions(
            topic_arn='t',
            endpoint_arns=['e']
        )
        self.assertEqual(subscriptions, [s])


class TestCallSnsApi(BaseTestCase):

    def setUp(self):

        self.actor = UnsubscribeTopicActor()
        self.sns_conn = MagicMock()
        self.actor.connect_sns = MagicMock(return_value=self.sns_conn)

    def test(self):

        self.actor.call_sns_api('subscription-arn')
        self.sns_conn.unsubscribe.assert_called_with('subscription-arn')


class TestRun(BaseTestCase):

    def setUp(self):

        self.actor = UnsubscribeTopicActor()
        self.actor.find_token_endpoint_arns = MagicMock()
        self.actor.find_topic_arn = MagicMock()
        self.actor.find_subscriptions = MagicMock()
        self.actor.call_sns_api = MagicMock()

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
        s = SubscriptionFactory()

        # If this line is not present, run() method will raise exception
        # saying it cannot delete the subscription instance due to it is
        # not persisted.
        # TODO figure out why
        self.assertIsNotNone(Session().query(Subscription).first())

        self.actor.find_token_endpoint_arns.return_value = ['endpoint-arn']
        self.actor.find_topic_arn.return_value = 'topic-arn'
        self.actor.find_subscriptions.return_value = [s]

        self.actor.run(message)

        self.actor.call_sns_api.assert_called_with(s.subscription_arn)
        self.assertIsNone(Session().query(Subscription).first())
