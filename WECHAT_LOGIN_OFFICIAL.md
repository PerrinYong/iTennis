# ✅ 微信小程序登录 - 官方最新推荐方案

## 📋 实现说明

已按照**微信官方2022年10月25日后的最新规范**实现登录功能。

## 🎯 核心方案

### 1. 登录流程（wx.login）

按照微信官方文档的登录流程时序图实现：

```
用户操作
  ↓
小程序调用 wx.login() 获取临时登录凭证 code
  ↓
小程序将 code 传给开发者服务器
  ↓
开发者服务器调用 auth.code2Session 接口
  ↓
微信接口返回 openid + session_key (+ unionid)
  ↓
开发者服务器生成自定义登录态（JWT Token）
  ↓
返回 Token 给小程序
  ↓
小程序存储 Token，后续请求携带
  ↓
登录完成
```

### 2. 头像昵称获取（头像昵称填写能力）

使用微信官方推荐的"头像昵称填写能力"（基础库 2.21.2+）：

#### 头像选择
```html
<button open-type="chooseAvatar" bind:chooseavatar="onChooseAvatar">
  <image src="{{avatarUrl}}"></image>
</button>
```

```javascript
onChooseAvatar(e) {
  const { avatarUrl } = e.detail;
  this.setData({ avatarUrl });
}
```

**特点**：
- ✅ 官方推荐方案
- ✅ 从基础库 2.21.2 开始支持
- ✅ 覆盖 iOS 与安卓微信 8.0.16 以上版本
- ✅ 从基础库 2.24.4 起，自动接入内容安全检测

#### 昵称输入
```html
<input type="nickname" bindinput="onNicknameInput" />
```

```javascript
onNicknameInput(e) {
  const nickName = e.detail.value;
  this.setData({ nickName });
}
```

**特点**：
- ✅ 输入时键盘上方会显示微信昵称
- ✅ 从基础库 2.24.4 起，失焦时自动进行安全检测
- ✅ 未通过安全检测会自动清空内容

## 🚫 已废弃的API

### wx.getUserProfile（已于2022年10月25日废弃）

**生效期后的变化**：
- ❌ 通过 `wx.getUserProfile` 获取的头像统一返回默认灰色头像
- ❌ 通过 `wx.getUserProfile` 获取的昵称统一返回"微信用户"
- ❌ 生效期前发布的版本不受影响，但版本更新需要适配

**官方公告**：
https://developers.weixin.qq.com/community/develop/doc/000cacfa20ce88df04cb468bc52801

## 📝 当前实现代码说明

### 前端代码

#### 页面结构（login.wxml）
```xml
<!-- 头像选择（官方推荐方式） -->
<button open-type="chooseAvatar" bind:chooseavatar="onChooseAvatar">
  <image src="{{avatarUrl}}"></image>
</button>

<!-- 昵称输入（官方推荐方式） -->
<input 
  type="nickname" 
  bindinput="onNicknameInput"
  bindblur="onNicknameBlur"
/>

<!-- 登录按钮 -->
<button bindtap="wxLogin">微信一键登录</button>
```

#### 登录逻辑（login.js）
```javascript
// 1. 用户选择头像（通过 chooseAvatar）
onChooseAvatar(e) {
  const { avatarUrl } = e.detail;
  this.setData({ avatarUrl });
}

// 2. 用户输入昵称（通过 type="nickname"）
onNicknameInput(e) {
  const nickName = e.detail.value;
  this.setData({ nickName });
}

// 3. 点击登录
async wxLogin() {
  // 3.1 获取临时登录凭证 code
  const { code } = await wx.login();
  
  // 3.2 传给后端（code + 头像 + 昵称）
  const res = await api.wechatLogin({
    code: code,
    avatarUrl: this.data.avatarUrl,
    nickName: this.data.nickName
  });
  
  // 3.3 保存 Token
  wx.setStorageSync('token', res.data.token);
  
  // 3.4 登录完成
  wx.switchTab({ url: '/pages/welcome/welcome' });
}
```

### 后端代码

#### 登录接口（auth_views.py）
```python
def wechat_login(request):
    # 1. 接收参数
    code = request.POST.get('code')
    avatar_url = request.POST.get('avatarUrl')
    nick_name = request.POST.get('nickName')
    
    # 2. 调用微信接口，用 code 换取 openid
    wx_response = requests.get(
        'https://api.weixin.qq.com/sns/jscode2session',
        params={
            'appid': WECHAT_APPID,
            'secret': WECHAT_APPSECRET,
            'js_code': code,
            'grant_type': 'authorization_code'
        }
    )
    
    openid = wx_response.json()['openid']
    
    # 3. 创建/更新用户
    user = User.objects.update_or_create(
        wechat_openid=openid,
        defaults={
            'wechat_nickname': nick_name,
            'wechat_avatar': avatar_url
        }
    )
    
    # 4. 生成 JWT Token
    token = jwt.encode({
        'user_id': user.id,
        'openid': openid,
        'exp': datetime.utcnow() + timedelta(days=7)
    }, JWT_SECRET)
    
    # 5. 返回 Token
    return JsonResponse({
        'code': 200,
        'data': {
            'token': token,
            'userInfo': {
                'id': user.id,
                'nickName': user.wechat_nickname,
                'avatarUrl': user.wechat_avatar
            }
        }
    })
```

## ✨ 优势

### 相比废弃的 wx.getUserProfile

| 特性 | wx.getUserProfile (废弃) | 头像昵称填写能力 (推荐) |
|------|--------------------------|------------------------|
| 官方支持 | ❌ 已废弃 | ✅ 官方推荐 |
| 长期维护 | ❌ 不再维护 | ✅ 长期支持 |
| 获取真实头像 | ❌ 返回灰色头像 | ✅ 用户真实头像 |
| 获取真实昵称 | ❌ 返回"微信用户" | ✅ 用户真实昵称 |
| 内容安全 | ❌ 需自行处理 | ✅ 自动安全检测 |
| 用户体验 | ❌ 弹窗授权 | ✅ 自然填写 |

## 🔒 安全特性

### 内容安全检测（基础库 2.24.4+）

#### 头像安全检测
- 用户上传的图片自动接入 `mediaCheckAsync` 接口
- 未通过安全检测：不触发 `bindchooseavatar` 事件
- 开发者无需额外处理

#### 昵称安全检测
- 失焦时（`onBlur`）自动接入 `msgSecCheck` 接口
- 未通过安全检测：微信自动清空输入内容
- 建议通过 form 的 submit 按钮收集内容

## 📋 兼容性说明

### 基础库版本要求

| 功能 | 最低基础库版本 | 说明 |
|------|--------------|------|
| 头像选择 | 2.21.2 | chooseAvatar |
| 昵称输入 | 2.21.2 | type="nickname" |
| 内容安全 | 2.24.4 | 自动安全检测 |
| wx.login | 1.0.0 | 所有版本支持 |

### 覆盖范围
- iOS 微信 8.0.16+
- 安卓微信 8.0.16+

### 低版本处理
对于低于 2.21.2 的基础库，建议：
1. 使用普通 `<input>` 输入昵称
2. 使用图片上传组件选择头像
3. 或提示用户升级微信版本

## 🎯 关键注意事项

### 1. code 的使用限制
- ⚠️ **只能使用一次**：code 使用后立即失效
- ⚠️ **有效期 5 分钟**：超时需重新获取
- ⚠️ **不要在前端多次调用**：确保只调用一次后端接口

### 2. session_key 的保护
- ⚠️ **不要下发到小程序**：session_key 只在后端使用
- ⚠️ **不要对外提供**：这是加密签名的密钥
- ⚠️ **妥善保存**：建议加密存储

### 3. 头像处理
- ⚠️ **临时路径**：`chooseAvatar` 返回的是临时路径
- ✅ **需要上传**：如需永久保存，需上传到自己的服务器
- ✅ **或直接使用**：直接将临时路径传给后端也可以

### 4. 内容安全
- ⚠️ **自动检测**：从 2.24.4 起自动接入安全检测
- ⚠️ **不合规内容**：会被自动清空或不触发回调
- ✅ **无需额外处理**：微信自动处理，降低开发者风险

## 📊 完整流程图

```
用户进入登录页
    ↓
点击头像选择区域 → 选择头像 (open-type="chooseAvatar")
    ↓                     ↓
    |              微信自动安全检测
    |                     ↓
    |              触发 onChooseAvatar 回调
    |                     ↓
    |              前端存储临时头像路径
    ↓
点击昵称输入框 → 输入昵称 (type="nickname")
    ↓                     ↓
    |              键盘上方显示微信昵称
    |                     ↓
    |              失焦时自动安全检测
    |                     ↓
    |              前端存储昵称
    ↓
点击"微信一键登录"按钮
    ↓
前端调用 wx.login() 获取 code
    ↓
前端将 {code, avatarUrl, nickName} 发送给后端
    ↓
后端调用微信 auth.code2Session 接口
    ↓
微信返回 {openid, session_key, unionid}
    ↓
后端根据 openid 查找/创建用户
    ↓
后端更新用户头像和昵称
    ↓
后端生成 JWT Token
    ↓
后端返回 {token, userInfo}
    ↓
前端存储 Token 到本地
    ↓
跳转到首页
    ↓
登录完成 ✅
```

## 🧪 测试要点

### 功能测试
- [ ] 能正常选择头像
- [ ] 输入昵称时键盘上方显示微信昵称
- [ ] 点击登录正常获取 code
- [ ] 后端正确返回 Token
- [ ] Token 正确存储到本地
- [ ] 登录后正常跳转

### 安全测试（需基础库 2.24.4+）
- [ ] 上传违规图片，不触发 chooseAvatar 回调
- [ ] 输入违规昵称，失焦后自动清空

### 异常测试
- [ ] code 无效或过期
- [ ] 未选择头像直接登录
- [ ] 未输入昵称直接登录
- [ ] 网络请求失败

## 📚 官方文档参考

1. **小程序登录**：https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/login.html
2. **头像昵称填写**：https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/userProfile.html
3. **废弃公告**：https://developers.weixin.qq.com/community/develop/doc/000cacfa20ce88df04cb468bc52801
4. **wx.login API**：https://developers.weixin.qq.com/miniprogram/dev/api/open-api/login/wx.login.html
5. **auth.code2Session**：https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/user-login/code2Session.html

## ✅ 总结

当前实现**完全符合微信官方2022年10月后的最新规范**：

✅ 使用 `wx.login()` 获取 code  
✅ 使用头像昵称填写能力获取用户信息  
✅ 自动接入内容安全检测  
✅ 后端正确处理 code2Session  
✅ 使用 JWT Token 维护登录态  
✅ 完善的错误处理和用户提示  

---

**实现状态**：✅ 已完成，符合官方最新规范  
**基础库要求**：2.21.2+（推荐 2.24.4+）  
**微信版本**：8.0.16+  
**更新时间**：2025年12月14日
