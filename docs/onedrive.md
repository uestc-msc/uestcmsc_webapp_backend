# Onedrive 云盘相关使用

## 简介

本 Web App 使用 Onedrive for Business 作为云盘后端（理论上兼容 Onedrive 个人版）。

本 Web App 通过 Microsoft Graph API 调用 [Onedrive REST API](https://docs.microsoft.com/zh-cn/onedrive/developer/)，并对常用接口进行简单封装，封装到了 `/cloud/onedrive/`。

## 前期工作

可参考 [博客](https://blog.lyh543.cn/back-end/onedrive-rest-api/#注册应用、用户登录授权)。请将 `重定向 URI` 设置为 `http://localhost:8000/api/cloud/login_callback/` 和 `https://你的域名/api//cloud/login_callback/`。

完成后将 `ONEDRIVE_CLIENT_ID` 和 `ONEDRIVE_CLIENT_SECRET` 填在 `config.py` 中。

运行后端，访问 `localhost:8000/api/cloud/login/` 将被重定向到 Microsoft 登陆界面。

在 Microsoft 登陆授权后跳转到 `localhost:8000/api/cloud/login_callback/`，Django 自动获取 Access Token 和 Refresh Token 后跳转到前端页面 `localhost:8080`（只要跳转成功即表示成功获取），之后就可以享用 Onedrive REST API 了。

## 本后端提供的接口

### 上传

为了省去文件经过服务器的流量，本后端使用 Onedrive 的[通过上传会话上传大文件](https://docs.microsoft.com/zh-cn/graph/api/driveitem-createuploadsession) 方案上传文件。前后端和 Onedrive 的交互过程如下：


1. 在登陆状态下，前端向后端 `POST /api/cloud/file` 发起请求，后端请求 Onedrive 生成一个临时上传对话，并将 Onedrive 的应答（格式见上面的链接）转发给前端；
2. 前端按照上面链接所述方法，直接向 Onedrive 上传文件。上传完成后，Onedrive 返回文件的 id 等信息，文件将位于 `/(应用文件夹)/temp/{userid}/` 文件夹；
3. 前端根据需求（如上传沙龙相关文件、沙龙照片）向对应接口发起请求（请求需包含文件 id），后端将文件移动至每个功能对应的文件夹，并完成后续操作（录入数据库等）。

### 下载

为了省去文件经过服务器的流量，本后端只提供下载链接。由于 Onedrive API 限制，提供两种下载链接：

* 永久链接，但需在浏览器中访问
* 临时链接（Onedrive 链接有效期 15min，但本后端提供即时获取链接并重定向的 REST API）

#### 永久链接

有网友发现，手动或[利用 Onedrive API](https://docs.microsoft.com/zh-cn/graph/api/driveitem-createlink?view=graph-rest-1.0) 生成分享链接后，在分享链接后追加 `?download=1` 参数，在浏览器访问该链接即可自动下载文件。

但该链接对应的 html 需要运行 JavaScript，因此不能通过 `requests` 或 `XMLHTTPRequest` 直接下载。

#### 临时链接

[利用 Onedrive API 下载文件](https://docs.microsoft.com/zh-cn/graph/api/driveitem-get-content) 时，响应报文为 `302 Found`，`Location` 为一个下载 URL。该 URL 仅在较短的一段时间 （几分钟后）内有效，不需要认证即可下载。

本后端提供 `/cloud/file/{id}/download/` API，该 API 调用上述 API 后将报文返回给前端。
