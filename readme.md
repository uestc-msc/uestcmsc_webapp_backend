# 后端

## 环境配置

部署环境：主流 Linux 或 Windows，尚未安装 Docker 和 Nginx/Apache/Caddy 等服务器。本文以 Ubuntu 20.04 LTS 为部署环境。

### Docker、MySQL 及 Caddy 配置

安装 Docker：

```sh
bash <(curl -s https://get.docker.com)
```

安装 MySQL：

```sh
docker run -dit --name mysql -p 3306:3306 -e MYSQL_ROOT_PASSWORD=uestcmsc2021 --restart always mysql
```

安装 Caddy 并把 Caddyfile 复制到 `/etc/caddy`：

```
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/cfg/gpg/gpg.155B6D79CA56EA34.key' | sudo apt-key add -
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/cfg/setup/config.deb.txt?distro=debian&version=any-version' | sudo tee -a /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install caddy
cp Caddyfile /etc/caddy
```

## to-do

评论