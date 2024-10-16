#!/bin/sh

cd /home/user
pip3 install -r requirements.txt

exec "$@"