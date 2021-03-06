#!/usr/bin/env python
"""MessageRouter is responsible to create the actor to handle event."""

# standard library imports

# third party related imports

# local library imports
from mobile_push.actors.create_apns_token import CreateApnsTokenActor
from mobile_push.actors.create_gcm_token import CreateGcmTokenActor
from mobile_push.actors.create_topic import CreateTopicActor
from mobile_push.actors.direct_publish import DirectPublishActor
from mobile_push.actors.publish_to_topic import PublishToTopicActor
from mobile_push.actors.subscribe_topic import SubscribeTopicActor
from mobile_push.actors.unsubscribe_topic import UnsubscribeTopicActor


class MessageRouter(object):

    class BaseError(Exception):
        """Base exception class."""

    class ActionError(BaseError):
        """Raises when it is an unrecognizable action."""

    TABLE = {
        'create_topic': CreateTopicActor,
        'create_apns_token': CreateApnsTokenActor,
        'create_gcm_token': CreateGcmTokenActor,
        'subscribe_topic': SubscribeTopicActor,
        'unsubscribe_topic': UnsubscribeTopicActor,
        'publish_to_topic': PublishToTopicActor,
        'direct_publish': DirectPublishActor,
    }

    def __init__(self, message):

        self.message = message

    def get_actor(self):

        action = self.message.get('action')
        factory_cls = self.TABLE.get(action)

        if factory_cls is None:
            raise self.ActionError('Unknown action: %(action)s' % locals())

        return factory_cls()
