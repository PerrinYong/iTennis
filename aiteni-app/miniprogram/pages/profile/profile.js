// pages/profile/profile.js
const api = require('../../utils/api');

Page({
  data: {
    userInfo: null,
    isLoggedIn: false,
    loading: false,
    safeTopPadding: 20
  },

  onLoad() {
    this.initSafeArea();
  },

  onShow() {
    this.checkLoginStatus();
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
      console.error('[Profile SafeArea] 适配失败：', error);
      this.setData({ safeTopPadding: 120 });
    }
  },

  /**
   * 检查登录状态
   */
  async checkLoginStatus() {
    const token = wx.getStorageSync('token');
    
    if (!token) {
      this.setData({ isLoggedIn: false, userInfo: null });
      return;
    }

    try {
      this.setData({ loading: true });
      
      // 从本地存储获取用户信息
      const userInfo = wx.getStorageSync('userInfo');
      
      if (userInfo) {
        this.setData({
          isLoggedIn: true,
          userInfo: userInfo,
          loading: false
        });
      } else {
        // 如果本地没有，可以调用后端API获取
        this.setData({ isLoggedIn: false, loading: false });
      }
    } catch (error) {
      console.error('[Profile] 获取用户信息失败:', error);
      this.setData({ isLoggedIn: false, loading: false });
    }
  },

  /**
   * 去登录
   */
  goToLogin() {
    wx.navigateTo({
      url: '/pages/login/login'
    });
  },

  /**
   * 查看我的历史记录
   */
  goToHistory() {
    if (!this.data.isLoggedIn) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      });
      return;
    }
    wx.switchTab({
      url: '/pages/history/history'
    });
  },

  /**
   * 退出登录
   */
  handleLogout() {
    wx.showModal({
      title: '提示',
      content: '确定退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          // 清除登录信息
          wx.removeStorageSync('token');
          wx.removeStorageSync('userInfo');
          
          this.setData({
            isLoggedIn: false,
            userInfo: null
          });
          
          wx.showToast({
            title: '已退出登录',
            icon: 'success'
          });
        }
      }
    });
  }
});
