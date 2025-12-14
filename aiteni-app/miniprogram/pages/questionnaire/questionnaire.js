// pages/questionnaire/questionnaire.js - 两阶段评估实现
const api = require('../../utils/api');

Page({
  data: {
    questions: [],           // 当前阶段的问题列表
    currentIndex: 0,         // 当前问题索引
    currentQuestion: null,   // 当前显示的问题
    answers: {},             // 当前阶段答案
    basicAnswers: {},        // 基础题答案（保存用于第二阶段）
    stage: 'basic',          // 当前阶段：'basic' 或 'advanced'
    progress: 0,             // 答题进度
    isSubmitting: false,     // 是否正在提交
    isLoading: true,         // 是否正在加载
    selectedAnswer: '',      // 当前选中的答案
    currentQuestionTier: '', // 当前题目类型（basic/advanced）
    safeTopPadding: 0        // 顶部安全留白
  },

  onLoad(options) {
    // 初始化安全区域
    this.initSafeArea();

    // 获取阶段参数
    const stage = options.stage || 'basic';
    this.setData({ stage });
    
    // 加载题目
    this.loadQuestions();
    
    // 尝试恢复答题进度
    if (stage === 'basic') {
      this.restoreProgress();
    }
  },

  /**
   * 初始化安全区域适配
   */
  initSafeArea() {
    try {
      const systemInfo = wx.getSystemInfoSync();
      const menuButton = wx.getMenuButtonBoundingClientRect();
      
      // 计算顶部留白：胶囊按钮底部 + 12px 间距
      // 如果获取不到胶囊信息（极少数情况），使用状态栏 + 44px
      let topPx = 0;
      if (menuButton && menuButton.bottom) {
        topPx = menuButton.bottom + 12;
      } else {
        topPx = (systemInfo.statusBarHeight || 20) + 44 + 12;
      }

      // 转换为rpx
      const pixelRatio = 750 / systemInfo.windowWidth;
      const safeTopPadding = topPx * pixelRatio;
      
      this.setData({ safeTopPadding });
    } catch (e) {
      console.error('计算安全区域失败', e);
      this.setData({ safeTopPadding: 160 }); // 兜底值
    }
  },

  /**
   * 加载题目配置
   */
  async loadQuestions() {
    console.log('[问卷页] 开始加载题目，当前阶段:', this.data.stage);
    
    try {
      wx.showLoading({ title: '加载题目中...' });
      
      // 从缓存获取题目配置
      let questionsConfig = wx.getStorageSync('questions_config');
      console.log('[问卷页] 缓存中的题目配置:', questionsConfig ? '存在' : '不存在');
      
      if (!questionsConfig) {
        console.log('[问卷页] 从服务器获取题目配置...');
        // 缓存中没有，从服务器获取
        const config = await api.questionnaire.getConfig();
        console.log('[问卷页] 服务器返回的配置:', config);
        questionsConfig = config;
        // 缓存到本地
        wx.setStorageSync('questions_config', questionsConfig);
        console.log('[问卷页] 题目配置已缓存');
      }
      
      // 检查配置是否有效
      if (!questionsConfig || typeof questionsConfig !== 'object') {
        throw new Error('题目配置格式错误');
      }
      
      // 根据当前阶段筛选题目
      let filteredQuestions;
      if (this.data.stage === 'basic') {
        filteredQuestions = questionsConfig.basic_questions || [];
        console.log('[问卷页] 基础题数量:', filteredQuestions.length);
      } else {
        filteredQuestions = questionsConfig.advanced_questions || [];
        console.log('[问卷页] 进阶题数量:', filteredQuestions.length);
      }
      
      // 打印题目详情（仅第一题）
      if (filteredQuestions.length > 0) {
        console.log('[问卷页] 第一题示例:', {
          id: filteredQuestions[0].id,
          text: filteredQuestions[0].text?.substring(0, 30) + '...',
          optionCount: filteredQuestions[0].options?.length
        });
      }
      
      this.setData({ 
        questions: filteredQuestions,
        progress: 0,
        isLoading: false
      });
      
      // 设置第一题
      if (filteredQuestions.length > 0) {
        this.updateCurrentQuestion();
      }
      
      wx.hideLoading();
      
      if (filteredQuestions.length === 0) {
        console.warn('[问卷页] 警告：题目列表为空');
        wx.showModal({
          title: '题目加载失败',
          content: `未找到${this.data.stage === 'basic' ? '基础' : '进阶'}题目。\n\n可能原因：\n1. 服务器配置未正确设置\n2. 题目配置文件格式错误\n3. 网络连接问题`,
          showCancel: true,
          confirmText: '重试',
          cancelText: '返回',
          success: (res) => {
            if (res.confirm) {
              // 清除缓存后重试
              wx.removeStorageSync('questions_config');
              this.loadQuestions();
            } else {
              wx.navigateBack();
            }
          }
        });
      } else {
        console.log('[问卷页] 题目加载成功');
      }
      
    } catch (error) {
      console.error('[问卷页] 加载题目失败，错误详情:', error);
      console.error('[问卷页] 错误堆栈:', error.stack);
      
      wx.hideLoading();
      
      // 构建详细错误信息
      let errorMsg = '题目加载失败';
      if (error.message) {
        errorMsg += '：' + error.message;
      }
      if (error.errMsg) {
        errorMsg += '\n' + error.errMsg;
      }
      
      wx.showModal({
        title: '加载失败',
        content: errorMsg + '\n\n建议：\n1. 检查网络连接\n2. 确认服务器运行正常\n3. 联系技术支持',
        confirmText: '重试',
        cancelText: '返回',
        success: (res) => {
          if (res.confirm) {
            // 清除缓存后重试
            wx.removeStorageSync('questions_config');
            this.loadQuestions();
          } else {
            wx.navigateBack();
          }
        }
      });
    }
  },

  /**
   * 恢复答题进度
   */
  restoreProgress() {
    const savedAnswers = wx.getStorageSync('current_answers');
    const savedStage = wx.getStorageSync('current_stage');
    
    if (savedAnswers && savedStage === this.data.stage) {
      this.setData({
        answers: savedAnswers
      });
      this.updateProgress();
    }
  },

  /**
   * 选择答案
   */
  onSelectOption(e) {
    const { optionId } = e.currentTarget.dataset;
    const { currentQuestion, currentIndex } = this.data;
    
    console.log('[问卷页] 选择答案:', optionId);
    
    this.setData({
      selectedAnswer: optionId,
      [`answers.${currentQuestion.id}`]: optionId
    });
    
    // 更新进度
    this.updateProgress();
    
    // 保存答题进度（断点续答）
    this.saveProgress();
  },
  
  /**
   * 更新当前显示的问题
   */
  updateCurrentQuestion() {
    const { questions, currentIndex, answers } = this.data;
    
    if (currentIndex >= 0 && currentIndex < questions.length) {
      const currentQuestion = questions[currentIndex];
      const selectedAnswer = answers[currentQuestion.id] || '';
      const currentQuestionTier = currentQuestion.question_tier || 'basic';
      
      console.log('[问卷页] 切换到题目:', currentIndex + 1, '/', questions.length, '类型:', currentQuestionTier);
      
      this.setData({
        currentQuestion,
        selectedAnswer,
        currentQuestionTier,
        isLastQuestion: currentIndex === questions.length - 1
      });
    }
  },

  /**
   * 更新答题进度
   */
  updateProgress() {
    const { questions, answers } = this.data;
    const answeredCount = Object.keys(answers).length;
    const progress = Math.floor((answeredCount / questions.length) * 100);
    
    this.setData({ progress });
  },

  /**
   * 保存答题进度
   */
  saveProgress() {
    wx.setStorageSync('current_answers', this.data.answers);
    wx.setStorageSync('current_stage', this.data.stage);
  },

  /**
   * 上一题
   */
  prevQuestion() {
    if (this.data.currentIndex > 0) {
      this.setData({
        currentIndex: this.data.currentIndex - 1
      }, () => {
        this.updateCurrentQuestion();
      });
      
      // 滚动到顶部
      wx.pageScrollTo({
        scrollTop: 0,
        duration: 300
      });
    }
  },

  /**
   * 下一题
   */
  nextQuestion() {
    const { currentIndex, questions, selectedAnswer, isLastQuestion } = this.data;
    
    // 检查是否已选择答案
    if (!selectedAnswer) {
      wx.showToast({
        title: '请先选择答案',
        icon: 'none'
      });
      return;
    }
    
    // 如果是最后一题，提交
    if (isLastQuestion) {
      this.onSubmit();
      return;
    }
    
    // 否则跳转到下一题
    this.setData({
      currentIndex: currentIndex + 1
    }, () => {
      this.updateCurrentQuestion();
    });
    
    // 滚动到顶部
    wx.pageScrollTo({
      scrollTop: 0,
      duration: 300
    });
  },
  
  /**
   * 选择选项（兼容旧的事件名）
   */
  selectOption(e) {
    this.onSelectOption(e);
  },

  /**
   * 提交答案
   */
  async onSubmit() {
    const { questions, answers, stage } = this.data;
    
    // 验证是否所有题目都已回答
    const unansweredQuestions = questions.filter(q => !answers[q.id]);
    if (unansweredQuestions.length > 0) {
      wx.showModal({
        title: '还有题目未回答',
        content: `还有 ${unansweredQuestions.length} 道题目未回答，是否继续提交？`,
        success: (res) => {
          if (res.confirm) {
            this.submitAnswers();
          }
        }
      });
    } else {
      this.submitAnswers();
    }
  },

  /**
   * 执行提交
   */
  async submitAnswers() {
    if (this.data.isSubmitting) return;
    
    this.setData({ isSubmitting: true });
    wx.showLoading({ title: '评估中...' });
    
    try {
      if (this.data.stage === 'basic') {
        // 第一阶段：提交基础题
        await this.submitBasicStage();
      } else {
        // 第二阶段：提交完整答案
        await this.submitAdvancedStage();
      }
    } catch (error) {
      console.error('[问卷页] 提交失败:', error);
      wx.showModal({
        title: '提交失败',
        content: '网络连接失败，请检查网络后重试',
        confirmText: '重试',
        success: (res) => {
          if (res.confirm) {
            this.submitAnswers();
          }
        }
      });
    } finally {
      this.setData({ isSubmitting: false });
      wx.hideLoading();
    }
  },

  /**
   * 提交基础题阶段
   */
  async submitBasicStage() {
    const { answers } = this.data;
    
    console.log('[问卷页] 提交基础题，答案数量:', Object.keys(answers).length);
    
    try {
      // 调用基础评估接口
      const result = await api.evaluation.evaluateBasic(answers);
      
      console.log('[问卷页] 基础评估结果:', result);
      
      // 保存基础题答案，用于后续合并
      this.setData({ basicAnswers: answers });
      wx.setStorageSync('basic_answers', answers);
      
      // 判断是否需要进阶题
      if (result.need_advanced) {
        // 需要进阶题
        wx.showModal({
          title: '继续进阶评估',
          content: `您的初步水平约为 NTRP ${result.rounded_level}。为了获得更准确的评估结果，建议继续完成进阶题目。`,
          confirmText: '继续',
          cancelText: '稍后再说',
          success: (res) => {
            if (res.confirm) {
              // 继续进阶题
              this.loadAdvancedQuestions();
            } else {
              // 用户取消，使用基础评估结果跳转到结果页
              this.navigateToResult(result);
            }
          }
        });
      } else {
        // 水平较低，不需要进阶题，直接使用基础评估结果
        console.log('[问卷页] 水平较低，直接使用基础评估结果');
        this.navigateToResult(result);
      }
    } catch (error) {
      throw error;
    }
  },

  /**
   * 加载进阶题
   */
  async loadAdvancedQuestions() {
    console.log('[问卷页] 切换到进阶题阶段');
    
    this.setData({
      stage: 'advanced',
      currentIndex: 0,
      answers: {},
      progress: 0,
      isLoading: true
    });
    
    await this.loadQuestions();
    
    wx.showToast({
      title: '已进入进阶评估',
      icon: 'success'
    });
  },

  /**
   * 提交进阶题阶段
   */
  async submitAdvancedStage() {
    // 合并基础题和进阶题答案
    const basicAnswers = this.data.basicAnswers || wx.getStorageSync('basic_answers') || {};
    const advancedAnswers = this.data.answers;
    
    const allAnswers = {
      ...basicAnswers,
      ...advancedAnswers
    };
    
    console.log('[问卷页] 提交完整答案，数量:', Object.keys(allAnswers).length);
    
    try {
      // 调用完整评估接口
      const result = await api.evaluation.evaluateFull(allAnswers);
      
      console.log('[问卷页] 完整评估结果:', result);
      
      // 跳转到结果页
      this.navigateToResult(result);
    } catch (error) {
      throw error;
    }
  },

  /**
   * 跳转到结果页
   */
  async navigateToResult(result) {
    console.log('[问卷页] 跳转到结果页');
    
    // 获取完整答案
    const answers = this.data.stage === 'basic' 
      ? this.data.answers 
      : {
          ...(this.data.basicAnswers || wx.getStorageSync('basic_answers') || {}),
          ...this.data.answers
        };
    
    // 保存到后端
    try {
      console.log('[问卷页] 保存评估记录到后端');
      const saveResult = await api.saveEvaluation(answers, result);
      console.log('[问卷页] 保存成功:', saveResult);
      
      // 将record_id附加到result中
      result.record_id = saveResult.record_id;
    } catch (error) {
      console.error('[问卷页] 保存到后端失败:', error);
      // 即使保存失败也继续显示结果
    }
    
    // 缓存结果（供result页面使用）
    wx.setStorageSync('latest_result', result);
    
    // 清除答题进度
    wx.removeStorageSync('current_answers');
    wx.removeStorageSync('current_stage');
    wx.removeStorageSync('basic_answers');
    
    // 跳转到结果页
    wx.redirectTo({
      url: '/pages/result/result'
    });
  },

  /**
   * 退出评测
   */
  onExit() {
    wx.showModal({
      title: '确认退出',
      content: '答题进度将会保存，下次可以继续',
      success: (res) => {
        if (res.confirm) {
          // 保存进度后返回
          this.saveProgress();
          wx.navigateBack();
        }
      }
    });
  }
});
