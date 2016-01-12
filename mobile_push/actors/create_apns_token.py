#!/usr/bin/env python

# standard library imports
import re

# third party related imports
from boto.exception import BotoServerError
from boto.sns import connect_to_region
from sqlalchemy.exc import IntegrityError
import ujson

# local library imports
from mobile_push.actors.base import BaseActor
from mobile_push.config import setting
from mobile_push.logger import logger
from mobile_push.db import ApnsToken, Session


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
        str_user_data = ujson.dumps(user_data)

        if token is None:
            logger.warn('`token` is not present')
            return

        for app_arn in self.iter_application_arns():
            try:
                result = self.call_sns_api(app_arn, token, str_user_data)
                endpoint_arn = self.get_endpoint_arn_from_response(result)

            except BotoServerError as e:
                endpoint_arn = self.get_endpoint_arn_from_error_message(e)

            if endpoint_arn is None:
                logger.error('Cannot get endpoint arn of %s', token)
                logger.exception(e)
                return

            self.save_endpoint_arn(
                app_arn,
                token,
                str_user_data,
                endpoint_arn
            )

    def call_sns_api(self, app_arn, token, user_data):

        result = self.sns_conn.create_platform_endpoint(
            platform_application_arn=app_arn,
            token=token,
            custom_user_data=user_data
        )
        logger.info(
            ('create_platform_endpoint(platform_application_arn=%s, '
             'token=%s, custom_user_data=%s)'),
            app_arn,
            token,
            user_data
        )

        return result

    def get_endpoint_arn_from_response(self, api_response):

        obj = api_response.get('CreatePlatformEndpointResponse', {})
        obj = obj.get('CreatePlatformEndpointResult', {})
        return obj.get('EndpointArn')

    def get_endpoint_arn_from_error_message(self, err):

        pattern = re.compile(r'Endpoint(.*)already', re.IGNORECASE)
        result = pattern.search(err.message)

        if result is None:
            return None

        return result.group(0).replace('Endpoint ', '').replace(' already', '')

    def save_endpoint_arn(self, app_arn, token, user_data, endpoint_arn):

        try:
            session = Session()
            session.add(ApnsToken(
                token=token,
                application_arn=app_arn,
                endpoint_arn=endpoint_arn,
                user_data=user_data
            ))
            session.commit()

            logger.info(
                ('Save ApnsToken(token=%s, application_arn=%s, '
                 'endpoint_arn=%s, user_data=%s)'),
                token,
                app_arn,
                endpoint_arn,
                user_data
            )

        except IntegrityError as e:
            logger.warn(e)
            session.rollback()


if __name__ == '__main__':

    CreateApnsTokenActor().run({
        'args': {
            'token': '0' * 64,
            'user_data': {'user_id': 1}
        }
    })
