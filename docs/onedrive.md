# Onedrive 云盘相关使用

## 简介

本 Web App 使用 Onedrive for Business 作为云盘后端（理论上兼容 Onedrive 个人版）。

本 Web App 通过 Microsoft Graph API 调用 [Onedrive REST API](https://docs.microsoft.com/zh-cn/onedrive/developer/?view=odsp-graph-online)，并对常用接口进行简单封装，封装到了 `/utils/onedrive/`。

## 前期工作

可参考 [博客](https://blog.lyh543.cn/back-end/onedrive-rest-api/注册应用、用户登录授权)。请将 `重定向 URI` 设置为 `http://localhost:8000/api/cloud/login/` 和 `https://你的域名/api/cloud/login/`。

完成后将信息填在 `config.py` 中。

运行后端，访问 `localhost:8000/api/cloud/login/` 将被重定向到 Microsoft 登陆界面。

在 Microsoft 登陆授权后跳转到 `localhost:8000/api/cloud/login/`，Django 自动获取 Access Token 和 Refresh Token 后跳转到前端页面 `localhost:8080`（只要跳转成功即表示成功获取），之后就可以享用 Onedrive REST API 了。

## 本后端提供的接口

### 上传

为了省去文件经过服务器的流量，本后端使用 Onedrive 的[通过上传会话上传大文件](https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/api/driveitem_createuploadsession?view=odsp-graph-online) 方案上传文件。前后端和 Onedrive 的交互过程如下：


1. 在登陆状态下，前端向后端 `POST /api/cloud/create_upload_session` 发起请求，后端请求 Onedrive 生成一个临时上传对话，并将 Onedrive 的应答（格式见上面的链接）转发给前端；
2. 前端按照上面链接所述方法，直接向 Onedrive 上传文件。上传完成后，Onedrive 返回文件的 id 等信息，文件将位于 `/(应用文件夹)/temp` 文件夹；
3. 前端根据需求（如上传沙龙相关文件、沙龙照片）向对应接口发起请求（请求需包含文件 id），后端将文件移动至每个功能对应的文件夹，并完成后续操作（录入数据库等）。
