#!/bin/bash

cd /etc/uestcmsc_webapp/backend || return 1
sudo systemctl stop uestcmsc_webapp_backend
git pull
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt
python3 manage.py makemigrations accounts activities cloud gallery users
python3 manage.py migrate
sudo systemctl start uestcmsc_webapp_backend