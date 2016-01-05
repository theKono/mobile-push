#!/usr/bin/env python

# standard library imports

# third party related imports
from boto.sns import connect_to_region
from sqlalchemy.exc import IntegrityError

# local library imports
from mobile_push.actors.create_apns_token import CreateApnsTokenActor
from mobile_push.config import setting
from mobile_push.logger import logger
from mobile_push.db import GcmToken, Session


class CreateGcmTokenActor(CreateApnsTokenActor):

    def __init__(self):

        super(CreateGcmTokenActor, self).__init__()
        self.sns_conn = connect_to_region(setting.get('sns', 'region'))

    def iter_application_arns(self):

        return (arn for _, arn in setting.items('sns:gcm-applications'))

    def save_endpoint_arn(self, app_arn, token, user_data, endpoint_arn):

        try:
            session = Session()
            session.add(GcmToken(
                token=token,
                application_arn=app_arn,
                endpoint_arn=endpoint_arn,
                user_data=user_data
            ))
            session.commit()

            logger.info(
                ('Save GcmToken(token=%s, application_arn=%s, '
                 'endpoint_arn=%s, user_data=%s)'),
                token,
                app_arn,
                endpoint_arn,
                user_data
            )

        except IntegrityError as e:
            logger.warn(e)


if __name__ == '__main__':

    message = {
        'args': {
            'token': 'qq',
            'user_data': {'user_id': 1}
        }
    }
    actor = CreateGcmTokenActor()
    actor.run(message)
