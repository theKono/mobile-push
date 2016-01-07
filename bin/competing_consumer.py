#!/usr/bin/env python

# standard library imports
import signal

# third party related imports
import boto.sqs
import ujson

# local library imports
from mobile_push.config import setting
from mobile_push.logger import logger
from mobile_push.message_router import MessageRouter


keep_running = True


def sigterm_handler(signum, _):

    global keep_running

    logger.warn('Receive SIGTERM')
    keep_running = False


def get_queue():

    conn = boto.sqs.connect_to_region(setting.get('sqs', 'region'))
    return conn.get_queue(setting.get('sqs', 'queue'))


def poll_message(queue):

    message = queue.read(wait_time_seconds=20)

    if message is None:
        return

    try:
        body = message.get_body()
        units = ujson.loads(body)
    except ValueError:
        logger.error('Cannot parse: %s', body)
        units = []

    if not isinstance(units, list):
        units = [units]

    for unit in units:
        try:
            MessageRouter(unit).get_actor().run(unit)
        except MessageRouter.BaseError:
            logger.error('Cannot route message: %s', ujson.dumps(unit))
        except Exception as e:
            logger.exception(e)

    queue.delete_message(message)


def main():

    signal.signal(signal.SIGTERM, sigterm_handler)
    q = get_queue()

    while keep_running:
        poll_message(q)


if __name__ == '__main__':

    main()
