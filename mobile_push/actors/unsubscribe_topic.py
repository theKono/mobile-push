#!/usr/bin/env python

# standard library imports

# third party related imports
from boto.sns import connect_to_region

# local library imports
from mobile_push.actors.base import BaseActor
from mobile_push.config import setting
from mobile_push.logger import logger
from mobile_push.db import ApnsToken, GcmToken, Session, Subscription, Topic


class UnsubscribeTopicActor(BaseActor):

    def __init__(self):

        super(UnsubscribeTopicActor, self).__init__()
        self.sns_conn = connect_to_region(setting.get('sns', 'region'))

    def run(self, message):

        args = message.get('args', {})
        token = args.get('token')
        if token is None:
            logger.warn('`token` is not present')
            return

        endpoint_arns = self.find_token_endpoint_arns(token)
        if len(endpoint_arns) == 0:
            logger.warn('Unknown token %s', token)
            return

        topic = args.get('topic')
        if topic is None:
            logger.warn('`topic` is not present')
            return

        topic_arn = self.find_topic_arn(topic)
        if topic_arn is None:
            logger.warn('Unknown topic %s', topic)
            return

        session = Session()

        for s in self.find_subscriptions(topic_arn, endpoint_arns):
            self.call_sns_api(s.subscription_arn)
            session.delete(s)

        session.commit()

    def find_token_endpoint_arns(self, token):

        session = Session()
        rows = session.query(ApnsToken).filter_by(token=token).all()

        if len(rows) == 0:
            rows = session.query(GcmToken).filter_by(token=token).all()

        return [r.endpoint_arn for r in rows]

    def find_topic_arn(self, topic):

        session = Session()
        row = session.query(Topic).get(topic)
        return getattr(row, 'arn', None)

    def find_subscriptions(self, topic_arn, endpoint_arns):

        session = Session()
        query = session.query(Subscription).filter_by(topic_arn=topic_arn)
        query = query.filter(Subscription.endpoint_arn.in_(endpoint_arns))
        return query.all()

    def call_sns_api(self, subscription_arn):

        self.sns_conn.unsubscribe(subscription_arn)


if __name__ == '__main__':

    UnsubscribeTopicActor().run({'args': {'topic': 'qq', 'token': 'gg'}})
