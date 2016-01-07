#!/usr/bin/env python

# standard library imports

# third party related imports

# local library imports
from mobile_push.actors.base_sns import BaseSnsActor
from ..base import BaseTestCase
from ..factories.apns_token import ApnsTokenFactory
from ..factories.gcm_token import GcmTokenFactory
from ..factories.topic import TopicFactory


class TestFindTokenEndpointArns(BaseTestCase):

    def setUp(self):

        self.actor = BaseSnsActor()

    def test_when_there_exists_an_apns_token(self):

        ApnsTokenFactory.create(token='qq', endpoint_arn='arn')
        self.assertEqual(self.actor.find_token_endpoint_arns('qq'), ['arn'])

    def test_when_there_exists_a_gcm_token(self):

        GcmTokenFactory.create(token='qq', endpoint_arn='arn')
        self.assertEqual(self.actor.find_token_endpoint_arns('qq'), ['arn'])

    def test_when_there_is_no_such_token(self):

        self.assertEqual(self.actor.find_token_endpoint_arns('gg'), [])


class TestFindTopicArn(BaseTestCase):

    def setUp(self):

        self.actor = BaseSnsActor()

    def test_when_ther_exists_a_topic(self):

        TopicFactory.create(name='qq', arn='arn')
        self.assertEqual(self.actor.find_topic_arn('qq'), 'arn')

    def test_when_there_is_no_such_topic(self):

        self.assertIsNone(self.actor.find_topic_arn('qq'))
