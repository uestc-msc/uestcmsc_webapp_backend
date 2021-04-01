# 数据模型

本文档描述了软件中使用的数据模型。

* 超级用户可通过 Django 提供的 `<后端url>/admin/` 接口读取除密码外的所有数据、修改所有数据。
* 由于前后端的 cookie 是通用的，在前端登录后，访问后端 admin 页面不再需要登录。
* 如果需要绕过前端直接访问后端，注意到前端向后端传输密码前，经过了 md5 算法（`后端密码 == md5(前端密码)`），请提前计算 md5 值。可以在 Python3 使用如下方法：

```py
# 前端密码
raw_password='password'

import hashlib
md5_password=hashlib.md5(raw_password.encode()).hexdigest()
# 后端密码
md5_password # '5f4dcc3b5aa765d61d8327deb882cf99'
```

如果你的密码是 `password`，使用邮箱和 `5f4dcc3b5aa765d61d8327deb882cf99` 即可登录。

## 用户模型 UserProfile

用户模型是对 `django.contrib.auth.models.User` 的扩展，扩展的模型为 `users.models.UserProfile`。

-----------------------

本软件使用了 `django.contrib.auth.models.User` 模型的如下属性（√ 允许，× 不允许，○ 见注释）：

字段名|中文|自己可读|自己可写|任何人可读
-|-|:-:|:-:|:-:
username|用户名（邮箱）|√|○|√
first_name|姓名|√|√|√
last_name|头衔|√|√|√
password|密码|×|○|×
is_staff|是否为管理员|√|×|√
is_superuser|是否为超级管理员|√|×|√
last_login|上次登录日期时间|√|×|√
date_joined|注册日期时间|√|×|√

* 注意：**本软件的文档和代码中，`username` 和 `email` 为同一个概念**；
* 使用 `username` 而表示邮箱而不使用 `email` 字段的原因是 Django 认证系统要求 `username` 字段非空、非重复，而 `email` 则为可选字段，登录等函数都使用 `username`；
* 头衔是管理员授予的昵称，类似于 QQ 群头衔，如 `甜乐姐姐`；
* 用户登录并验证原密码后，可修改邮箱、密码。使用 API：`/users/{id}/password/`；
* 用户验证邮箱后，可修改密码。使用 API：`/accounts/forgetpassword/`。

-----------------------

本软件为 `users.models.UserProfile` 模型设置了如下额外属性（√ 允许，× 不允许，○ 见注释）：

字段名|中文|自己可读|自己可写|任何人可读
-|-|:-:|:-:|:-:
student_id|学号|√|√|√
experience|经验|√|×|√
about|自我介绍|√|√|√

### 管理员和超级用户

* 管理员和超级用户拥有用户本人的所有权限；
* 管理员和超级用户可修改权限低于 ta 们的用户的邮箱、密码，无需提供原密码。使用 API：`/users/{id}/changepassword/`；
* 超级用户可修改用户的 `is_staff` 和 `is_superuser` 属性。使用 API：`/users/{id}/admin/`。

