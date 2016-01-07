#!/usr/bin/env python

# standard library imports

# third party related imports
import factory

# local library imports
from mobile_push.db import GcmToken, Session


class GcmTokenFactory(factory.alchemy.SQLAlchemyModelFactory):

    class Meta(object):
        model = GcmToken
        sqlalchemy_session = Session

    token = factory.Sequence(lambda n: 'token-%s' % n)
    application_arn = factory.Sequence(lambda n: 'app-arn-%s' % n)
    endpoint_arn = factory.Sequence(lambda n: 'endpoint-arn-%s' % n)
