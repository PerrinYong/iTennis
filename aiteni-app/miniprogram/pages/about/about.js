// pages/about/about.js
Page({
  data: {
    safeTopPadding: 20, // 页面容器顶部安全留白（rpx�?
    version: '1.0.0',
    features: [
      {
        title: 'NTRP专业评估',
        desc: '基于国际网球评级标准，提供科学准确的水平评估'
      },
      {
        title: '多维度分�?,
        desc: '�?0个维度全面分析您的网球技术水�?
      },
      {
        title: '个性化建议',
        desc: '根据评估结果提供针对性的训练建议'
      },
      {
        title: '历史记录',
        desc: '保存每次评估记录，追踪您的进步历�?
      }
    ]
  },

  onLoad() {
    // 初始化安全区域适配
    this.initSafeArea();
  },

  /**
   * 初始化安全区域适配
   */
  initSafeArea() {
    try {
      const systemInfo = wx.getSystemInfoSync();
      const statusBarHeight = systemInfo.statusBarHeight || 20;
      const navBarHeight = 44;
      const totalHeightPx = statusBarHeight + navBarHeight;
      const totalHeightRpx = totalHeightPx * 2;
      const safeTopPadding = totalHeightRpx + 20;
      
      this.setData({ safeTopPadding });
    } catch (error) {
      console.error('[About SafeArea] 适配失败�?, error);
      this.setData({ safeTopPadding: 120 });
    }
  },

  onShow() {
    // 每次显示时刷新用户信�?
    this.# removed
  },

  /**
   * 加载用户信息
   */
  load# removed
    const # removed
    this.setData({ # removed
  },

  /**
   * 微信登录
   */
  async handleLogin() {
    try {
      wx.showLoading({ title: '登录�?..' });

      // 调用微信登录
      await app.login();

      // 获取用户信息
      const # removed
      
      this.setData({ # removed
      
      wx.hideLoading();
      wx.showToast({
        title: '登录成功',
        icon: 'success'
      });
    } catch (err) {
      wx.hideLoading();
      console.error('登录失败:', err);
      
      if (err.errMsg && err.errMsg.includes('getUserProfile:fail auth deny')) {
        wx.showToast({
          title: '您取消了授权',
          icon: 'none'
        });
      } else {
        wx.showToast({
          title: '登录失败，请重试',
          icon: 'none'
        });
      }
    }
  },

  /**
   * 退出登�?
   */
  handleLogout() {
    wx.showModal({
      title: '提示',
      content: '确定退出登录吗�?,
      success: (res) => {
        if (res.confirm) {
          app.logout();
          this.setData({ # removed
          wx.showToast({
            title: '已退出登�?,
            icon: 'success'
          });
        }
      }
    });
  }
})
