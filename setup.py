#!/usr/bin/env python

# standard library imports
from os.path import exists

# third party related imports
from setuptools import setup, find_packages

# local library imports
from mobile_push import __version__


def read_from_file(filename):

    if exists(filename):
        with open(filename) as f:
            return f.read()

    return ''


setup(
    name='mobile-push',
    version=__version__,
    # Your name & email here
    author='Yu Liang',
    author_email='yu.liang@thekono.com',
    # If you had mobile_push.tests, you would also include that in this list
    packages=find_packages(),
    # Any executable scripts, typically in 'bin'. E.g 'bin/do-something.py'
    scripts=[],
    # REQUIRED: Your project's URL
    url='https://github.com/theKono/mobile-push',
    # Put your license here. See LICENSE.txt for more information
    license=read_from_file('LICENSE'),
    # Put a nice one-liner description here
    description='A mobile-push microservice (APNS, GCM)',
    long_description=read_from_file('README.md'),
    # Any requirements here, e.g. "Django >= 1.1.1"
    install_requires=read_from_file('requirements.txt').split('\n'),
)
