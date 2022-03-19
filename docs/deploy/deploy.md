# 阮薇薇点名啦 后端开发 & 部署

部署环境：

* Ubuntu 18.04 / CentOS / Windows / Mac OS X 等 
* Docker
* Python 3.6+

## 开发 & 部署：安装 Docker、MySQL、Redis

Linux 安装 Docker（Windows & Mac 自行安装 Docker Desktop）：

```sh
bash <(curl -s https://get.docker.com)
```

# 开发 & 部署：初始化数据库

按自己的情况修改 `.env.template`，并保存为 `.env`。然后安装依赖库并初始化数据库：

```sh
git clone https://github.com/uestc-msc/uestcmsc_webapp_backend
cd uestcmsc_webapp_backend
sudo apt-get install libmysqlclient-dev     # Ubuntu 需要安装 libmysqlclient-dev
sudo yum install python3-devel maria-devel  # CentOS 需要安装 python3-devel maria-devel
pip3 install pipenv pip --upgrade
pipenv install
pipenv shell
python3 manage.py makemigrations accounts activities activities_files activities_photos activities_links activities_comments activities_tags cloud users --noinput
python3 manage.py migrate --noinput
python3 manage.py createcachetable
python3 manage.py collectstatic --noinput --clear --no-post-process
```

虽然最后 Django 是在 docker 里面跑，但是为了将 Django 的 migrations 持久化，所以部署环境也需要在 Docker 外面跑 Django。

## 开发：运行 Django Server：

在 Docker 外跑：

```sh
python3 manage.py runserver
```

访问 `http://localhost:8000/api/` 即可。

## 部署：docker-compose

```
docker-compose up --build -d backend
```

然后借助 Nginx、Apache 或 Caddy 实现反向代理。注意还需要对 `uestcmsc_webbapp_backend/.static/` 中的文件提供 file_server 服务。这里提供一份 Caddy 2 的配置文件 [Caddyfile](Caddyfile)。
