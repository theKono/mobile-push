#!/usr/bin/env python

# standard library imports

# third party related imports
import factory

# local library imports
from mobile_push.db import Session, Subscription


class SubscriptionFactory(factory.alchemy.SQLAlchemyModelFactory):

    class Meta(object):
        model = Subscription
        sqlalchemy_session = Session

    endpoint_arn = factory.Sequence(lambda n: 'endpoint-arn-%s' % n)
    topic_arn = factory.Sequence(lambda n: 'topic-arn-%s' % n)
    subscription_arn = factory.Sequence(lambda n: 'subscription-arn-%s' % n)
