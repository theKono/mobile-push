#!/usr/bin/env python

# standard library imports
from __future__ import print_function
import json
import sys

# third party related imports
import boto.sns

# local library imports
from mobile_push.config import setting
from mobile_push.db import ApnsToken, GcmToken, Session


def main(argv):

    if len(argv) != 2:
        print('usage: python %s <token>' % argv[0], file=sys.stderr)
        exit(1)

    token = argv[1]
    session = Session()
    apns_tokens = session.query(ApnsToken).filter_by(token=token).all()
    gcm_tokens = session.query(GcmToken).filter_by(token=token).all()
    sns_conn = boto.sns.connect_to_region(setting.get('sns', 'region'))
    items = 0

    for token in apns_tokens + gcm_tokens:
        result = sns_conn.get_endpoint_attributes(token.endpoint_arn)
        result = result['GetEndpointAttributesResponse']
        result = result['GetEndpointAttributesResult']['Attributes']
        result['Application'] = token.application_arn
        print(json.dumps(result, indent=4))
        items += 1

    print('-' * 80)
    print('%s result(s)' % items)


if __name__ == '__main__':

    main(sys.argv)
