// pages/history/history.js
const api = require('../../utils/api');

// 维度名称映射
const DIMENSION_NAMES = {
  baseline: '底线综合',
  forehand: '正手',
  backhand: '反手',
  serve: '发球',
  return: '接发球',
  net: '网前',
  footwork: '步伐',
  tactics: '战术',
  match_result: '实战',
  training: '训练'
}

Page({
  data: {
    history: [],
    loading: false,
    hasMore: true,
    page: 1,
    pageSize: 10,
    safeTopPadding: 20 // 页面容器顶部安全留白（rpx）
  },

  onLoad() {
    // 初始化安全区域适配
    this.initSafeArea();
    this.loadHistory();
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
      console.error('[History SafeArea] 适配失败：', error);
      this.setData({ safeTopPadding: 120 });
    }
  },

  onShow() {
    // 每次显示时刷新历史记录
    this.refreshHistory();
  },

  /**
   * 刷新历史记录（重新从第一页加载）
   */
  refreshHistory() {
    this.setData({
      history: [],
      page: 1,
      hasMore: true
    });
    this.loadHistory();
  },

  /**
   * 加载历史记录
   */
  async loadHistory() {
    if (this.data.loading || !this.data.hasMore) return;
    
    this.setData({ loading: true });
    
    try {
      console.log('[History] 从后端加载历史记录，页码:', this.data.page);
      
      const result = await api.getHistory(this.data.page, this.data.pageSize);
      
      console.log('[History] 加载成功:', result);
      
      const { records, total } = result;
      const processedRecords = records.map(item => this.processHistoryItem(item));
      
      this.setData({
        history: this.data.history.concat(processedRecords),
        page: this.data.page + 1,
        hasMore: this.data.history.length + processedRecords.length < total,
        loading: false
      });
      
    } catch (error) {
      console.error('[History] 加载失败:', error);
      
      // 如果是认证错误，提示登录
      if (error.code === 401) {
        wx.showModal({
          title: '需要登录',
          content: '请先登录后查看历史记录',
          confirmText: '去登录',
          success: (res) => {
            if (res.confirm) {
              wx.navigateTo({
                url: '/pages/login/login'
              });
            }
          }
        });
      } else {
        wx.showToast({
          title: '加载失败',
          icon: 'none'
        });
      }
      
      this.setData({ loading: false });
    }
  },

  /**
   * 处理历史记录项
   */
  processHistoryItem(item) {
    // 格式化日期
    const date = new Date(item.created_at);
    const dateText = this.formatDate(date);
    
    // 获取前3个维度
    const topDimensions = this.getTopDimensions(item.dimension_scores);
    
    return {
      id: item.id,
      rounded_level: item.rounded_level,
      level_label: item.level_label,
      dateText,
      topDimensions,
      // 保留完整数据供result页面使用
      ...item
    };
  },

  /**
   * 格式化日期
   */
  formatDate(date) {
    const now = new Date()
    const diff = now - date
    const days = Math.floor(diff / (1000 * 60 * 60 * 24))
    
    if (days === 0) {
      return '今天'
    } else if (days === 1) {
      return '昨天'
    } else if (days < 7) {
      return `${days}天前`
    } else {
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      return `${year}-${month}-${day}`
    }
  },

  /**
   * 获取前3个优势维度
   */
  getTopDimensions(dimensions) {
    if (!dimensions) return []
    
    const entries = Object.entries(dimensions)
    return entries
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([key]) => DIMENSION_NAMES[key] || key)
  },

  /**
   * 查看结果详情
   */
  viewResult(e) {
    const resultId = e.currentTarget.dataset.resultId;
    
    // 将选中的结果设置为最新结果（用于result页面读取）
    const selectedResult = this.data.history.find(item => item.id === resultId);
    
    if (selectedResult) {
      wx.setStorageSync('latest_result', selectedResult);
      wx.navigateTo({
        url: `/pages/result/result?recordId=${resultId}`
      });
    }
  },

  /**
   * 删除记录
   */
  async deleteRecord(e) {
    const recordId = e.currentTarget.dataset.resultId;
    
    wx.showModal({
      title: '确认删除',
      content: '确定要删除这条评估记录吗？',
      success: async (res) => {
        if (res.confirm) {
          try {
            wx.showLoading({ title: '删除中...' });
            
            await api.deleteResult(recordId);
            
            wx.hideLoading();
            wx.showToast({
              title: '删除成功',
              icon: 'success'
            });
            
            // 刷新列表
            this.refreshHistory();
            
          } catch (error) {
            wx.hideLoading();
            console.error('[History] 删除失败:', error);
            wx.showToast({
              title: '删除失败',
              icon: 'none'
            });
          }
        }
      }
    });
  },

  /**
   * 上拉加载更多
   */
  onReachBottom() {
    this.loadHistory();
  },

  /**
   * 下拉刷新
   */
  onPullDownRefresh() {
    this.refreshHistory();
    setTimeout(() => {
      wx.stopPullDownRefresh();
    }, 1000);
  },

  /**
   * 开始新评测
   */
  startTest() {
    wx.navigateTo({
      url: '/pages/questionnaire/questionnaire'
    })
  }
})
