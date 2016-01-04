#!/usr/bin/env python

# standard library imports

# third party related imports
from boto.sns import connect_to_region

# local library imports
from mobile_push.actors.create_apns_token import CreateApnsTokenActor
from mobile_push.config import setting


class CreateGcmTokenActor(CreateApnsTokenActor):

    def __init__(self):

        super(CreateGcmTokenActor, self).__init__()
        self.sns_conn = connect_to_region(setting.get('sns', 'region'))

    def iter_application_arns(self):

        return (arn for _, arn in setting.items('sns:gcm-applications'))


if __name__ == '__main__':

    message = {
        'args': {
            'token': 'qq',
            'user_data': {'user_id': 1}
        }
    }
    actor = CreateGcmTokenActor()
    actor.run(message)
