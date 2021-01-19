#!/bin/bash

cd /etc/uestcmsc_webapp/backend || return 1
git pull
pip3 install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate