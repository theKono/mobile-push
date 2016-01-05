#!/usr/bin/env python

# standard library imports
import time

# third party related imports
from sqlalchemy import Column, Integer, String

# local library imports
from mobile_push.models.base import Base


class GcmToken(Base):

    __tablename__ = 'gcm_tokens'

    token = Column(String, primary_key=True)
    application_arn = Column(String, primary_key=True)
    endpoint_arn = Column(String, nullable=False)
    user_data = Column(String, nullable=False, default='')
    created_at = Column(Integer, default=lambda: int(time.time()))
