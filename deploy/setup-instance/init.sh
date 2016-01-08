#!/bin/bash
#
# Set up environment for mobile-push microservice

#
# ARGV
#
if [[ -z "$1" ]]; then
    echo "usage: $0 <region>"
    exit 1
fi

region=$1

#
# utilities
#
err() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%Sz')]: $@" >&2
}

#
# apt
#
sudo apt-get update
apt-get install -y supervisor git make build-essential python-dev ntp

#
# set up python environment
#
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py
rm get-pip.py

pip install virtualenv
virtualenv /opt/mobile-push

#
# install AWS CodeDeploy agent
#
apt-get install -y ruby2.0
pip install awscli
aws s3 cp s3://aws-codedeploy-$region/latest/install . --region $region
chmod +x ./install
./install auto
rm ./install

#
# set up code directory structure
#
mkdir -p /srv/mobile-push/release
mkdir -p /srv/mobile-push/share
chown -R ubuntu:ubuntu /srv/mobile-push

#
# supervisor
#
cp ./competing-consumer.conf /etc/supervisor/conf.d/
