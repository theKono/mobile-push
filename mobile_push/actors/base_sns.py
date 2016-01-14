#!/usr/bin/env python

# standard library imports

# third party related imports

# local library imports
from mobile_push.actors.base import BaseActor
from mobile_push.db import ApnsToken, GcmToken, Session, Topic


class BaseSnsActor(BaseActor):

    def find_token_endpoint_arns(self, token):

        session = Session()
        rows = session.query(ApnsToken).filter_by(token=token).all()
        if len(rows) == 0:
            rows = session.query(GcmToken).filter_by(token=token).all()

        return [row.endpoint_arn for row in rows]

    def find_topic_arn(self, topic):

        session = Session()
        row = session.query(Topic).get(topic)
        return getattr(row, 'arn', None)
