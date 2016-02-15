#!/usr/bin/env python
# pylint: disable=missing-docstring

# standard library imports

# third party related imports
from boto.exception import BotoServerError

# local library imports
from mobile_push.actors.base_sns import BaseSnsActor
from mobile_push.logger import logger


class PublishToTopicActor(BaseSnsActor):

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
        except BotoServerError as err:
            logger.error(err)
            logger.exception(err)

    def call_sns_api(self, topic_arn, message):

        self.connect_sns().publish(
            topic=topic_arn,
            message=message,
            message_structure='json',
        )
        logger.info(
            'publish(topic=%s, message=%s, message_structure=json)',
            topic_arn,
            message
        )
