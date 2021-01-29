#!/bin/bash
set -xe

cd /etc/uestcmsc_webapp/backend
# 拉取源代码
git pull
# 安装依赖
sudo python3 -m pip install --upgrade pip
sudo pip3 install -r requirements.txt
# 更新数据库、static files
python3 manage.py makemigrations accounts activities cloud comment gallery users --noinput
python3 manage.py migrate --noinput
python3 manage.py collectstatic --noinput --clear
# 重启后端服务
sudo systemctl restart uestcmsc_webapp_backend
# 重启 Caddy 服务
sudo cp deploy/Caddyfile /etc/caddy
sudo systemctl restart caddy
# 测试
sleep 1
curl -sSI "https://app.uestc-msc.com/" | grep "200"
curl -sSI "https://app.uestc-msc.com/api/" | grep "200"
curl -sSI "https://app.uestc-msc.com/api/static/" | grep "200"