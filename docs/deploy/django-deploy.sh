#!/bin/bash
set -xe
cd /etc/uestcmsc_webapp/backend
# 拉取源代码
git pull
# 安装依赖
sudo python3 -m pip install --upgrade pip
sudo pip3 install -r requirements.txt
# 更新数据库、static files、缓存数据库
python3 manage.py makemigrations accounts activities \
        activities_files activities_photos activities_links activities_comments \
        cloud users
python3 manage.py migrate
python3 manage.py collectstatic --clear --no-post-process
python3 manage.py createcachetable
# python3 manage.py crontab add
# 重启后端服务
sudo systemctl stop uestcmsc_webapp_backend
sudo systemctl start uestcmsc_webapp_backend
# 测试
sleep 1
curl -sSI "https://api.uestc-msc.com/api/" | grep "200"
curl -sSI "https://api.uestc-msc.com/api/static/" | grep "200"