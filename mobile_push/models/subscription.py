#!/usr/bin/env python

# standard library imports
import time

# third party related imports
from sqlalchemy import Column, Integer, String

# local library imports
from mobile_push.models.base import Base


class Subscription(Base):

    __tablename__ = 'subscriptions'

    endpoint_arn = Column(String, primary_key=True)
    topic_arn = Column(String, primary_key=True)
    subscription_arn = Column(String, nullable=False)
    created_at = Column(Integer, default=lambda: int(time.time()))
