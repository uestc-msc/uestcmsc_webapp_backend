#!/bin/bash

cd /etc/uestcmsc_webapp/backend || return 1
sudo systemctl stop uestcmsc_webapp_backend
git pull || return 1
sudo python3 -m pip install --upgrade pip
sudo pip3 install -r requirements.txt
python3 manage.py makemigrations accounts activities cloud comment gallery users --noinput
python3 manage.py migrate --noinput
sudo systemctl start uestcmsc_webapp_backend