#!/usr/bin/env python

# standard library imports

# third party related imports
import factory

# local library imports
from mobile_push.db import Session, Topic


class TopicFactory(factory.alchemy.SQLAlchemyModelFactory):

    class Meta(object):
        model = Topic
        sqlalchemy_session = Session

    name = factory.Sequence(lambda n: 'topic-%s' % n)
    arn = factory.Sequence(lambda n: 'topic-arn-%s' % n)

