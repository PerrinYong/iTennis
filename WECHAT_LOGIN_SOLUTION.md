# ⚠️ 微信登录方案说明

## 当前实现方案

已按你的要求修改为**微信一键授权登录**，用户只需点击登录按钮即可。

### 实现逻辑

```
用户点击"微信授权登录"按钮
    ↓
尝试调用 wx.getUserProfile() 获取用户信息
    ↓
如果成功：使用微信头像和昵称
如果失败：使用默认头像和昵称
    ↓
调用 wx.login() 获取code
    ↓
传code + 头像 + 昵称给后端
    ↓
登录成功
```

## ⚠️ 重要提醒

### wx.getUserProfile 已被废弃

**微信官方于2022年10月25日起收回了 `wx.getUserProfile` 接口**，该接口现在已无法正常使用。

官方公告：https://developers.weixin.qq.com/community/develop/doc/000cacfa20ce88df04cb468bc52801

### 当前代码的处理策略

代码中已做容错处理：

```javascript
try {
  // 尝试使用 wx.getUserProfile（可能失败）
  const profileRes = await wx.getUserProfile({
    desc: '用于完善用户资料'
  });
  userInfo = profileRes.userInfo;
} catch (profileErr) {
  // 如果失败，使用默认头像和昵称
  wx.showModal({
    title: '提示',
    content: 'wx.getUserProfile已废弃，将使用默认信息登录'
  });
  
  userInfo = {
    nickName: '网球爱好者',
    avatarUrl: '默认微信头像'
  };
}
```

## 💡 推荐方案

根据微信官方最新规范，有以下几种推荐方案：

### 方案1：头像昵称填写能力（官方推荐）⭐

这是**微信官方目前唯一推荐的方案**，也是我最初实现的方案：

```html
<!-- 头像选择 -->
<button open-type="chooseAvatar" bind:chooseavatar="onChooseAvatar">
  <image src="{{avatarUrl}}"></image>
</button>

<!-- 昵称输入 -->
<input type="nickname" bindinput="onNicknameInput" />

<!-- 登录 -->
<button bindtap="login">登录</button>
```

**优点**：
- ✅ 官方推荐，长期支持
- ✅ 符合最新微信小程序规范
- ✅ 用户体验流畅

**缺点**：
- ❌ 需要用户点击两次（选头像 + 登录）

### 方案2：纯静默登录（最简单）

如果不需要展示用户头像和昵称，可以纯静默登录：

```javascript
async wxLogin() {
  try {
    // 直接获取code
    const { code } = await wx.login();
    
    // 传给后端，后端只用openid识别用户
    const res = await api.wechatLogin({
      code: code,
      avatarUrl: '', // 空值
      nickName: ''   // 空值
    });
    
    // 登录成功
  } catch (err) {
    // 错误处理
  }
}
```

**需要修改后端**：让 avatarUrl 和 nickName 参数变为可选。

**优点**：
- ✅ 真正的一键登录，用户无感知
- ✅ 无需任何授权弹窗

**缺点**：
- ❌ 无法获取用户真实头像和昵称
- ❌ 需要修改后端接口

### 方案3：手机号快速验证

使用微信手机号快速验证：

```html
<button open-type="getPhoneNumber" bindgetphonenumber="getPhoneNumber">
  手机号快速登录
</button>
```

**优点**：
- ✅ 真正的一键授权
- ✅ 可以获取真实手机号

**缺点**：
- ❌ 需要企业小程序认证
- ❌ 需要额外开发后端手机号验证逻辑

## 📋 对比表格

| 方案 | 是否官方推荐 | 一键登录 | 获取头像昵称 | 开发难度 | 用户体验 |
|------|-------------|---------|-------------|---------|---------|
| wx.getUserProfile | ❌ 已废弃 | ❌ | ✅ | 简单 | 差（可能失败） |
| 头像昵称填写 | ✅ 官方推荐 | ❌ | ✅ | 简单 | 好 |
| 纯静默登录 | ✅ | ✅ | ❌ | 最简单 | 最好 |
| 手机号验证 | ✅ | ✅ | ❌ | 复杂 | 好 |

## 🔧 如何切换方案

### 切换回方案1（头像昵称填写）

恢复之前的代码版本即可，或参考以下文件：
- [WECHAT_LOGIN_IMPLEMENTATION.md](./WECHAT_LOGIN_IMPLEMENTATION.md)

### 切换到方案2（纯静默登录）

**前端修改**：

[login.js](aiteni-app/miniprogram/pages/login/login.js)：
```javascript
async wxLogin() {
  this.setData({ isLoading: true });
  
  try {
    const { code } = await wx.login();
    
    const res = await api.wechatLogin({
      code: code,
      avatarUrl: '',
      nickName: '网球爱好者'
    });
    
    wx.setStorageSync('token', res.data.token);
    wx.showToast({ title: '登录成功', icon: 'success' });
    
    setTimeout(() => {
      wx.switchTab({ url: '/pages/welcome/welcome' });
    }, 1500);
    
  } catch (err) {
    wx.showToast({ title: '登录失败', icon: 'none' });
  } finally {
    this.setData({ isLoading: false });
  }
}
```

**后端修改**：

[backend/auth_views.py](aiteni-backend/backend/auth_views.py)：
```python
# 修改参数校验，让头像和昵称变为可选
if not nick_name:
    nick_name = '网球爱好者'  # 使用默认昵称
    
if not avatar_url:
    avatar_url = 'https://默认头像URL'  # 使用默认头像
```

## 📝 当前代码状态

✅ 已按你的要求修改完成
⚠️ 但由于 wx.getUserProfile 已废弃，实际运行时会使用默认头像和昵称

## 🎯 我的建议

根据你的需求"**只需要直接点击微信授权登录即可**"，我建议：

### 最佳选择：方案2（纯静默登录）

1. **用户体验最好**：真正的一键登录，无任何弹窗
2. **开发最简单**：只需小改后端参数校验
3. **长期稳定**：不依赖可能被废弃的API

### 如果需要头像昵称：方案1（头像昵称填写）

虽然需要点击两次，但：
1. **官方唯一推荐方案**
2. **长期维护**
3. **可以获取真实头像昵称**

## 📞 需要帮助？

如果你想切换到其他方案，请告诉我：
- 方案1：切换回头像昵称填写能力
- 方案2：改为纯静默登录（最简单）
- 方案3：使用其他登录方式

我可以帮你快速修改代码。

---

**当前实现**：使用 wx.getUserProfile + 降级处理（可能失败时使用默认信息）  
**推荐方案**：纯静默登录（方案2）或头像昵称填写（方案1）  
**测试状态**：待测试
