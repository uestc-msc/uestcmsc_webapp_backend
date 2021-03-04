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
python3 manage.py collectstatic --noinput --clear --no-post-process
python3 manage.py crontab add
# 重启后端服务
sudo systemctl stop uestcmsc_webapp_backend
sudo systemctl start uestcmsc_webapp_backend
# 测试
sleep 1
curl -sSI "https://api.uestc-msc.com/api/" | grep "200"
curl -sSI "https://api.uestc-msc.com/api/static/" | grep "200"