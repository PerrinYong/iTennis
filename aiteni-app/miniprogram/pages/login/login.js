// pages/login/login.js
const api = require('../../utils/api.js');

// 微信默认头像（官方提供的占位图）
const defaultAvatarUrl = 'https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0';

Page({
  data: {
    avatarUrl: defaultAvatarUrl, // 用户头像（使用微信官方默认头像）
    nickName: '', // 用户昵称
    isLoading: false, // 加载状态
  },

  // 页面加载
  onLoad(options) {
    console.log('[Login] 页面加载');
    
    // 检查是否已经登录
    this.checkLoginStatus();
  },

  /**
   * 选择头像（微信官方推荐：open-type="chooseAvatar"）
   * 从基础库2.21.2开始支持
   */
  onChooseAvatar(e) {
    const { avatarUrl } = e.detail;
    console.log('[Login] 选择头像:', avatarUrl);
    
    this.setData({
      avatarUrl: avatarUrl
    });
  },

  /**
   * 输入昵称（微信官方推荐：type="nickname"）
   * 输入时键盘上方会显示微信昵称
   */
  onNicknameInput(e) {
    const nickName = e.detail.value;
    this.setData({
      nickName: nickName
    });
  },

  /**
   * 昵称输入失焦（从基础库2.24.4起，会进行安全检测）
   * 如果未通过安全检测，微信会自动清空内容
   */
  onNicknameBlur(e) {
    const nickName = e.detail.value;
    console.log('[Login] 昵称输入完成:', nickName);
  },

  /**
   * 检查登录状态
   */
  checkLoginStatus() {
    const token = wx.getStorageSync('token');
    if (token) {
      console.log('[Login] 已有Token，验证有效性');
      
      // 验证Token是否有效
      api.verifyToken()
        .then(res => {
          console.log('[Login] Token验证成功，跳转到首页');
          wx.showToast({
            title: '已登录',
            icon: 'success',
            duration: 1500
          });
          
          // 延迟跳转
          setTimeout(() => {
            wx.switchTab({
              url: '/pages/welcome/welcome'
            });
          }, 1500);
        })
        .catch(err => {
          console.log('[Login] Token已失效，需要重新登录');
          // Token失效，清除本地存储
          wx.removeStorageSync('token');
          wx.removeStorageSync('userInfo');
        });
    }
  },

  /**
   * 微信登录（使用官方最新推荐方式）
   * 
   * 流程说明：
   * 1. 用户通过 open-type="chooseAvatar" 选择头像
   * 2. 用户通过 type="nickname" 输入昵称
   * 3. 点击登录按钮
   * 4. 调用 wx.login() 获取临时登录凭证 code
   * 5. 将 code + 头像 + 昵称 传给后端
   * 6. 后端调用微信接口用 code 换取 openid
   * 7. 后端生成 JWT Token 返回给前端
   * 8. 前端存储 Token，完成登录
   */
  async wxLogin() {
    const { avatarUrl, nickName } = this.data;
    
    // 校验头像（不能是默认头像）
    if (avatarUrl === defaultAvatarUrl) {
      wx.showToast({
        title: '请先选择头像',
        icon: 'none',
        duration: 2000
      });
      return;
    }
    
    // 校验昵称
    if (!nickName || nickName.trim() === '') {
      wx.showToast({
        title: '请输入昵称',
        icon: 'none',
        duration: 2000
      });
      return;
    }

    // 设置加载状态
    this.setData({ isLoading: true });

    try {
      console.log('[Login] 开始微信登录流程');
      
      // 1. 调用 wx.login() 获取临时登录凭证 code（有效期5分钟，只能使用一次）
      const loginRes = await wx.login();
      const code = loginRes.code;
      
      if (!code) {
        throw new Error('获取登录凭证失败');
      }
      
      console.log('[Login] 获取到code:', code.substring(0, 10) + '...');
      
      // 2. 调用后端登录接口，传递 code、头像、昵称
      // 后端会用 code 调用微信接口换取 openid 和 session_key
      console.log('[Login] 调用后端登录接口');
      const res = await api.wechatLogin({
        code: code,
        avatarUrl: avatarUrl,
        nickName: nickName.trim()
      });

      console.log('[Login] 登录成功:', res);
      
      // 3. 保存Token和用户信息到本地
      wx.setStorageSync('token', res.token);
      wx.setStorageSync('userInfo', res.userInfo);
      
      // 4. 显示成功提示
      wx.showToast({
        title: '登录成功',
        icon: 'success',
        duration: 2000
      });
      
      // 5. 跳转到首页
      setTimeout(() => {
        wx.switchTab({
          url: '/pages/welcome/welcome'
        });
      }, 2000);
      
    } catch (err) {
      console.error('[Login] 登录失败:', err);
      
      // 显示错误提示
      const errorMsg = err.errMsg || err.msg || err.message || '登录失败，请重试';
      wx.showToast({
        title: errorMsg,
        icon: 'none',
        duration: 3000
      });
      
    } finally {
      // 取消加载状态
      this.setData({ isLoading: false });
    }
  }
});
