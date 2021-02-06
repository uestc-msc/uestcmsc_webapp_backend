# 阮薇薇点名啦 后端部署

部署环境：

* Ubuntu 18.04 / CentOS 7 / Windows 10, 
* Python 3.7~3.9

## Docker、MySQL 部署

安装 Docker：

```sh
bash <(curl -s https://get.docker.com)
```

安装 MySQL：

```sh
docker run -dit --name mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=testtest -e MYSQL_DATABASE=uestcmsc_webapp -v ~/mysql:/usr/lib/mysql --restart always mysql
```

## Django 运行

按自己的情况修改 `config.template.py`，并保存为 `config.py`。然后安装依赖库并初始化数据库：

```sh
git clone https://github.com/uestc-msc/uestcmsc_webapp_backend
cd uestcmsc_webapp_backend
sudo apt-get install libmysqlclient-dev     # Ubuntu 需要安装 libmysqlclient-dev
sudo yum install python3-devel maria-devel  # CentOS 需要安装 python3-devel maria-devel
pip3 install -r requirements.txt
python3 manage.py makemigrations accounts activities cloud comment gallery users --noinput
python3 manage.py migrate --noinput
python3 manage.py collectstatic --noinput --clear
```

运行 Django Server：

```sh
python3 manage.py runserver
```

访问 `http://localhost:8000/api/` 即可。

## 使用 Gunicorn 部署 Django

在项目目录下运行：

```
gunicorn -b "127.0.0.1:8000" uestcmsc_webapp_backend.wsgi
```

然后借助 Nginx、Apache 或 Caddy 实现反向代理。注意还需要对 `/etc/uestc_webapp/backend/.static/` 中的文件提供 file_server 服务。这里提供一份 Caddy 2 的配置文件 [Caddyfile](./Caddyfile)。

## 加入 systemd 实现自动重启

```sh
sudo cp deploy/uestcmsc_webapp_backend.service /etc/systemd/system
sudo systemctl enable uestcmsc_webapp_backend.service
sudo systemctl start uestcmsc_webapp_backend.service
```