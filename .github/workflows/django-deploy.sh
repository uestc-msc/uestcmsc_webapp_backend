#!/bin/bash
set -xe

cd /etc/uestcmsc_webapp/backend
git pull
sudo python3 -m pip install --upgrade pip
sudo pip3 install -r requirements.txt
python3 manage.py makemigrations accounts activities cloud comment gallery users --noinput
python3 manage.py migrate --noinput
python3 manage.py collectstatic --noinput --clear
sudo systemctl restart uestcmsc_webapp_backend

sudo cp deploy/Caddyfile /etc/caddy
sudo systemctl restart caddy

sleep 1
curl -I "https://app.uestc-msc.com/" | grep "200"
curl -I "https://app.uestc-msc.com/api/" | grep "200"
curl -I "https://app.uestc-msc.com/api/static/" | grep "200"