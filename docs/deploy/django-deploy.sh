# 需要在 pipenv 中执行
#!/bin/bash
set -xe
# 拉取源代码
git pull
pipenv install
python3 manage.py makemigrations accounts activities \
        activities_files activities_photos activities_links activities_comments activities_tags \
        cloud users
python3 manage.py migrate
python3 manage.py createcachetable
python3 manage.py collectstatic --noinput --clear --no-post-process
# python3 manage.py crontab add
# 重启后端服务
docker-compose up --build -d backend
# 测试
sleep 1
curl -sSI "https://api.uestc-msc.com/api/" | grep "200"
curl -sSI "https://api.uestc-msc.com/api/static/" | grep "200"