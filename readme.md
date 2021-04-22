# 阮薇薇点名啦 后端


[![Django Test](https://github.com/uestc-msc/uestcmsc_webapp_backend/actions/workflows/django-test.yml/badge.svg)](https://github.com/uestc-msc/uestcmsc_webapp_backend/actions/workflows/django-test.yml)
![Language](https://img.shields.io/badge/Python-3.7~3.9-blue.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
<a href="http://www.djangoproject.com/"><img src="https://www.djangoproject.com/m/img/badges/djangomade124x25.gif" border="0" alt="Made with Django." title="Made with Django." /></a>


本 API 遵循[语义化版本控制](https://semver.org/lang/zh-CN/)。

## 运行 & 部署

运行环境：

* Ubuntu 18.04 / Windows 10, 
* Python 3.7~3.9

[部署文档](docs/deploy/deploy.md)

## 文档

* API 文档：本项目的 API 文档使用 [drf-yasg](https://github.com/axnsan12/drf-yasg/) 生成。运行项目后见 `http://localhost:8000/api/docs/`
* [数据模型文档](docs/models.md)

## TO-DO

* 微信用户迁移
* 留言板块
* 云盘及图片板块
* 经验及经验变化记录板块
* 记录并屏蔽频繁登录的情况
* 邮件推送提醒活动
* 邮件推送留言、评论
* 修改用户信息部分，目前采用管理员和用户在修改字段上同权
* 给活动加上 tag
* 超级用户修改管理员名单
* GitHub OAuth
