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

// 默认头像
const defaultAvatarUrl = 'https://mmbiz.qpic.cn/mmbiz/icTdbqWNOwNRna42FI242Lcia07jQodd2FJGIYQfG0LAJGFxM4FbnQP6yfMxBgJ0F3YRqJCJ1aPAK2dQagdusBZg/0';

Page({
  data: {
    isLoading: true,
    safeTopPadding: 20, // 页面容器顶部安全留白（rpx）
    showDetail: false, // 是否显示详细版
    
    // 用户信息
    userInfo: null,

    // 评估结果数据
    result: null,
    resultId: null,
    
    // 分享相关
    showSharePreview: false,
    shareImage: '',
    isGeneratingImage: false
  },

  onLoad(options) {
    // 初始化安全区域适配
    this.initSafeArea();

    // 获取用户信息
    const userInfo = wx.getStorageSync('userInfo') || null;
    this.setData({ userInfo });

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
        const recordId = latestResult.record_id || null;
        
        this.setData({
          result: processedResult,
          isLoading: false,
          resultId: recordId
        });
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
    
    console.log('[Result] 后端返回的advantages:', rawResult.advantages);
    console.log('[Result] 后端返回的weaknesses:', rawResult.weaknesses);
    
    // 将后端返回的优势/短板数组转换为UI需要的格式
    // 如果后端没有返回，则从dimension_scores中计算
    let advantages = [];
    let weaknesses = [];
    
    if (rawResult.advantages && rawResult.advantages.length > 0) {
      // 使用后端返回的优势列表
      advantages = rawResult.advantages.map(dim => ({
        name: DIMENSION_NAMES[dim] || dim,
        score: (dimensionScores[dim] || overallLevel).toFixed(1),
        description: dimensionComments[dim] || this.getAdvantageDescription(dim, dimensionScores[dim] || overallLevel)
      }));
    } else {
      // 从维度分数中计算优势（降低阈值到0.2）
      const entries = Object.entries(dimensionScores);
      advantages = entries
        .filter(([key, value]) => value >= overallLevel + 0.2)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 3)
        .map(([key, value]) => ({
          name: DIMENSION_NAMES[key] || key,
          score: value.toFixed(1),
          description: dimensionComments[key] || this.getAdvantageDescription(key, value)
        }));
      
      // 如果仍然没有优势，则选择分数最高的3个维度
      if (advantages.length === 0) {
        advantages = entries
          .sort((a, b) => b[1] - a[1])
          .slice(0, 3)
          .map(([key, value]) => ({
            name: DIMENSION_NAMES[key] || key,
            score: value.toFixed(1),
            description: dimensionComments[key] || this.getAdvantageDescription(key, value)
          }));
      }
    }
    
    if (rawResult.weaknesses && rawResult.weaknesses.length > 0) {
      // 使用后端返回的短板列表
      weaknesses = rawResult.weaknesses.map(dim => ({
        name: DIMENSION_NAMES[dim] || dim,
        score: (dimensionScores[dim] || overallLevel).toFixed(1),
        description: dimensionComments[dim] || this.getWeaknessDescription(dim, dimensionScores[dim] || overallLevel)
      }));
    } else {
      // 从维度分数中计算短板（降低阈值到0.2）
      const entries = Object.entries(dimensionScores);
      weaknesses = entries
        .filter(([key, value]) => value < overallLevel - 0.2)
        .sort((a, b) => a[1] - b[1])
        .slice(0, 3)
        .map(([key, value]) => ({
          name: DIMENSION_NAMES[key] || key,
          score: value.toFixed(1),
          description: dimensionComments[key] || this.getWeaknessDescription(key, value)
        }));
      
      // 如果仍然没有短板，则选择分数最低的3个维度
      if (weaknesses.length === 0) {
        weaknesses = entries
          .sort((a, b) => a[1] - b[1])
          .slice(0, 3)
          .map(([key, value]) => ({
            name: DIMENSION_NAMES[key] || key,
            score: value.toFixed(1),
            description: dimensionComments[key] || this.getWeaknessDescription(key, value)
          }));
      }
    }
    
    console.log('[Result] 处理后的advantages:', advantages);
    console.log('[Result] 处理后的weaknesses:', weaknesses);
    
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
   * 切换显示详细版/简略版
   */
  toggleDetail() {
    this.setData({
      showDetail: !this.data.showDetail
    });
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
   * 生成分享图片
   */
  async onShareImage() {
    if (this.data.shareImage) {
      this.setData({ showSharePreview: true });
      return;
    }

    this.setData({ isGeneratingImage: true });
    wx.showLoading({
      title: '生成海报中...',
    });

    // === 获取二维码 ===
    let qrCodePath = null;
    try {
      const qrPath = this.data.resultId ? `pages/result/result?resultId=${this.data.resultId}` : 'pages/welcome/welcome';
      
      // 判断环境 (简单的环境判断，生产环境使用域名，开发环境使用IP)
      const { miniProgram } = wx.getAccountInfoSync();
      const API_BASE = (miniProgram.envVersion === 'release') 
        ? 'https://perrin-minigame.cloud/api' 
        : 'http://182.92.109.59/api';

      qrCodePath = await new Promise((resolve) => {
        wx.request({
          url: `${API_BASE}/generate_qrcode`,
          method: 'POST',
          data: { path: qrPath, width: 200 },
          responseType: 'arraybuffer',
          success: (res) => {
            if (res.statusCode === 200) {
              const fs = wx.getFileSystemManager();
              const filePath = `${wx.env.USER_DATA_PATH}/share_qrcode.jpg`;
              fs.writeFile({
                filePath,
                data: res.data,
                encoding: 'binary',
                success: () => resolve(filePath),
                fail: (e) => {
                    console.error('写入二维码文件失败', e);
                    resolve(null);
                }
              });
            } else {
              console.error('获取二维码API失败', res);
              resolve(null);
            }
          },
          fail: (e) => {
            console.error('请求二维码接口失败', e);
            resolve(null);
          }
        });
      });
    } catch (e) {
      console.error('二维码流程异常', e);
    }

    const query = wx.createSelectorQuery();
    query.select('#shareCanvas')
      .fields({ node: true, size: true })
      .exec((res) => {
        if (!res || !res[0]) {
            wx.hideLoading();
            this.setData({ isGeneratingImage: false });
            wx.showToast({ title: 'Canvas初始化失败', icon: 'none' });
            return;
        }
        
        const canvas = res[0].node;
        const ctx = canvas.getContext('2d');
        const dpr = wx.getSystemInfoSync().pixelRatio;
        
        // 设置画布尺寸
        canvas.width = res[0].width * dpr;
        canvas.height = res[0].height * dpr;
        ctx.scale(dpr, dpr);
        
        // 绘制内容 (改为异步调用)
        this.drawShareContent(ctx, canvas, res[0].width, res[0].height, qrCodePath)
          .then(() => {
             // 导出图片
             wx.canvasToTempFilePath({
               canvas: canvas,
               success: (res) => {
                 wx.hideLoading();
                 this.setData({
                   shareImage: res.tempFilePath,
                   showSharePreview: true,
                   isGeneratingImage: false
                 });
               },
               fail: (err) => {
                 wx.hideLoading();
                 this.setData({ isGeneratingImage: false });
                 console.error('生成图片失败', err);
                 wx.showToast({ title: '生成失败', icon: 'none' });
               }
             });
          });
      });
  },

  /**
   * 绘制海报内容
   */
  async drawShareContent(ctx, canvas, width, height, qrCodePath) {
    const { result } = this.data;
    if (!result) return;

    // 清空
    ctx.clearRect(0, 0, width, height);

    // === 目标：尽可能复刻 result 简略版的视觉 ===
    // 设计基准（canvas 使用 px）
    const P = 16; // 外边距
    const gap = 14;
    const cardW = width - P * 2;

    // 背景（对应页面灰底）
    ctx.fillStyle = '#F5F7FA';
    ctx.fillRect(0, 0, width, height);

    let y = P;

    // === 用户信息 Header ===
    const headerH = 64;
    await this.drawUserHeader(ctx, canvas, P, y, cardW, headerH);
    y += headerH + gap;

    // Hero 卡
    const heroH = 190;
    this.drawPosterHero(ctx, P, y, cardW, heroH, result);
    y += heroH + gap;

    // 优势卡（简略）- 只显示前2条以留出底部空间
    y = this.drawPosterListCard(ctx, P, y, cardW, {
      icon: '💪',
      title: '你的主要优势',
      dotColor: '#1FA27A',
      rows: (result.advantages || []).slice(0, 2),
      rowIcon: '🎾',
      rowIconBg: 'rgba(31, 162, 122, 0.15)',
      rowIconColor: '#1FA27A',
      chipBg: 'rgba(29, 124, 242, 0.10)',
      chipColor: '#1D7CF2'
    });
    y += gap;

    // 短板卡（简略）- 只显示前2条以留出底部空间
    y = this.drawPosterListCard(ctx, P, y, cardW, {
      icon: '🎯',
      title: '当前最值得优先提升的环节',
      dotColor: '#F97316',
      rows: (result.weaknesses || []).slice(0, 2),
      rowIcon: '🎯',
      rowIconBg: 'rgba(249, 115, 22, 0.12)',
      rowIconColor: '#F97316',
      chipBg: 'rgba(249, 115, 22, 0.12)',
      chipColor: '#F97316'
    });

    // === 绘制底部 Footer (Logo + Slogan + QR) ===
    await this.drawFooter(ctx, canvas, width, height, qrCodePath);
    
    return true;
  },

  /**
   * 绘制用户 Header (头像 + 昵称 + Title)
   */
  async drawUserHeader(ctx, canvas, x, y, w, h) {
    const { userInfo } = this.data;
    const avatarUrl = userInfo?.avatarUrl || defaultAvatarUrl;
    const nickName = userInfo?.nickName || '网球爱好者';

    // 背景：白色圆角矩形
    ctx.save();
    ctx.shadowColor = 'rgba(15, 23, 42, 0.06)';
    ctx.shadowBlur = 12;
    ctx.shadowOffsetY = 4;
    this.fillRoundRect(ctx, x, y, w, h, h / 2, '#FFFFFF');
    ctx.restore();

    // 1. 绘制头像
    const padding = 8; // 头像距离边缘的内边距
    const avatarSize = h - padding * 2; 
    const avatarX = x + padding;
    const avatarY = y + padding;

    try {
      // 创建图片对象
      const img = canvas.createImage();
      await new Promise((resolve) => {
        img.onload = resolve;
        img.onerror = (e) => {
            console.error('Avatar load error', e); 
            resolve(); 
        };
        img.src = avatarUrl;
      });

      // 绘制圆形头像
      ctx.save();
      ctx.beginPath();
      ctx.arc(avatarX + avatarSize / 2, avatarY + avatarSize / 2, avatarSize / 2, 0, Math.PI * 2);
      ctx.clip();
      ctx.drawImage(img, avatarX, avatarY, avatarSize, avatarSize);
      ctx.restore();

    } catch (e) {
      console.error('Draw avatar failed', e);
      // 失败兜底：绘制灰色圆形
      ctx.fillStyle = '#F0F2F5';
      ctx.beginPath();
      ctx.arc(avatarX + avatarSize / 2, avatarY + avatarSize / 2, avatarSize / 2, 0, Math.PI * 2);
      ctx.fill();
    }

    // 2. 绘制文本
    const textX = avatarX + avatarSize + 12;
    const centerY = y + h / 2;

    // 昵称
    ctx.textAlign = 'left';
    ctx.textBaseline = 'bottom';
    ctx.font = 'bold 18px sans-serif';
    ctx.fillStyle = '#1F2933';
    ctx.fillText(nickName, textX, centerY - 2);

    // Title
    ctx.textBaseline = 'top';
    ctx.font = '13px sans-serif';
    ctx.fillStyle = '#616E7C';
    ctx.fillText('网球等级报告', textX, centerY + 2);
  },

  /**
   * 绘制底部 Footer
   */
  async drawFooter(ctx, canvas, width, height, qrCodePath) {
    const footerH = 120;
    const y = height - footerH;
    
    // 背景
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, y, width, footerH);
    
    // 顶部分割线（可选，太细可能看不清，这里用淡淡的阴影替代）
    ctx.save();
    ctx.shadowColor = 'rgba(0,0,0,0.03)';
    ctx.shadowBlur = 10;
    ctx.shadowOffsetY = -2;
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, y, width, 2); // 仅为了产生向上阴影
    ctx.restore();

    // === 左侧品牌信息 ===
    const leftP = 24;
    let textY = y + 40;
    
    // LOGO/标题
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillStyle = '#1F2933';
    ctx.font = 'bold 24px sans-serif';
    ctx.fillText('AiTeni', leftP, textY);
    
    // 智能网球评测
    textY += 32;
    ctx.fillStyle = '#3E4C59';
    ctx.font = '15px sans-serif';
    ctx.fillText('智能网球评测系统', leftP, textY);
    
    // 数据声明
    textY += 24;
    ctx.fillStyle = '#9AA5B1';
    ctx.font = '12px sans-serif';
    ctx.fillText('数据仅供训练参考', leftP, textY);

    // === 右侧二维码 ===
    if (qrCodePath) {
      try {
        const qrSize = 80;
        const qrX = width - 24 - qrSize;
        const qrY = y + (footerH - qrSize) / 2; // 垂直居中

        const img = canvas.createImage();
        
        await new Promise((resolve, reject) => {
           img.onload = resolve;
           img.onerror = (e) => { console.error('二维码加载失败', e); resolve(); }; // 失败不阻断
           img.src = qrCodePath;
        });

        // 绘制二维码
        ctx.drawImage(img, qrX, qrY, qrSize, qrSize);
        
        // 扫码提示文字 (仅当二维码绘制成功时绘制)
        ctx.textAlign = 'center';
        ctx.fillStyle = '#616E7C';
        ctx.font = '10px sans-serif';
        ctx.textBaseline = 'top'; // 确保垂直对齐一致
        ctx.fillText('长按识别', qrX + qrSize / 2, qrY + qrSize + 8);

      } catch (e) {
        console.error('绘制二维码失败', e);
      }
    }
  },

  /**
   * 海报：Hero 卡（尽量贴近 result 简略版 hero）
   */
  drawPosterHero(ctx, x, y, w, h, result) {
    // 渐变背景
    const g = ctx.createLinearGradient(x, y, x + w, y + h);
    g.addColorStop(0, '#4DA4FF');
    g.addColorStop(0.45, '#1D7CF2');
    g.addColorStop(1, '#2A8CFF');

    // 阴影
    ctx.save();
    ctx.shadowColor = 'rgba(15, 23, 42, 0.16)';
    ctx.shadowBlur = 18;
    ctx.shadowOffsetY = 10;
    this.fillRoundRect(ctx, x, y, w, h, 18, g);
    ctx.restore();

    // 装饰球阴影
    ctx.save();
    ctx.globalAlpha = 0.18;
    const ballG = ctx.createRadialGradient(x + w - 60, y + 40, 10, x + w - 60, y + 40, 120);
    ballG.addColorStop(0, '#FFEFA3');
    ballG.addColorStop(0.55, '#FFD84A');
    ballG.addColorStop(1, '#F4C938');
    ctx.fillStyle = ballG;
    ctx.beginPath();
    ctx.arc(x + w - 40, y + 30, 110, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // 左侧文案
    const leftX = x + 18;
    const topY = y + 18;
    ctx.textAlign = 'left';
    ctx.textBaseline = 'top';
    ctx.fillStyle = '#FFFFFF';
    ctx.font = 'bold 28px sans-serif';
    ctx.fillText(`NTRP ${result.overallLevel}`, leftX, topY);

    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
    ctx.font = '14px sans-serif';
    ctx.fillText(result.levelLabel || '', leftX, topY + 36);

    // 优势标签 chips（最多 3）
    const chips = (result.advantageTags || []).slice(0, 3);
    let chipX = leftX;
    const chipY = topY + 64;
    chips.forEach((t) => {
      const text = String(t || '');
      ctx.font = '12px sans-serif';
      const tw = ctx.measureText(text).width;
      const cw = tw + 18;
      this.fillRoundRect(ctx, chipX, chipY, cw, 22, 11, 'rgba(255, 255, 255, 0.18)');
      ctx.fillStyle = '#EFF6FF';
      ctx.textBaseline = 'middle';
      ctx.fillText(text, chipX + 9, chipY + 11);
      chipX += cw + 8;
    });

    // 注释
    ctx.textBaseline = 'top';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';
    ctx.font = '12px sans-serif';
    ctx.fillText('数据基于你的问卷作答，仅供训练参考。', leftX, topY + 96);

    // 右侧等级徽章
    const badgeSize = 86;
    const bx = x + w - badgeSize - 18;
    const by = y + 24;
    ctx.save();
    ctx.shadowColor = 'rgba(180, 137, 0, 0.35)';
    ctx.shadowBlur = 16;
    ctx.shadowOffsetY = 8;
    this.fillRoundRect(ctx, bx, by, badgeSize, badgeSize, badgeSize / 2, '#FFD84A');
    ctx.restore();

    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillStyle = '#1F2933';
    ctx.font = 'bold 22px sans-serif';
    ctx.fillText(String(result.overallLevel), bx + badgeSize / 2, by + badgeSize / 2 - 6);
    ctx.font = 'bold 10px sans-serif';
    ctx.fillText('NTRP', bx + badgeSize / 2, by + badgeSize / 2 + 16);
  },

  /**
   * 海报：列表卡片（尽量贴近简略版“优势/短板”卡）
   */
  drawPosterListCard(ctx, x, y, w, config) {
    const headerH = 54;
    const rowH = 52;
    const rows = (config.rows || []);
    const listCount = Math.max(rows.length, 1);
    const h = headerH + listCount * rowH + 16;

    // 卡片背景 + 阴影
    ctx.save();
    ctx.shadowColor = 'rgba(15, 23, 42, 0.08)';
    ctx.shadowBlur = 18;
    ctx.shadowOffsetY = 10;
    this.fillRoundRect(ctx, x, y, w, h, 18, '#FFFFFF');
    ctx.restore();

    // header
    ctx.textAlign = 'left';
    ctx.textBaseline = 'middle';
    ctx.font = 'bold 16px sans-serif';
    ctx.fillStyle = '#1F2933';
    ctx.fillText(`${config.icon}  ${config.title}`, x + 16, y + 28);

    // status dot
    ctx.fillStyle = config.dotColor;
    ctx.beginPath();
    ctx.arc(x + w - 18, y + 28, 5, 0, Math.PI * 2);
    ctx.fill();

    // rows
    let cy = y + headerH;
    if (rows.length === 0) {
      ctx.fillStyle = '#6B7280';
      ctx.font = '13px sans-serif';
      ctx.textBaseline = 'middle';
      ctx.fillText('各维度发展较为均衡', x + 16, cy + rowH / 2);
      return y + h;
    }

    rows.forEach((item, idx) => {
      // divider
      if (idx > 0) {
        ctx.fillStyle = '#E5E7EB';
        ctx.fillRect(x + 16, cy, w - 32, 1);
      }

      const rowTop = cy + 1;
      const iconSize = 28;
      const iconX = x + 16;
      const iconY = rowTop + (rowH - iconSize) / 2;
      this.fillRoundRect(ctx, iconX, iconY, iconSize, iconSize, iconSize / 2, config.rowIconBg);
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = config.rowIconColor;
      ctx.font = '16px sans-serif';
      ctx.fillText(config.rowIcon, iconX + iconSize / 2, iconY + iconSize / 2);

      // name
      ctx.textAlign = 'left';
      ctx.fillStyle = '#1F2933';
      ctx.font = '14px sans-serif';
      const name = this.truncateText(ctx, String(item.name || ''), w - 32 - iconSize - 90);
      const nameX = iconX + iconSize + 12;
      const nameY = rowTop + rowH / 2;
      ctx.fillText(name, nameX, nameY);

      // chip score
      const score = `${item.score} 级`;
      ctx.font = '12px sans-serif';
      const sw = ctx.measureText(score).width + 16;
      const sh = 20;
      const sx = x + w - 16 - sw;
      const sy = rowTop + (rowH - sh) / 2;
      this.fillRoundRect(ctx, sx, sy, sw, sh, 10, config.chipBg);
      ctx.fillStyle = config.chipColor;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(score, sx + sw / 2, sy + sh / 2);

      cy += rowH;
    });

    return y + h;
  },

  /**
   * 省略号截断
   */
  truncateText(ctx, text, maxWidth) {
    if (ctx.measureText(text).width <= maxWidth) return text;
    let t = text;
    while (t.length > 0 && ctx.measureText(`${t}…`).width > maxWidth) {
      t = t.slice(0, -1);
    }
    return `${t}…`;
  },

  /**
   * 填充圆角矩形
   */
  fillRoundRect(ctx, x, y, w, h, r, fillStyle) {
    ctx.save();
    ctx.fillStyle = fillStyle;
    this.roundRect(ctx, x, y, w, h, r);
    ctx.fill();
    ctx.restore();
  },

  /**
   * 关闭分享预览
   */
  closeSharePreview() {
    this.setData({ showSharePreview: false });
  },

  /**
   * 保存图片到相册
   */
  saveImageToPhotos() {
    if (!this.data.shareImage) return;
    
    wx.saveImageToPhotosAlbum({
      filePath: this.data.shareImage,
      success: () => {
        wx.showToast({
          title: '已保存到相册',
          icon: 'success'
        });
      },
      fail: (err) => {
        console.error('保存图片失败', err);
        if (err.errMsg.includes('auth')) {
          wx.showModal({
            title: '提示',
            content: '需要保存到相册权限，请在设置中开启',
            success: (res) => {
              if (res.confirm) {
                wx.openSetting();
              }
            }
          });
        } else {
          wx.showToast({ title: '保存失败', icon: 'none' });
        }
      }
    });
  },

  /**
   * 调用微信原生分享（分享给朋友）
   */
  shareToFriend() {
    // 提示用户使用原生分享功能（部分场景下无法直接拉起，需引导）
    // 或者利用 button open-type="share"，这里我们已经在WXML中使用了 open-type="share" 的按钮
    // 如果是自定义逻辑，可以使用 wx.showShareMenu
  },

  /**
   * 朋友圈分享提示
   */
  shareToTimeline() {
    // 小程序无法直接“发图片到朋友圈”，最符合微信习惯的是：预览图片 -> 微信里分享 / 或保存后去朋友圈选择图片
    if (!this.data.shareImage) return;
    wx.previewImage({
      urls: [this.data.shareImage],
      current: this.data.shareImage
    });
  },

  /**
   * 预览分享图片（利用微信原生预览页：可转发/保存/朋友圈）
   */
  previewShareImage() {
    if (!this.data.shareImage) return;
    wx.previewImage({
      urls: [this.data.shareImage],
      current: this.data.shareImage
    });
  },

  /**
   * 绘制圆角矩形
   */
  roundRect(ctx, x, y, w, h, r) {
    if (w < 2 * r) r = w / 2
    if (h < 2 * r) r = h / 2
    ctx.beginPath()
    ctx.moveTo(x + r, y)
    ctx.arcTo(x + w, y, x + w, y + h, r)
    ctx.arcTo(x + w, y + h, x, y + h, r)
    ctx.arcTo(x, y + h, x, y, r)
    ctx.arcTo(x, y, x + w, y, r)
    ctx.closePath()
  },

  /**
   * 保存 Canvas 为图片 (已集成在生成逻辑中，此方法废弃或改为仅保存到相册)
   */
  saveCanvasToImage(canvas) {
    // 逻辑已移至 onShareImage 中的 canvasToTempFilePath 回调
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
