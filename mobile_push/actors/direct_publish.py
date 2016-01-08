#!/usr/bin/env python

# standard library imports

# third party related imports
from boto.exception import BotoServerError
import eventlet

# local library imports
from mobile_push.logger import logger

# greening aws sns
green_module = eventlet.import_patched('mobile_push.actors.base_sns')
BaseSnsActor = green_module.BaseSnsActor


class DirectPublishActor(BaseSnsActor):

    def run(self, message):

        args = message.get('args', {})
        tokens = args.get('tokens', [])
        token_arns = set()

        for token in tokens:
            target_arns = self.find_token_endpoint_arns(token)
            map(token_arns.add, target_arns)

        pool = eventlet.GreenPool(20)

        for token_arn in token_arns:
            pool.spawn_n(self.call_sns_api, token_arn, args.get('message'))

        pool.waitall()

    def call_sns_api(self, target_arn, message):

        try:
            self.sns_conn.publish(
                message=message,
                message_structure='json',
                target_arn=target_arn
            )
            logger.info(
                'publish(message=%s, message_structure=json, target_arn=%s)',
                message,
                target_arn
            )
        except BotoServerError as e:
            logger.error(e)
            logger.exception(e)
