#!/usr/bin/env python

# standard library imports

# third party related imports
from sqlalchemy import engine_from_config
from sqlalchemy.orm import scoped_session, sessionmaker

# local library imports
from mobile_push.config import setting
from mobile_push.models.base import Base

# We should import all model before we can create all tables
from mobile_push.models.topic import Topic


engine = engine_from_config(dict(setting.items('db')))
Base.metadata.create_all(engine)
Session = scoped_session(sessionmaker(bind=engine))
