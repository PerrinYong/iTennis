// app.js
const api = require('./utils/api.js');

App({
  globalData: {
    userInfo: null,
    token: null,
    hasLogin: false
  },

  onLaunch: function () {
    console.log('[App] 小程序启动');
    // 检查登录状态
    this.checkLoginStatus();
  },

  /**
   * 检查登录状态
   */
  checkLoginStatus() {
    try {
      const token = wx.getStorageSync('token');
      const userInfo = wx.getStorageSync('userInfo');
      
      if (token && userInfo) {
        console.log('[App] 检测到本地Token，验证有效性');
        this.globalData.token = token;
        this.globalData.userInfo = userInfo;
        this.globalData.hasLogin = true;
        
        // 可选：验证Token是否仍然有效
        api.verifyToken().then(() => {
          console.log('[App] Token验证成功');
        }).catch(() => {
          console.log('[App] Token已失效，清除本地数据');
          this.logout();
        });
      } else {
        console.log('[App] 未检测到登录信息');
        this.globalData.hasLogin = false;
      }
    } catch (e) {
      console.error('[App] 检查登录状态失败:', e);
    }
  },

  /**
   * 检查是否需要登录
   * @returns {Boolean} 是否已登录
   */
  checkNeedLogin() {
    const token = wx.getStorageSync('token');
    if (!token) {
      wx.showModal({
        title: '需要登录',
        content: '请先登录后再使用',
        confirmText: '去登录',
        success: (res) => {
          if (res.confirm) {
            wx.redirectTo({
              url: '/pages/login/login'
            });
          }
        }
      });
      return false;
    }
    return true;
  },

  /**
   * 退出登录
   */
  logout() {
    console.log('[App] 用户退出登录');
    this.globalData.userInfo = null;
    this.globalData.token = null;
    this.globalData.hasLogin = false;
    wx.removeStorageSync('userInfo');
    wx.removeStorageSync('token');
    
    // 跳转到登录页
    wx.redirectTo({
      url: '/pages/login/login'
    });
  }
});
