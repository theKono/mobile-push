#!/usr/bin/env python

# standard library imports

# third party related imports
from mock import MagicMock

# local library imports
from mobile_push.actors.publish_to_topic import PublishToTopicActor
from ..base import BaseTestCase
from ..factories.topic import TopicFactory


class TestFindTopicArn(BaseTestCase):

    def setUp(self):

        self.actor = PublishToTopicActor()

    def test_when_ther_exists_a_topic(self):

        TopicFactory.create(name='qq', arn='arn')
        self.assertEqual(self.actor.find_topic_arn('qq'), 'arn')

    def test_when_there_is_no_such_topic(self):

        self.assertIsNone(self.actor.find_topic_arn('qq'))


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

    def test_when_topic_is_not_present(self):

        self.actor
