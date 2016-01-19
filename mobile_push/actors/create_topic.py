#!/usr/bin/env python

# standard library imports

# third party related imports
from boto.exception import BotoServerError
from sqlalchemy.exc import IntegrityError

# local library imports
from mobile_push.actors.base import BaseActor
from mobile_push.db import Session, Topic
from mobile_push.logger import logger


class CreateTopicActor(BaseActor):

    def run(self, message):

        if message.get('args', {}).get('name') is None:
            logger.warn('`name` is not present')
            return

        topic_name = message['args']['name']

        try:
            resp = self.connect_sns().create_topic(topic_name)
            logger.info('Create topic(%s) to SNS', topic_name)
        except BotoServerError as e:
            logger.error(e)
            logger.exception(e)
            return

        self._save_topic_arn(topic_name, resp)

    def _save_topic_arn(self, topic_name, api_response):

        obj = api_response.get('CreateTopicResponse', {})
        obj = obj.get('CreateTopicResult', {})
        arn = obj.get('TopicArn')

        if arn is None:
            logger.error('Cannot obtain topic arn: %s', topic_name)
            return

        try:
            session = Session()
            session.add(Topic(name=topic_name, arn=arn))
            session.commit()
            logger.info('Save topic(%s) into database', topic_name)

        except IntegrityError as e:
            logger.warn(e)
            session.rollback()


if __name__ == '__main__':

    message = {'args': {'name': 'qq'}}
    actor = CreateTopicActor()
    actor.run(message)
