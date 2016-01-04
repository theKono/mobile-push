#!/usr/bin/env python

# standard library imports

# third party related imports
from boto.exception import BotoServerError
from boto.sns import connect_to_region
import ujson

# local library imports
from mobile_push.actors.base import BaseActor
from mobile_push.config import setting
from mobile_push.logger import logger


class CreateApnsTokenActor(BaseActor):

    def __init__(self):

        super(CreateApnsTokenActor, self).__init__()
        self.sns_conn = connect_to_region(setting.get('sns', 'region'))

    def iter_application_arns(self):

        return (arn for _, arn in setting.items('sns:apns-applications'))

    def run(self, message):

        args = message.get('args', {})
        token = args.get('token')
        user_data = args.get('user_data', {})

        if token is None:
            logger.warn('`token` is not present')
            return

        for arn in self.iter_application_arns():
            try:
                self.sns_conn.create_platform_endpoint(
                    platform_application_arn=arn,
                    token=token,
                    custom_user_data=ujson.dumps(user_data)
                )
                logger.info(
                    ('create_platform_endpoint(platform_application_arn=%s, '
                     'token=%s, custom_user_data=%s)'),
                    arn,
                    token,
                    ujson.dumps(user_data),
                )

            except BotoServerError as e:
                logger.error(e)
                logger.exception(e)


if __name__ == '__main__':

    message = {
        'args': {
            'token': '0' * 64,
            'user_data': {'user_id': 1}
        }
    }
    actor = CreateApnsTokenActor()
    actor.run(message)
