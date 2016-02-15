#!/usr/bin/env python

# standard library imports
from __future__ import print_function
import argparse
import logging

# third party related imports
import boto.sns

# local library imports
from mobile_push.config import setting
from mobile_push.db import ApnsToken, Session


logging.basicConfig(level=logging.INFO)


def parse_args():

    parser = argparse.ArgumentParser(description='Set endpoint attributes')
    parser.add_argument(
        '--customer-data',
        help='Set arbitrary user data to associate with the endpoint',
        dest='customer_data'
    )
    parser.add_argument(
        '--enable',
        help='Flag that enables/disables delivery to the endpoint',
        dest='enable'
    )
    parser.add_argument(
        'apns-token',
        help='APNS token to set attributes'
    )

    args = vars(parser.parse_args())
    logging.info(args)
    return args


def main():

    args = parse_args()
    token = args['apns-token']
    attributes = {}

    if args.get('customer_data') is not None:
        attributes['CustomUserData'] = args['customer_data']

    if args.get('enable') is not None:
        attributes['Enabled'] = (args['enable'] == 'true')

    if len(attributes) == 0:
        logging.error('customer data or enable must be provided')
        exit(1)

    session = Session()
    apns_token = session.query(ApnsToken).filter_by(token=token).first()
    if apns_token is None:
        logging.error('Cannot find %s', token)
        exit(1)

    sns_conn = boto.sns.connect_to_region(setting.get('sns', 'region'))
    endpoint = apns_token.endpoint_arn
    result = sns_conn.set_endpoint_attributes(endpoint, attributes)
    logging.info(result)


if __name__ == '__main__':

    main()
