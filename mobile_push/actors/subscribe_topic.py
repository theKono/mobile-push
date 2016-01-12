#!/usr/bin/env python

# standard library imports

# third party related imports
from sqlalchemy.exc import IntegrityError

# local library imports
from mobile_push.actors.base_sns import BaseSnsActor
from mobile_push.logger import logger
from mobile_push.db import Session, Subscription


class SubscribeTopicActor(BaseSnsActor):

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

        for endpoint_arn in endpoint_arns:
            api_response = self.call_sns_api(topic_arn, endpoint_arn)
            subscription_arn = self.get_arn_from_response(api_response)
            self.save_subscription(topic_arn, endpoint_arn, subscription_arn)

    def call_sns_api(self, topic_arn, endpoint_arn):

        ret = self.sns_conn.subscribe(topic_arn, 'application', endpoint_arn)
        logger.info('subscribe(%s, application, %s)', topic_arn, endpoint_arn)
        return ret

    def get_arn_from_response(self, api_response):

        obj = api_response.get('SubscribeResponse', {})
        obj = obj.get('SubscribeResult', {})
        return obj.get('SubscriptionArn')

    def save_subscription(self, topic_arn, endpoint_arn, subscription_arn):

        try:
            session = Session()
            session.add(Subscription(
                topic_arn=topic_arn,
                endpoint_arn=endpoint_arn,
                subscription_arn=subscription_arn
            ))
            session.commit()

            logger.info(
                ('Save Subscription(topic_arn=%s, '
                 'endpoint_arn=%s, subscription_arn=%s)'),
                topic_arn,
                endpoint_arn,
                subscription_arn
            )

        except IntegrityError as err:
            logger.warn(err)
            session.rollback()
