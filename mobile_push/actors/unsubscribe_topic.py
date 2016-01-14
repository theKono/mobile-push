#!/usr/bin/env python

# standard library imports

# third party related imports

# local library imports
from mobile_push.actors.base_sns import BaseSnsActor
from mobile_push.logger import logger
from mobile_push.db import Session, Subscription


class UnsubscribeTopicActor(BaseSnsActor):

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

    def find_subscriptions(self, topic_arn, endpoint_arns):

        session = Session()
        query = session.query(Subscription).filter_by(topic_arn=topic_arn)
        query = query.filter(Subscription.endpoint_arn.in_(endpoint_arns))
        return query.all()

    def call_sns_api(self, subscription_arn):

        self.connect_sns().unsubscribe(subscription_arn)


if __name__ == '__main__':

    UnsubscribeTopicActor().run({'args': {'topic': 'qq', 'token': 'gg'}})
