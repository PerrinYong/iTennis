# 微信小程序登录功能配置指南

## 一、后端配置

### 1. 安装依赖

在后端目录 `aiteni-backend` 下运行：

```bash
pip install -r requirements.txt
```

主要新增依赖：
- `PyJWT>=2.8.0` - JWT Token生成和验证

### 2. 配置微信小程序参数

#### 方式一：环境变量（推荐用于生产环境）

在系统环境变量或 `.env` 文件中设置：

```bash
# 微信小程序配置
WECHAT_APPID=你的小程序AppID
WECHAT_APPSECRET=你的小程序AppSecret

# JWT配置（可选，不设置则使用Django的SECRET_KEY）
JWT_SECRET=你的JWT密钥（建议随机生成一个复杂字符串）
JWT_EXPIRATION_DAYS=7
```

#### 方式二：直接修改settings.py（仅用于开发测试）

编辑 `aiteni-backend/backend/settings.py`，找到文件末尾的配置：

```python
# 微信小程序配置
WECHAT_APPID = '你的小程序AppID'  # 替换为实际的AppID
WECHAT_APPSECRET = '你的小程序AppSecret'  # 替换为实际的AppSecret

# JWT配置
JWT_SECRET = '你的JWT密钥'  # 建议使用复杂的随机字符串
JWT_EXPIRATION_DAYS = 7  # Token有效期（天）
```

### 3. 数据库迁移

由于User模型已存在且包含微信登录所需字段，无需额外迁移。如果是全新部署：

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. 启动后端服务

```bash
# Windows
start.bat

# Linux/Mac
python manage.py runserver 0.0.0.0:8000
```

## 二、获取微信小程序AppID和AppSecret

### 1. 登录微信公众平台

访问：https://mp.weixin.qq.com/

使用小程序管理员账号登录。

### 2. 获取AppID和AppSecret

1. 进入 **开发** → **开发管理** → **开发设置**
2. 找到 **开发者ID** 部分：
   - **AppID(小程序ID)**：复制此值
   - **AppSecret(小程序密钥)**：点击"生成"或"重置"获取

⚠️ **重要提示**：
- AppSecret 只显示一次，请妥善保存
- 如果忘记，需要重置（会使旧的失效）
- 切勿将 AppSecret 提交到公开的代码仓库

### 3. 配置服务器域名

在 **开发** → **开发管理** → **开发设置** → **服务器域名** 中：

将后端API域名添加到 **request合法域名**：
```
https://你的后端域名
# 例如：https://api.aiteni.com
```

⚠️ **注意**：
- 必须是 HTTPS 协议（开发阶段可在开发者工具中关闭域名校验）
- 一个月只能修改5次

## 三、前端配置

### 1. 修改API地址

编辑 `aiteni-app/miniprogram/utils/api.js`，修改后端地址：

```javascript
const CONFIG = {
  // 生产环境
  BASE_URL: 'https://你的后端域名/api',
  
  // 或本地开发环境
  // BASE_URL: 'http://localhost:8000/api',
  
  TIMEOUT: 10000
}
```

### 2. 准备默认头像图片

在 `aiteni-app/miniprogram/images/` 目录下放置默认头像图片：
- 文件名：`default-avatar.png`
- 建议尺寸：200x200 像素
- 格式：PNG（支持透明）

如果没有图片，可以暂时使用小程序的占位图或直接删除该路径。

### 3. 微信开发者工具配置

1. 打开微信开发者工具
2. 导入项目（选择 `aiteni-app` 目录）
3. 填写你的小程序AppID
4. **开发阶段**：勾选"不校验合法域名"（在右上角详情 → 本地设置中）

## 四、API接口说明

### 1. 登录接口

**接口地址**：`POST /api/auth/login`

**请求参数**：
```json
{
  "code": "微信临时登录凭证（通过wx.login获取）",
  "avatarUrl": "用户头像URL",
  "nickName": "用户昵称"
}
```

**响应示例**（成功）：
```json
{
  "code": 200,
  "msg": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "userInfo": {
      "id": 1,
      "nickName": "张三",
      "avatarUrl": "https://..."
    }
  }
}
```

**响应示例**（失败）：
```json
{
  "code": 400,
  "msg": "code无效或已过期"
}
```

### 2. Token验证接口

**接口地址**：`POST /api/auth/verify`

**请求头**：
```
Authorization: Bearer <token>
```

**响应示例**（成功）：
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

## 五、测试流程

### 1. 本地测试

#### 后端测试
```bash
# 启动后端
cd aiteni-backend
python manage.py runserver

# 测试健康检查
curl http://localhost:8000/api/health
```

#### 前端测试
1. 打开微信开发者工具
2. 编译并运行小程序
3. 进入登录页面
4. 点击头像选择器（选择头像）
5. 输入昵称
6. 点击"微信一键登录"

### 2. 常见问题排查

#### 问题1：code无效或已过期
- **原因**：code只能使用一次，有效期5分钟
- **解决**：重新获取code（重新登录）

#### 问题2：获取用户信息失败
- **原因**：AppID或AppSecret配置错误
- **解决**：检查配置是否正确，查看后端日志

#### 问题3：网络请求失败
- **原因**：域名未配置或不是HTTPS
- **解决**：开发阶段关闭域名校验；生产环境配置HTTPS和合法域名

#### 问题4：Token已过期
- **原因**：Token有效期已过（默认7天）
- **解决**：重新登录获取新Token

## 六、安全建议

### 1. 生产环境配置
- ✅ 使用环境变量存储敏感信息
- ✅ AppSecret 不要硬编码在代码中
- ✅ 使用独立的 JWT_SECRET
- ✅ 定期更换密钥
- ✅ 启用 HTTPS

### 2. Token管理
- Token 存储在小程序本地缓存
- 后续所有需要认证的API请求都要携带Token
- Token过期后需要重新登录

### 3. 日志记录
- 后端已配置日志记录
- 查看登录日志：`aiteni-backend/logs/info-YYYY-MM-DD.log`
- 查看错误日志：`aiteni-backend/logs/error-YYYY-MM-DD.log`

## 七、部署到生产环境

### 1. 后端部署
```bash
# 设置环境变量
export WECHAT_APPID=你的AppID
export WECHAT_APPSECRET=你的AppSecret
export JWT_SECRET=生产环境的JWT密钥

# 使用gunicorn启动（已在requirements.txt中）
gunicorn -c gunicorn_config.py backend.wsgi:application
```

### 2. 前端配置
1. 修改 `api.js` 中的 BASE_URL 为生产环境地址
2. 在微信公众平台配置服务器域名
3. 上传代码审核并发布

### 3. 验证部署
- 测试登录功能
- 检查Token生成和验证
- 查看后端日志确认请求正常

## 八、功能扩展建议

可以在此基础上扩展的功能：
1. **手机号绑定**：获取用户手机号
2. **会员系统**：根据用户信息实现会员等级
3. **消息推送**：订阅消息通知
4. **分享功能**：分享评测结果
5. **数据统计**：用户行为分析

---

## 联系支持

如有问题，请查看：
- 后端日志：`aiteni-backend/logs/`
- 微信小程序文档：https://developers.weixin.qq.com/miniprogram/dev/framework/
- Django文档：https://docs.djangoproject.com/
