# 生产环境配置说明

## ✅ 已完成配置

### 1. 前端配置
**文件**：`aiteni-app/miniprogram/utils/api.js`

```javascript
BASE_URL: 'https://perrin-minigame.cloud/api'
```

- ✅ 使用HTTPS协议
- ✅ 使用域名 perrin-minigame.cloud
- ✅ SSL证书已安装

### 2. 后端配置
**文件**：`aiteni-backend/backend/settings.py`

```python
DEBUG = False
ALLOWED_HOSTS = ['perrin-minigame.cloud', 'www.perrin-minigame.cloud', 'localhost', '127.0.0.1']

# HTTPS和安全配置
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False  # Nginx已处理HTTPS重定向
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

---

## 🔧 服务器Nginx配置参考

确保Nginx配置包含以下内容：

```nginx
server {
    listen 80;
    server_name perrin-minigame.cloud www.perrin-minigame.cloud;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name perrin-minigame.cloud www.perrin-minigame.cloud;

    # SSL证书配置
    ssl_certificate /path/to/your/cert.pem;
    ssl_certificate_key /path/to/your/key.pem;

    # SSL安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 代理Django后端
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件
    location /static/ {
        alias /path/to/aiteni-backend/static/;
    }

    # 其他配置...
}
```

---

## 🎯 微信小程序配置

### 1. 配置服务器域名
登录 [微信公众平台](https://mp.weixin.qq.com/) → 开发 → 开发管理 → 服务器域名

**request合法域名**：
```
https://perrin-minigame.cloud
```

**uploadFile合法域名**（如需上传）：
```
https://perrin-minigame.cloud
```

**downloadFile合法域名**（如需下载）：
```
https://perrin-minigame.cloud
```

### 2. 业务域名（如需使用web-view）
```
https://perrin-minigame.cloud
```

### 3. 域名配置要求
- ✅ 必须使用HTTPS
- ✅ 域名已备案
- ✅ SSL证书有效
- ✅ 不能使用IP地址
- ✅ 端口必须是443

---

## 🔐 环境变量配置

在服务器上设置以下环境变量（建议使用 `.env` 文件）：

```bash
# 微信小程序配置
export WECHAT_APPID="你的AppID"
export WECHAT_APPSECRET="你的AppSecret"

# JWT配置
export JWT_SECRET="随机生成的强密钥"
export JWT_EXPIRATION_DAYS="7"

# Django配置
export DJANGO_SECRET_KEY="随机生成的Django密钥"
```

或者创建 `.env` 文件：

```bash
cd aiteni-backend
cat > .env << EOF
WECHAT_APPID=你的AppID
WECHAT_APPSECRET=你的AppSecret
JWT_SECRET=$(python -c "import secrets; print(secrets.token_hex(32))")
JWT_EXPIRATION_DAYS=7
DJANGO_SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
EOF
```

---

## 🚀 部署步骤

### 1. 更新后端代码
```bash
cd /path/to/aiteni-backend
git pull origin main
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 收集静态文件
```bash
python manage.py collectstatic --noinput
```

### 4. 数据库迁移（如有变更）
```bash
python manage.py migrate
```

### 5. 重启后端服务
```bash
# 如果使用systemd
sudo systemctl restart aiteni-backend

# 或使用supervisorctl
sudo supervisorctl restart aiteni-backend

# 或使用gunicorn
pkill -HUP gunicorn
```

### 6. 重启Nginx
```bash
sudo nginx -t  # 测试配置
sudo systemctl reload nginx
```

### 7. 前端小程序
在微信开发者工具中：
1. 上传代码
2. 提交审核
3. 发布版本

---

## ✅ 验证清单

### 后端验证
```bash
# 1. 检查服务运行
curl -I https://perrin-minigame.cloud/api/

# 2. 测试登录接口
curl -X POST https://perrin-minigame.cloud/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"code":"test","avatarUrl":"https://test.jpg","nickName":"测试"}'
```

### 前端验证
1. 打开微信开发者工具
2. 关闭"不校验合法域名"选项
3. 测试登录功能
4. 检查网络请求是否成功

### SSL证书验证
```bash
# 检查证书有效期
openssl s_client -connect perrin-minigame.cloud:443 -servername perrin-minigame.cloud < /dev/null 2>/dev/null | openssl x509 -noout -dates
```

---

## 📊 监控与日志

### 查看后端日志
```bash
# Django日志
tail -f /path/to/aiteni-backend/logs/all-*.log
tail -f /path/to/aiteni-backend/logs/error-*.log

# Nginx日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 性能监控
```bash
# 检查进程
ps aux | grep gunicorn
ps aux | grep nginx

# 检查端口
netstat -tunlp | grep 8000
netstat -tunlp | grep 443
```

---

## 🔒 安全建议

### 1. 定期更新
- 定期更新SSL证书
- 及时更新Django和依赖包
- 监控安全漏洞

### 2. 备份策略
- 定期备份数据库
- 备份静态文件
- 保存配置文件

### 3. 访问控制
- 限制数据库访问权限
- 使用防火墙规则
- 配置fail2ban防止暴力攻击

### 4. 日志审计
- 定期检查日志
- 监控异常访问
- 设置告警机制

---

## 📞 故障排查

### 问题1：前端无法连接后端
**检查**：
- Nginx是否运行：`sudo systemctl status nginx`
- Django是否运行：`ps aux | grep gunicorn`
- 防火墙是否开放443端口：`sudo firewall-cmd --list-ports`

### 问题2：SSL证书错误
**检查**：
- 证书是否过期
- 证书域名是否匹配
- Nginx SSL配置是否正确

### 问题3：登录失败
**检查**：
- WECHAT_APPID和WECHAT_APPSECRET是否正确
- 微信公众平台域名是否配置
- 后端日志是否有错误

### 问题4：504 Gateway Timeout
**检查**：
- Django进程是否卡死
- 数据库连接是否正常
- 增加Nginx proxy_read_timeout时间

---

## 📝 配置变更记录

| 日期 | 变更内容 | 操作人 |
|------|----------|--------|
| 2025-12-14 | 配置生产域名perrin-minigame.cloud | GitHub Copilot |
| 2025-12-14 | 启用HTTPS和安全配置 | GitHub Copilot |
| 2025-12-14 | 关闭DEBUG模式 | GitHub Copilot |

---

**更新时间**：2025年12月14日  
**环境**：生产环境  
**域名**：https://perrin-minigame.cloud
