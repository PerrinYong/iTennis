# 生产环境问题诊断与解决方案

## 🚨 问题现象
前端登录返回：`ERROR_CONNECTION_REFUSED`

---

## 🔍 问题分析

### 1. 当前架构
```
微信小程序 
    ↓ (HTTPS/443)
Nginx 服务器 
    ↓ (HTTP/8000 内网)
Django 后端
```

### 2. 安全组配置现状
✅ **已开放端口**：
- TCP:443 (HTTPS) - 已开放
- TCP:80 (HTTP) - 已开放
- TCP:22 (SSH) - 已开放
- TCP:3389 (RDP) - 已开放

❌ **未开放端口**：
- TCP:8000 (Django后端) - 不需要开放（内网访问即可）

### 3. 根本原因
⚠️ **Nginx配置问题**：
- 当前Nginx配置只监听 **80端口**
- 没有配置 **443端口的SSL**
- 前端请求 `https://perrin-minigame.cloud/api` 无法被Nginx处理

---

## ✅ 解决方案

### 步骤1：上传SSL证书到服务器

```bash
# 登录服务器
ssh root@perrin-minigame.cloud

# 创建SSL证书目录
mkdir -p /etc/nginx/ssl

# 上传证书（在本地执行）
scp cert.pem root@perrin-minigame.cloud:/etc/nginx/ssl/
scp key.pem root@perrin-minigame.cloud:/etc/nginx/ssl/

# 设置证书权限
chmod 600 /etc/nginx/ssl/key.pem
chmod 644 /etc/nginx/ssl/cert.pem
```

### 步骤2：更新Nginx配置

使用项目中的 `nginx-production.conf` 配置文件：

```bash
# 备份现有配置
cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup

# 或者如果用的是sites-available
cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup

# 上传新配置（在本地执行）
scp aiteni-backend/nginx-production.conf root@perrin-minigame.cloud:/etc/nginx/conf.d/aiteni.conf

# 或者直接编辑
vim /etc/nginx/conf.d/aiteni.conf
# 复制 nginx-production.conf 的内容
```

**关键配置点**：
```nginx
# HTTP (80) - 重定向到HTTPS
server {
    listen 80;
    server_name perrin-minigame.cloud www.perrin-minigame.cloud;
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS (443) - 主服务
server {
    listen 443 ssl http2;
    server_name perrin-minigame.cloud www.perrin-minigame.cloud;
    
    # SSL证书
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # 代理到Django
    location /api/ {
        proxy_pass http://localhost:8000;  # 或 http://backend:8000
        proxy_set_header X-Forwarded-Proto https;
        # ...其他配置
    }
}
```

### 步骤3：修改SSL证书路径

根据你的证书实际位置，修改配置文件中的路径：

```nginx
# 如果使用阿里云证书
ssl_certificate /etc/nginx/ssl/cert.pem;
ssl_certificate_key /etc/nginx/ssl/key.pem;

# 如果使用Let's Encrypt
ssl_certificate /etc/letsencrypt/live/perrin-minigame.cloud/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/perrin-minigame.cloud/privkey.pem;
```

### 步骤4：验证并重启Nginx

```bash
# 测试配置文件语法
nginx -t

# 如果显示 "syntax is ok" 和 "test is successful"，则重启
systemctl reload nginx

# 或
systemctl restart nginx

# 检查Nginx状态
systemctl status nginx

# 检查端口监听
netstat -tunlp | grep nginx
# 应该看到 0.0.0.0:443 和 0.0.0.0:80
```

### 步骤5：确保Django后端运行

```bash
# 检查Django进程
ps aux | grep gunicorn
# 或
ps aux | grep python

# 检查8000端口
netstat -tunlp | grep 8000

# 如果没有运行，启动Django
cd /path/to/aiteni-backend

# 方式1：使用gunicorn（推荐）
gunicorn backend.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 60 \
    --access-logfile logs/gunicorn-access.log \
    --error-logfile logs/gunicorn-error.log \
    --daemon

# 方式2：使用Django自带服务器（不推荐生产环境）
python manage.py runserver 0.0.0.0:8000

# 方式3：使用systemd服务（推荐）
systemctl start aiteni-backend
```

### 步骤6：测试连接

```bash
# 1. 测试后端直接访问
curl http://localhost:8000/api/health

# 2. 测试Nginx到后端
curl http://localhost/api/health

# 3. 测试HTTPS访问
curl https://perrin-minigame.cloud/api/health

# 4. 查看Nginx日志
tail -f /var/log/nginx/aiteni-access.log
tail -f /var/log/nginx/aiteni-error.log
```

---

## 🎯 快速检查清单

### 证书检查
```bash
# 检查证书文件是否存在
ls -la /etc/nginx/ssl/

# 检查证书有效期
openssl x509 -in /etc/nginx/ssl/cert.pem -noout -dates

# 检查证书域名
openssl x509 -in /etc/nginx/ssl/cert.pem -noout -text | grep DNS
```

### 端口检查
```bash
# 检查443端口是否监听
netstat -tunlp | grep :443

# 检查80端口是否监听
netstat -tunlp | grep :80

# 检查8000端口是否监听
netstat -tunlp | grep :8000
```

### 服务检查
```bash
# 检查Nginx状态
systemctl status nginx

# 检查防火墙状态
firewall-cmd --list-ports  # CentOS/RHEL
ufw status                 # Ubuntu

# 检查SELinux（如果有）
getenforce
```

---

## 🔧 常见问题排查

### 问题1：Nginx配置测试失败
```bash
# 查看详细错误
nginx -t

# 常见错误：
# 1. 证书文件不存在
ls -la /etc/nginx/ssl/cert.pem

# 2. 证书权限不对
chmod 644 /etc/nginx/ssl/cert.pem
chmod 600 /etc/nginx/ssl/key.pem
```

### 问题2：HTTPS访问失败
```bash
# 检查443端口是否被占用
netstat -tunlp | grep :443

# 检查防火墙
firewall-cmd --list-all

# 确保443端口开放
firewall-cmd --permanent --add-service=https
firewall-cmd --reload
```

### 问题3：502 Bad Gateway
```bash
# 原因：Nginx无法连接到Django后端

# 检查Django是否运行
ps aux | grep python

# 检查8000端口
netstat -tunlp | grep 8000

# 查看Nginx错误日志
tail -f /var/log/nginx/aiteni-error.log
```

### 问题4：Django后端无法启动
```bash
# 查看Django日志
cd /path/to/aiteni-backend
tail -f logs/error-*.log

# 检查环境变量
echo $WECHAT_APPID
echo $WECHAT_APPSECRET

# 手动启动测试
python manage.py runserver 0.0.0.0:8000
```

---

## 📋 Nginx配置详解

### upstream配置
```nginx
upstream backend {
    server localhost:8000;        # Django运行地址
    # server 127.0.0.1:8000;      # 或者使用IP
    # server backend:8000;        # Docker环境使用服务名
}
```

### HTTP服务器（80端口）
```nginx
server {
    listen 80;
    server_name perrin-minigame.cloud www.perrin-minigame.cloud;
    
    # 保留健康检查的HTTP访问
    location /api/health {
        proxy_pass http://backend;
    }
    
    # 其他请求重定向到HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}
```

### HTTPS服务器（443端口）
```nginx
server {
    listen 443 ssl http2;
    server_name perrin-minigame.cloud www.perrin-minigame.cloud;
    
    # SSL证书（必须配置）
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    # SSL协议和加密套件
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # API代理（核心配置）
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;  # 告诉Django这是HTTPS请求
    }
}
```

---

## 🚀 生产环境systemd服务配置

创建 `/etc/systemd/system/aiteni-backend.service`：

```ini
[Unit]
Description=AiTeni Backend Service
After=network.target

[Service]
Type=forking
User=root
Group=root
WorkingDirectory=/path/to/aiteni-backend
Environment="PATH=/usr/bin:/usr/local/bin"
Environment="WECHAT_APPID=your_appid"
Environment="WECHAT_APPSECRET=your_secret"
ExecStart=/usr/local/bin/gunicorn backend.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 60 \
    --access-logfile /path/to/aiteni-backend/logs/gunicorn-access.log \
    --error-logfile /path/to/aiteni-backend/logs/gunicorn-error.log \
    --daemon
ExecReload=/bin/kill -HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
systemctl daemon-reload
systemctl enable aiteni-backend
systemctl start aiteni-backend
systemctl status aiteni-backend
```

---

## 📝 验证步骤

### 1. 本地测试（在服务器上）
```bash
# 测试Django
curl http://localhost:8000/api/health

# 测试Nginx HTTP
curl http://localhost/api/health

# 测试Nginx HTTPS
curl -k https://localhost/api/health
```

### 2. 外部测试（在本地电脑上）
```bash
# 测试HTTP（会重定向到HTTPS）
curl -I http://perrin-minigame.cloud/api/health

# 测试HTTPS
curl https://perrin-minigame.cloud/api/health
```

### 3. 浏览器测试
访问：https://perrin-minigame.cloud/api/health

应该看到类似：
```json
{"status": "ok"}
```

### 4. 小程序测试
在微信开发者工具中：
1. **关闭**"不校验合法域名"选项
2. 测试登录功能
3. 查看网络请求日志

---

## 🎯 问题解决后的状态

### 端口状态
```bash
$ netstat -tunlp | grep -E ':(80|443|8000)'
tcp  0  0.0.0.0:80     0.0.0.0:*  LISTEN  1234/nginx
tcp  0  0.0.0.0:443    0.0.0.0:*  LISTEN  1234/nginx
tcp  0  0.0.0.0:8000   0.0.0.0:*  LISTEN  5678/python
```

### 服务状态
```bash
$ systemctl status nginx
● nginx.service - nginx
   Active: active (running)

$ systemctl status aiteni-backend
● aiteni-backend.service - AiTeni Backend
   Active: active (running)
```

### 日志状态
```bash
# Nginx访问日志应该显示HTTPS请求
$ tail /var/log/nginx/aiteni-access.log
... "GET /api/health HTTP/2.0" 200 ...

# Django日志应该显示请求处理
$ tail /path/to/aiteni-backend/logs/all-*.log
[INFO] Received request: /api/health
```

---

## 📞 如仍有问题

提供以下信息：

1. **Nginx配置测试结果**
```bash
nginx -t
```

2. **端口监听状态**
```bash
netstat -tunlp | grep -E ':(80|443|8000)'
```

3. **Nginx日志**
```bash
tail -50 /var/log/nginx/aiteni-error.log
```

4. **Django日志**
```bash
tail -50 /path/to/aiteni-backend/logs/error-*.log
```

5. **curl测试结果**
```bash
curl -v https://perrin-minigame.cloud/api/health
```

---

**更新时间**：2025年12月14日
**问题**：ERROR_CONNECTION_REFUSED
**原因**：Nginx未配置SSL
**解决**：添加443端口SSL配置
