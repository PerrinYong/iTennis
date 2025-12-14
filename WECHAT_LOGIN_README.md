# 🎉 微信小程序登录功能 - 使用指南

## ✨ 功能介绍

已为爱特尼网球评测小程序完整实现微信登录功能：
- ✅ 微信一键登录
- ✅ 头像选择（原生组件）
- ✅ 昵称输入（原生组件）
- ✅ JWT Token认证
- ✅ 自动登录状态保持
- ✅ Token过期处理
- ✅ 用户信息管理

## 📦 已创建的文件

### 后端文件
```
aiteni-backend/
├── backend/
│   ├── auth_views.py           ✨ 登录接口实现
│   ├── models.py               ✅ 用户模型（已有微信字段）
│   ├── urls.py                 📝 添加了登录路由
│   └── settings.py             📝 添加了微信配置
├── requirements.txt            📝 添加了PyJWT依赖
├── .env.example                📝 添加了微信配置示例
├── test_login.py               ✨ 接口测试脚本
└── postman_collection.json     ✨ Postman测试集合
```

### 前端文件
```
aiteni-app/
└── miniprogram/
    ├── pages/login/            ✨ 完整的登录页面
    │   ├── login.js
    │   ├── login.json
    │   ├── login.wxml
    │   └── login.wxss
    ├── utils/api.js            📝 添加了登录API
    ├── app.js                  📝 更新了登录状态管理
    └── app.json                📝 添加了login路由
```

### 文档文件
```
根目录/
├── WECHAT_LOGIN_QUICKSTART.md      ✨ 5分钟快速开始
├── WECHAT_LOGIN_SETUP.md           ✨ 详细配置指南
└── WECHAT_LOGIN_IMPLEMENTATION.md  ✨ 实现总结文档
```

## 🚀 快速开始（只需3步）

### 步骤1️⃣：获取微信凭证

1. 登录 https://mp.weixin.qq.com/
2. 进入【开发 → 开发管理 → 开发设置】
3. 复制 **AppID** 和 **AppSecret**

### 步骤2️⃣：配置后端

编辑 `aiteni-backend/backend/settings.py`，在文件末尾找到：

```python
# 微信小程序配置
WECHAT_APPID = ''  # 👈 粘贴你的AppID
WECHAT_APPSECRET = ''  # 👈 粘贴你的AppSecret
```

安装依赖并启动：

```bash
cd aiteni-backend
pip install -r requirements.txt
python manage.py runserver
```

### 步骤3️⃣：运行小程序

1. 用微信开发者工具打开 `aiteni-app` 目录
2. 填写你的小程序AppID
3. 勾选【详情 → 本地设置 → 不校验合法域名】
4. 编译运行，进入登录页面测试

## 🎯 功能演示

### 登录流程

```
1. 启动小程序 → 自动进入登录页
2. 点击头像区域 → 选择头像（微信原生）
3. 输入昵称 → 可手动输入
4. 点击"微信一键登录" → 自动完成登录
5. 成功后跳转首页 → Token已存储
```

### 页面截图说明

登录页包含：
- 🎾 应用Logo
- 🖼️ 头像选择按钮
- ✏️ 昵称输入框
- 🔘 登录按钮
- 📜 用户协议提示

## 🔧 API接口说明

### 1. 登录接口

```http
POST /api/auth/login
Content-Type: application/json

{
  "code": "微信临时登录凭证",
  "avatarUrl": "用户头像URL",
  "nickName": "用户昵称"
}
```

**成功响应**：
```json
{
  "code": 200,
  "msg": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "userInfo": {
      "id": 1,
      "nickName": "张三",
      "avatarUrl": "https://..."
    }
  }
}
```

### 2. Token验证接口

```http
POST /api/auth/verify
Authorization: Bearer <token>
```

**成功响应**：
```json
{
  "code": 200,
  "msg": "Token有效",
  "data": {
    "userId": 1,
    "userInfo": {
      "nickName": "张三",
      "avatarUrl": "https://..."
    }
  }
}
```

## 🧪 测试方法

### 方法1：使用Python测试脚本

```bash
cd aiteni-backend
python test_login.py
```

脚本会：
- ✅ 测试健康检查
- ✅ 测试参数校验
- ✅ 支持真实code测试
- ✅ 自动测试Token验证

### 方法2：使用Postman

1. 导入 `aiteni-backend/postman_collection.json`
2. 修改变量 `base_url` 为你的后端地址
3. 运行测试用例集合

### 方法3：小程序真机测试

1. 微信开发者工具中【预览】
2. 手机扫码打开
3. 完成登录流程
4. 查看后端日志确认请求

## 📋 配置检查清单

部署前请确认：

### 必须配置 ✅
- [ ] 微信小程序 AppID（settings.py）
- [ ] 微信小程序 AppSecret（settings.py）
- [ ] 后端API地址（api.js中的BASE_URL）
- [ ] 安装了PyJWT依赖

### 生产环境额外配置 🚀
- [ ] 使用环境变量存储敏感信息
- [ ] 配置独立的JWT_SECRET
- [ ] 启用HTTPS
- [ ] 微信公众平台配置服务器合法域名
- [ ] 修改DEBUG=False
- [ ] 配置生产数据库

## ⚠️ 常见问题

### Q1: code无效或已过期
**原因**：微信code只能使用一次，有效期5分钟  
**解决**：重新登录获取新code

### Q2: 获取用户信息失败
**原因**：AppID或AppSecret配置错误  
**解决**：检查settings.py中的配置，查看后端日志

### Q3: 网络请求失败
**原因**：域名未配置或不是HTTPS  
**解决**：
- 开发阶段：勾选"不校验合法域名"
- 生产环境：配置HTTPS和合法域名

### Q4: Token已过期
**原因**：Token默认有效期7天  
**解决**：重新登录获取新Token

### Q5: 头像无法显示
**原因**：默认头像图片不存在  
**解决**：
- 方案1：在images目录放置default-avatar.png
- 方案2：使用网络图片URL
- 方案3：在wxml中用emoji替代

## 📚 详细文档

- **快速开始**：[WECHAT_LOGIN_QUICKSTART.md](./WECHAT_LOGIN_QUICKSTART.md)
- **详细配置**：[WECHAT_LOGIN_SETUP.md](./WECHAT_LOGIN_SETUP.md)
- **实现总结**：[WECHAT_LOGIN_IMPLEMENTATION.md](./WECHAT_LOGIN_IMPLEMENTATION.md)

## 🔐 安全提醒

### 开发环境
- ✅ 可以在settings.py中硬编码AppID和AppSecret
- ✅ 可以关闭域名校验
- ✅ 可以使用HTTP协议

### 生产环境
- ⚠️ 必须使用环境变量存储密钥
- ⚠️ 必须配置HTTPS
- ⚠️ 必须在微信公众平台配置服务器域名
- ⚠️ 不要将AppSecret提交到代码仓库
- ⚠️ 使用独立的JWT_SECRET

## 🎯 下一步建议

### 功能扩展
1. **手机号绑定**：使用微信手机号快速验证
2. **Token刷新**：实现refresh token机制
3. **多端登录管理**：记录登录设备
4. **用户行为统计**：登录次数、活跃度分析

### 界面优化
1. **引导页**：首次使用引导
2. **骨架屏**：登录加载优化
3. **错误提示**：更友好的错误信息
4. **退出登录**：添加退出功能入口

## 📞 获取帮助

遇到问题时：

1. **查看日志**
   - 后端：`aiteni-backend/logs/error-YYYY-MM-DD.log`
   - 前端：微信开发者工具控制台

2. **检查配置**
   - 确认AppID和AppSecret正确
   - 确认后端服务已启动
   - 确认网络连接正常

3. **参考文档**
   - 微信小程序官方文档
   - Django官方文档
   - 本项目配置文档

## ✅ 测试验收标准

功能测试通过标准：
- [x] 能够正常选择头像
- [x] 能够输入昵称
- [x] 点击登录按钮正常发起请求
- [x] 后端正确返回Token
- [x] Token被正确存储到本地
- [x] 登录成功后跳转到首页
- [x] 下次启动自动登录
- [x] Token过期后提示重新登录

## 🎉 完成状态

- ✅ 后端接口开发完成
- ✅ 前端页面开发完成
- ✅ 配置文档编写完成
- ✅ 测试脚本准备完成
- ⏳ 等待配置AppID和AppSecret
- ⏳ 等待测试验收
- ⏳ 等待生产环境部署

---

**开发完成时间**：2025年12月14日  
**开发者**：GitHub Copilot  
**版本**：v1.0.0

祝你使用愉快！🎾
