#!/usr/bin/env python

# standard library imports

# third party related imports
from mock import MagicMock

# local library imports
from mobile_push.actors.publish_to_topic import PublishToTopicActor
from ..base import BaseTestCase


class TestCallSnsApi(BaseTestCase):

    def setUp(self):

        self.actor = PublishToTopicActor()
        self.actor.sns_conn = MagicMock()

    def test(self):

        self.actor.call_sns_api('topic-arn', 'message')
        self.actor.sns_conn.publish.assert_called_with(
            topic='topic-arn',
            message='message',
            message_structure='json'
        )


class TestRun(BaseTestCase):

    def setUp(self):

        self.actor = PublishToTopicActor()
        self.actor.call_sns_api = MagicMock()

    def test_when_topic_is_not_present(self):

        self.actor.run({'args': {}})
        self.assertFalse(self.actor.call_sns_api.called)

    def test_when_topic_is_not_found(self):

        self.actor.run({'args': {'topic': 'not-exist'}})
        self.assertFalse(self.actor.call_sns_api.called)

    def test_when_everything_is_ok(self):

        self.actor.find_topic_arn = MagicMock(return_value='topic-arn')
        self.actor.run({'args': {'topic': 't', 'message': 'so'}})
        self.actor.call_sns_api.assert_called_with('topic-arn', 'so')
