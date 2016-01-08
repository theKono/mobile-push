#!/usr/bin/env python

# standard library imports
import logging
from logging.handlers import TimedRotatingFileHandler

# third party related imports

# local library imports
from mobile_push.config import setting


__all__ = ['logger']
logging_level = getattr(logging, setting.get('logger', 'level'))

handler = TimedRotatingFileHandler(
    filename=setting.get('logger', 'filename'),
    when='midnight',
    backupCount=30
)
handler.setLevel(logging_level)
handler.setFormatter(logging.Formatter(setting.get('logger', 'format')))

logger = logging.getLogger('mobile_push')
logger.setLevel(logging_level)
logger.addHandler(handler)
