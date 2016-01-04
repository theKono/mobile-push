#!/usr/bin/env python

# standard library imports

# third party related imports
from boto.exception import BotoServerError
from mock import MagicMock

# local library imports
from mobile_push.actors.create_topic import CreateTopicActor
from mobile_push.db import Session, Topic
from ..base import BaseTestCase


class TestRun(BaseTestCase):

    def setUp(self):

        self.actor = CreateTopicActor()
        self.actor.sns_conn = MagicMock()

    def test_when_name_is_not_present(self):

        self.actor.run({'args': {}})
        self.assertFalse(self.actor.sns_conn.create_topic.called)

    def test_when_sns_api_failed(self):

        self.actor.sns_conn.create_topic = MagicMock(
            side_effect=BotoServerError(403, ':)')
        )
        self.actor.run({'args': {'name': 'qq'}})

        session = Session()
        self.assertEqual(session.query(Topic).count(), 0)

    def test_when_everything_is_ok(self):

        self.actor.sns_conn.create_topic.return_value = {
            'CreateTopicResponse': {
                'CreateTopicResult': {'TopicArn': 'an-arn'},
                'ResponseMetadata': {'RequestId': 'xxx'}
            }
        }

        self.actor.run({'args': {'name': 'qq'}})

        session = Session()
        t = session.query(Topic).first()
        self.assertEqual(t.name, 'qq')
        self.assertEqual(t.arn, 'an-arn')
