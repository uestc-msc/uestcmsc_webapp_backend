#!/bin/bash

cd /etc/uestcmsc_webapp/backend || return 1
git pull
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt
python3 manage.py makemigrations accounts activities cloud gallery users
python3 manage.py migrate