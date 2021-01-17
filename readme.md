# 阮薇薇点名啦 后端

## 环境配置

部署环境：

* Ubuntu 18.04 / Windows 10, 
* Python 3.6~3.9

### Docker、MySQL 部署

安装 Docker：

```sh
bash <(curl -s https://get.docker.com)
```

安装 MySQL：

```sh
docker run -dit --name mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=testtest -e MYSQL_DATABASE=uestcmsc_webapp -v ~/mysql:/usr/lib/mysql --restart always mysql
```

### Django 部署

按自己的情况修改 `config.template.py`，并保存为 `config.py`。然后安装依赖库并初始化数据库：

```sh
pip3 install -r requirements.txt
python3 manage.py migrate
```

运行 Django Server：

```sh
python3 manage.py runserver
```

访问 `http://localhost:8000/` 即可。

## 文档

* API 文档：`http://localhost:8000/docs/`
* [数据模型文档](docs/model.md)