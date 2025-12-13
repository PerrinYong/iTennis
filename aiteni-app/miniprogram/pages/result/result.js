// pages/result/result.js

// 维度名称映射
const DIMENSION_NAMES = {
  baseline: '底线综合',
  forehand: '正手',
  backhand: '反手',
  serve: '发球',
  return: '接发球',
  net: '网前与高压',
  footwork: '步伐与场地覆盖',
  tactics: '战术与心理',
  match_result: '实战成绩',
  training: '训练背景'
}

Page({
  data: {
    isLoading: true,
    safeTopPadding: 20, // 页面容器顶部安全留白（rpx）
    
    // 评估结果数据
    result: null,
    resultId: null
  },

  onLoad(options) {
    // 初始化安全区域适配
    this.initSafeArea();
    // 加载评估结果
    if (options.resultId) {
      this.setData({ resultId: options.resultId })
      this.loadResult(options.resultId)
    } else {
      // 加载最新的评估结果
      this.loadLatestResult()
    }
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
      console.error('[Result SafeArea] 适配失败：', error);
      this.setData({ safeTopPadding: 120 });
    }
  },

  /**
   * 加载评估结果
   */
  async loadResult(resultId) {
    try {
      this.setData({ isLoading: true })

      // TODO: 从后端API或本地存储获取结果
      const result = await this.fetchResult(resultId)
      
      // 处理结果数据
      const processedResult = this.processResult(result)

      this.setData({
        result: processedResult,
        isLoading: false
      })
    } catch (error) {
      console.error('加载结果失败:', error)
      wx.showToast({
        title: '加载失败',
        icon: 'none'
      })
    }
  },

  /**
   * 加载最新的评估结果
   */
  loadLatestResult() {
    try {
      const latestResult = wx.getStorageSync('latest_result')
      if (latestResult) {
        const processedResult = this.processResult(latestResult)
        this.setData({
          result: processedResult,
          isLoading: false
        })
      } else {
        wx.showToast({
          title: '没有找到评估结果',
          icon: 'none'
        })
        setTimeout(() => {
          wx.switchTab({
            url: '/pages/welcome/welcome'
          })
        }, 1500)
      }
    } catch (e) {
      console.error('加载最新结果失败:', e)
    }
  },

  /**
   * 从API获取结果
   */
  async fetchResult(resultId) {
    // TODO: 实际API调用
    await new Promise(resolve => setTimeout(resolve, 500))
    
    return wx.getStorageSync('latest_result')
  },

  /**
   * 处理结果数据，生成UI所需的数据结构
   */
  processResult(rawResult) {
    console.log('[Result] 处理评估结果:', rawResult);
    
    // 后端返回的数据结构：
    // - total_level: 最终等级
    // - rounded_level: 四舍五入等级
    // - level_label: 等级标签
    // - dimension_scores: 维度分数
    // - dimension_comments: 维度评语
    // - advantages: 优势列表（维度名称数组）
    // - weaknesses: 短板列表（维度名称数组）
    // - summary_text: 总结文本
    
    const overallLevel = rawResult.rounded_level || rawResult.total_level || 3.5;
    const dimensionScores = rawResult.dimension_scores || {};
    const dimensionComments = rawResult.dimension_comments || {};
    
    // 将后端返回的优势/短板数组转换为UI需要的格式
    const advantages = (rawResult.advantages || []).map(dim => ({
      name: DIMENSION_NAMES[dim] || dim,
      score: (dimensionScores[dim] || overallLevel).toFixed(1),
      description: dimensionComments[dim] || `${DIMENSION_NAMES[dim] || dim}是您的优势项目`
    }));
    
    const weaknesses = (rawResult.weaknesses || []).map(dim => ({
      name: DIMENSION_NAMES[dim] || dim,
      score: (dimensionScores[dim] || overallLevel).toFixed(1),
      description: dimensionComments[dim] || `${DIMENSION_NAMES[dim] || dim}有提升空间`
    }));
    
    // 直接使用后端返回的数据
    const result = {
      overallLevel: overallLevel,
      levelLabel: rawResult.level_label || `NTRP ${overallLevel}`,
      dimensions: dimensionScores,
      dimensionComments: dimensionComments,
      advantages: advantages,
      weaknesses: weaknesses,
      summaryText: rawResult.summary_text || '',
      
      // 为UI生成额外的数据
      advantageTags: this.generateAdvantageTags(rawResult),
      dimensionDetails: this.generateDimensionDetails(rawResult)
    };
    
    console.log('[Result] 处理后的结果:', result);
    return result;
  },

  /**
   * 生成优势标签（简短）- 基于后端返回的advantages
   */
  generateAdvantageTags(result) {
    const advantages = result.advantages || [];
    // 直接使用后端返回的优势维度，转换为中文名称
    return advantages.slice(0, 3).map(dim => DIMENSION_NAMES[dim] || dim);
  },

  /**
   * 生成优势列表（详细）
   */
  generateAdvantages(result) {
    const { dimensions, overallLevel } = result
    const entries = Object.entries(dimensions || {})
    
    // 筛选高于平均水平的维度
    const advantages = entries
      .filter(([key, value]) => value >= overallLevel + 0.2)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([key, value]) => ({
        name: DIMENSION_NAMES[key] || key,
        score: value.toFixed(1),
        description: this.getAdvantageDescription(key, value)
      }))
    
    return advantages
  },

  /**
   * 生成短板列表
   */
  generateWeaknesses(result) {
    const { dimensions, overallLevel } = result
    const entries = Object.entries(dimensions || {})
    
    // 筛选低于平均水平的维度
    const weaknesses = entries
      .filter(([key, value]) => value < overallLevel - 0.2)
      .sort((a, b) => a[1] - b[1])
      .slice(0, 2)
      .map(([key, value]) => ({
        name: DIMENSION_NAMES[key] || key,
        score: value.toFixed(1),
        description: this.getWeaknessDescription(key, value)
      }))
    
    return weaknesses
  },

  /**
   * 生成维度详情列表 - 基于后端返回的dimension_scores和dimension_comments
   */
  generateDimensionDetails(result) {
    const dimensions = result.dimension_scores || {};
    const dimensionComments = result.dimension_comments || {};
    const overallLevel = result.rounded_level || result.total_level || 3.5;
    const entries = Object.entries(dimensions);
    
    return entries.map(([key, value], index) => {
      const diff = value - overallLevel;
      let tagClass, tagText, subtitle;
      
      if (diff >= 0.3) {
        tagClass = 'tag-strong';
        tagText = '优势';
        subtitle = '可以作为主要得分手段';
      } else if (diff <= -0.3) {
        tagClass = 'tag-weak';
        tagText = '短板';
        subtitle = '有提升空间';
      } else {
        tagClass = 'tag-balance';
        tagText = '均衡';
        subtitle = '符合整体水平';
      }
      
      return {
        name: DIMENSION_NAMES[key] || key,
        score: value.toFixed(1),
        subtitle,
        tagClass,
        tagText,
        detail: dimensionComments[key] || this.getDimensionDetail(key, value),
        expanded: index === 0 // 默认展开第一个
      };
    });
  },

  /**
   * 获取优势描述
   */
  getAdvantageDescription(dimension, score) {
    const descriptions = {
      forehand: '正手已经是你的核心武器之一，在中速节奏的多拍相持中，击球质量稳定，能够主动压制对手，为自己创造进攻机会。',
      footwork: '基本步伐移动积极，能较快回位并覆盖大部分场地，在对抗中不容易被简单拉空位，具备较好的防守和救球能力。',
      tactics: '对比分、节奏有一定意识，能够根据对手特点调整出球路线，情绪波动相对可控，不容易一局失误后完全崩盘。',
      net: '网前已经具备一定威胁，可以针对低球截击、反手截击和连续截击做专项训练，让你在合适机会时更有把握通过一两拍结束这一分。'
    }
    
    return descriptions[dimension] || `${DIMENSION_NAMES[dimension]}是你的优势项目，表现出色。`
  },

  /**
   * 获取短板描述
   */
  getWeaknessDescription(dimension, score) {
    const descriptions = {
      serve: '一发威胁有限，二发更多是"保守推过去"，在关键分容易被对手主动抢攻，建议优先提升发球稳定性和落点变化。',
      baseline: '在被拉开、被压迫时失误率偏高，防守质量不足，经常在"多拍拼稳定"中率先失误，建议强化防守球和相持球的安全容错。'
    }
    
    return descriptions[dimension] || `${DIMENSION_NAMES[dimension]}有提升空间，建议加强针对性练习。`
  },

  /**
   * 获取维度详细说明
   */
  getDimensionDetail(dimension, score) {
    const details = {
      forehand: '正手击球动作相对完整，基本节奏下的稳定性较好，能够主动压制对手。接下来可以重点练习：\n· 在不同落点（对角 / 直线）之间切换，而不是只盯一个区域；\n· 在有余力的球上增加"前冲"和"下压"，逐步形成真正的进攻球；\n· 用正手在 1~2 拍内主动抢攻对方弱点，建立属于自己的王牌套路。',
      backhand: '反手在被攻击时偏向"挡回去"，整体可靠，但主动性有限。可以通过固定节奏的多拍训练，逐步增加反手的击球质量和线路控制，不需要立刻变成武器，但要尽量避免成为明显漏洞。',
      serve: '一发速度尚可，但落点不够明确；二发偏保守，容易被对手抢攻。建议先确立"最稳的一发套路"（比如上旋偏安全的外角球），再逐步练习不同落点组合，让你的发球局不再只是"勉强开球"，而是能真正建立优势。',
      footwork: '你愿意主动动脚，并且有一定的回位速度，这让你在相持中具备不错的防守下限。如果希望继续提升，可以增加"小碎步调整"和"启动第一步"的训练，让你在面对更快节奏时依然可以保持稳定击球姿态。'
    }
    
    return details[dimension] || `${DIMENSION_NAMES[dimension]}的详细分析和建议。`
  },

  /**
   * 切换维度展开/收起
   */
  toggleDimension(e) {
    const index = e.currentTarget.dataset.index
    const key = `result.dimensionDetails[${index}].expanded`
    const currentValue = this.data.result.dimensionDetails[index].expanded
    
    this.setData({
      [key]: !currentValue
    })
  },

  /**
   * 查看训练建议
   */
  getTrainingPlan() {
    wx.showToast({
      title: '功能开发中',
      icon: 'none'
    })
    
    // TODO: 导航到训练建议页面
    // wx.navigateTo({
    //   url: `/pages/training/training?resultId=${this.data.resultId}`
    // })
  },

  /**
   * 分享结果
   */
  shareResult() {
    // 小程序分享功能需要在onShareAppMessage中实现
    wx.showToast({
      title: '请点击右上角分享',
      icon: 'none'
    })
  },

  /**
   * 返回
   */
  goBack() {
    wx.switchTab({
      url: '/pages/welcome/welcome'
    })
  },

  /**
   * 分享配置
   */
  onShareAppMessage() {
    const { result } = this.data
    return {
      title: `我的NTRP等级是${result.overallLevel}，快来测测你的网球水平！`,
      path: '/pages/welcome/welcome',
      imageUrl: '' // TODO: 生成分享图片
    }
  }
})
