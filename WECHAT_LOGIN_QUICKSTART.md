# 微信小程序登录功能 - 快速开始

## 🚀 5分钟快速配置

### 第一步：获取微信小程序凭证

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入 **开发** → **开发管理** → **开发设置**
3. 复制 **AppID** 和 **AppSecret**

### 第二步：配置后端

编辑 `aiteni-backend/backend/settings.py` 文件末尾：

```python
# 微信小程序配置
WECHAT_APPID = '你的AppID'  # 👈 粘贴AppID
WECHAT_APPSECRET = '你的AppSecret'  # 👈 粘贴AppSecret
```

安装依赖并启动：

```bash
cd aiteni-backend
pip install -r requirements.txt
python manage.py runserver
```

### 第三步：配置前端

1. 用微信开发者工具打开 `aiteni-app` 目录
2. 填写你的小程序AppID
3. 勾选"不校验合法域名"（右上角详情 → 本地设置）
4. 编译运行

### 第四步：测试登录

1. 小程序启动后会自动进入登录页
2. 点击头像选择器，选择头像
3. 输入昵称
4. 点击"微信一键登录"
5. 成功后自动跳转首页

## 📝 主要文件说明

### 后端文件
- `backend/auth_views.py` - 登录接口实现
- `backend/models.py` - 用户模型（已包含微信字段）
- `backend/urls.py` - 路由配置
- `backend/settings.py` - 配置文件

### 前端文件
- `pages/login/` - 登录页面
- `utils/api.js` - API接口封装
- `app.js` - 全局登录状态管理
- `app.json` - 页面路由配置

## 🔧 API接口

### 登录接口
```
POST /api/auth/login

参数：
{
  "code": "微信code",
  "avatarUrl": "头像URL",
  "nickName": "昵称"
}

返回：
{
  "code": 200,
  "msg": "登录成功",
  "data": {
    "token": "JWT Token",
    "userInfo": {...}
  }
}
```

### Token验证接口
```
POST /api/auth/verify
请求头：Authorization: Bearer <token>
```

## ⚠️ 常见问题

### 1. code无效或已过期
- code只能使用一次，有效期5分钟
- 解决：重新登录获取新code

### 2. 获取用户信息失败
- 检查AppID和AppSecret是否正确
- 查看后端日志：`aiteni-backend/logs/error-*.log`

### 3. 网络请求失败
- 开发阶段：勾选"不校验合法域名"
- 生产环境：在微信公众平台配置request合法域名

## 📚 详细文档

查看完整配置文档：[WECHAT_LOGIN_SETUP.md](./WECHAT_LOGIN_SETUP.md)

## ✨ 核心流程

```
用户点击登录
    ↓
前端获取wx.login() code
    ↓
前端传code+头像+昵称给后端
    ↓
后端用code向微信服务器换取openid
    ↓
后端生成JWT Token
    ↓
后端存储/更新用户信息
    ↓
返回Token给前端
    ↓
前端存储Token
    ↓
登录完成
```

## 🎯 下一步

- [ ] 配置生产环境HTTPS域名
- [ ] 设置环境变量保护密钥
- [ ] 部署到服务器
- [ ] 提交小程序审核

---

有问题？查看详细文档或检查日志文件。
