#!/usr/bin/env python

# standard library imports

# third party related imports
from boto.exception import BotoServerError
from boto.sns import connect_to_region

# local library imports
from mobile_push.actors.base import BaseActor
from mobile_push.config import setting
from mobile_push.logger import logger
from mobile_push.db import Session, Topic


class PublishToTopicActor(BaseActor):

    def __init__(self):

        super(PublishToTopicActor, self).__init__()
        self.sns_conn = connect_to_region(setting.get('sns', 'region'))

    def run(self, message):

        args = message.get('args', {})

        topic = args.get('topic')
        if topic is None:
            logger.warn('`topic` is not present')
            return

        topic_arn = self.find_topic_arn(topic)
        if topic_arn is None:
            logger.warn('Unknown topic %s', topic)
            return

        try:
            self.call_sns_api(topic_arn, args.get('message'))
        except BotoServerError as e:
            logger.error(e)
            logger.exception(e)

    def find_topic_arn(self, topic):

        session = Session()
        row = session.query(Topic).get(topic)
        return getattr(row, 'arn', None)

    def call_sns_api(self, topic_arn, message):

        self.sns_conn.publish(
            topic=topic_arn,
            message=message,
            message_structure='json',
        )
        logger.info(
            'publish(topic=%s, message=%s, message_structure=json)',
            topic_arn,
            message
        )

