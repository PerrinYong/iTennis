# 后端API接口文档

## 📋 接口概览

### 认证相关
- `POST /api/auth/login` - 微信登录
- `POST /api/auth/verify` - 验证Token

### 用户相关（需要登录）
- `GET /api/user/info` - 获取用户信息
- `POST /api/user/update` - 更新用户信息

### 评估相关
- `GET /api/evaluation/questions` - 获取问题配置
- `POST /api/evaluation/basic` - 基础题评估
- `POST /api/evaluation/full` - 完整评估
- `POST /api/evaluation/submit` - 提交答案
- `GET /api/evaluation/demo-cases` - 获取演示案例
- `POST /api/evaluation/demo-evaluate` - 评估演示案例
- `GET /api/evaluation/config` - 获取系统配置

---

## 🔐 认证说明

### Token格式
所有需要认证的接口，请求头需携带Token：
```
Authorization: Bearer <token>
```

### Token获取
通过 `/api/auth/login` 接口登录后获取Token。

### Token有效期
默认7天，过期后需重新登录。

---

## 1. 微信登录

### 接口信息
- **路径**：`POST /api/auth/login`
- **认证**：不需要
- **描述**：微信小程序登录，获取Token

### 请求参数
```json
{
  "code": "微信临时登录凭证（通过wx.login获取）",
  "avatarUrl": "用户头像URL",
  "nickName": "用户昵称"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| code | string | 是 | 微信临时登录凭证，有效期5分钟，只能使用一次 |
| avatarUrl | string | 是 | 用户头像URL |
| nickName | string | 是 | 用户昵称 |

### 响应示例

**成功**（200）：
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

**失败**（400）：
```json
{
  "code": 400,
  "msg": "code无效，请重新登录"
}
```

### 错误码说明
| code | msg | 说明 |
|------|-----|------|
| 400 | 缺少登录凭证code | 请求参数缺少code |
| 400 | 请完善头像和昵称 | 缺少avatarUrl或nickName |
| 400 | code无效，请重新登录 | 微信code已使用或过期 |
| 400 | 登录频率限制，请稍后再试 | 调用频率过快 |
| 400 | 小程序配置错误，请联系管理员 | AppID或AppSecret配置错误 |
| 500 | 服务器内部错误 | 服务器异常 |

---

## 2. 验证Token

### 接口信息
- **路径**：`POST /api/auth/verify`
- **认证**：需要Token
- **描述**：验证Token是否有效

### 请求头
```
Authorization: Bearer <token>
```

### 请求参数
无

### 响应示例

**成功**（200）：
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

**失败**（401）：
```json
{
  "code": 401,
  "msg": "Token已过期，请重新登录"
}
```

### 错误码说明
| code | msg | 说明 |
|------|-----|------|
| 401 | 缺少认证Token | 请求头缺少Authorization |
| 401 | Token已过期，请重新登录 | Token已超过有效期 |
| 401 | Token无效 | Token格式错误或签名无效 |
| 401 | 用户不存在 | Token对应的用户已被删除 |
| 500 | 服务器内部错误 | 服务器异常 |

---

## 3. 获取用户信息

### 接口信息
- **路径**：`GET /api/user/info`
- **认证**：需要Token ✅
- **描述**：获取当前登录用户的详细信息

### 请求头
```
Authorization: Bearer <token>
```

### 请求参数
无

### 响应示例

**成功**（200）：
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": 1,
    "username": "wx_12345678",
    "nickName": "张三",
    "avatarUrl": "https://...",
    "phone": "13800138000",
    "createdAt": "2025-12-14 10:30:00"
  }
}
```

**失败**（401）：
```json
{
  "code": 401,
  "msg": "请先登录"
}
```

---

## 4. 更新用户信息

### 接口信息
- **路径**：`POST /api/user/update`
- **认证**：需要Token ✅
- **描述**：更新当前用户的信息

### 请求头
```
Authorization: Bearer <token>
```

### 请求参数
```json
{
  "nickName": "新昵称",
  "phone": "13800138000",
  "realName": "张三"
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| nickName | string | 否 | 新昵称 |
| phone | string | 否 | 手机号 |
| realName | string | 否 | 真实姓名 |

### 响应示例

**成功**（200）：
```json
{
  "code": 200,
  "msg": "更新成功"
}
```

**失败**（400）：
```json
{
  "code": 400,
  "msg": "请求数据格式错误"
}
```

---

## 🔧 认证装饰器使用

### @login_required
用于必须登录才能访问的接口：

```python
from backend.auth_decorators import login_required

@login_required
def my_protected_view(request):
    user = request.user  # 当前登录用户
    user_id = request.user_id  # 用户ID
    openid = request.openid  # 微信openid
    
    return JsonResponse({
        'code': 200,
        'data': {'userId': user.id}
    })
```

### @optional_login
用于可选登录的接口（登录则有用户信息，不登录也能访问）：

```python
from backend.auth_decorators import optional_login

@optional_login
def my_public_view(request):
    if request.user:
        # 已登录
        return JsonResponse({'msg': f'欢迎 {request.user.wechat_nickname}'})
    else:
        # 未登录
        return JsonResponse({'msg': '欢迎游客'})
```

### get_current_user()
手动获取当前用户：

```python
from backend.auth_decorators import get_current_user

def my_view(request):
    user = get_current_user(request)
    
    if user:
        print(f'当前用户：{user.wechat_nickname}')
    else:
        print('未登录')
```

---

## 📊 响应码规范

### 成功响应
| HTTP状态码 | code | 说明 |
|-----------|------|------|
| 200 | 200 | 请求成功 |

### 客户端错误
| HTTP状态码 | code | 说明 |
|-----------|------|------|
| 400 | 400 | 请求参数错误 |
| 401 | 401 | 未授权（需要登录或Token无效） |
| 404 | 404 | 资源不存在 |

### 服务器错误
| HTTP状态码 | code | 说明 |
|-----------|------|------|
| 500 | 500 | 服务器内部错误 |

---

## 🧪 接口测试

### 使用Python测试脚本
```bash
cd aiteni-backend
python test_login.py
```

### 使用Postman
1. 导入 `postman_collection.json`
2. 设置环境变量 `base_url`
3. 先调用登录接口获取Token
4. Token会自动保存，后续接口自动携带

### 使用curl
```bash
# 登录
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "code": "微信code",
    "avatarUrl": "头像URL",
    "nickName": "昵称"
  }'

# 获取用户信息（需要替换<token>）
curl -X GET http://localhost:8000/api/user/info \
  -H "Authorization: Bearer <token>"
```

---

## 🔒 安全说明

### 1. Token安全
- Token采用JWT加密
- 有效期7天，可配置
- 包含用户ID和openid
- 使用HS256算法签名

### 2. 密钥保护
- AppSecret从环境变量读取
- JWT_SECRET独立配置
- 不在代码中硬编码

### 3. 接口防护
- CSRF豁免（针对API）
- HTTP方法限制
- 参数验证
- 异常捕获

### 4. 日志记录
- 所有请求记录
- 错误详细日志
- 敏感信息脱敏

---

## 📝 开发指南

### 添加新的认证接口

1. 在 `backend/user_views.py` 中创建视图函数
2. 使用 `@login_required` 装饰器
3. 在 `backend/urls.py` 中添加路由
4. 更新本文档

**示例**：
```python
# backend/user_views.py
@csrf_exempt
@require_http_methods(["GET"])
@login_required
def get_my_data(request):
    user = request.user
    # ... 业务逻辑
    return JsonResponse({'code': 200, 'data': {}})

# backend/urls.py
re_path(r'^api/user/my-data/?$', user_views.get_my_data),
```

---

## 📚 相关文档

- [后端功能完整性检查](./BACKEND_COMPLETENESS_CHECK.md)
- [微信登录配置指南](./WECHAT_LOGIN_SETUP.md)
- [快速开始](./WECHAT_LOGIN_QUICKSTART.md)

---

**更新时间**：2025年12月14日  
**API版本**：v1.0
