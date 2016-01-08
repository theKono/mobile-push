#!/usr/bin/env python

# standard library imports
import time

# third party related imports
from sqlalchemy import Column, Integer, String

# local library imports
from mobile_push.models.base import Base


class Topic(Base):

    __tablename__ = 'topics'

    name = Column(String, primary_key=True)
    arn = Column(String, nullable=False)
    created_at = Column(Integer, default=lambda: int(time.time()))
