#!/usr/bin/env python

# standard library imports
from string import hexdigits
from random import choice

# third party related imports
import factory

# local library imports
from mobile_push.db import ApnsToken, Session


class ApnsTokenFactory(factory.alchemy.SQLAlchemyModelFactory):

    class Meta(object):
        model = ApnsToken
        sqlalchemy_session = Session

    token = factory.Sequence(
        lambda n: ''.join([choice(hexdigits) for _ in xrange(64)])
    )
    application_arn = factory.Sequence(lambda n: 'app-arn-%s' % n)
    endpoint_arn = factory.Sequence(lambda n: 'endpoint-arn-%s' % n)
