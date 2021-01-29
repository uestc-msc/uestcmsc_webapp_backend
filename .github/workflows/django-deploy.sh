#!/bin/bash

cd /etc/uestcmsc_webapp/backend || return 1
git pull
sudo python3 -m pip install --upgrade pip
sudo pip3 install -r requirements.txt
python3 manage.py makemigrations accounts activities cloud comment gallery users --noinput
python3 manage.py migrate --noinput
python3 manage.py collectstatic
sudo systemctl restart uestcmsc_webapp_backend

sudo cp deploy/Caddyfile /etc/caddy
sudo systemctl restart caddy