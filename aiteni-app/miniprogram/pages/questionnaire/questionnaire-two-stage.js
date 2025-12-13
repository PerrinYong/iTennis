// pages/questionnaire/questionnaire.js - 两阶段评估实现
const api = require('../../utils/api');

Page({
  data: {
    questions: [],           // 当前阶段的问题列表
    currentIndex: 0,         // 当前问题索引
    answers: {},             // 当前阶段答案
    basicAnswers: {},        // 基础题答案（保存用于第二阶段）
    stage: 'basic',          // 当前阶段：'basic' 或 'advanced'
    progress: 0,             // 答题进度
    isSubmitting: false,     // 是否正在提交
    isLoading: true          // 是否正在加载
  },

  onLoad(options) {
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
   * 加载题目配置
   */
  async loadQuestions() {
    try {
      wx.showLoading({ title: '加载题目中...' });
      
      // 从缓存获取题目配置
      let questionsConfig = wx.getStorageSync('questions_config');
      
      if (!questionsConfig) {
        // 缓存中没有，从服务器获取
        const config = await api.questionnaire.getConfig();
        questionsConfig = config;
        // 缓存到本地
        wx.setStorageSync('questions_config', questionsConfig);
      }
      
      // 根据当前阶段筛选题目
      let filteredQuestions;
      if (this.data.stage === 'basic') {
        filteredQuestions = questionsConfig.basic_questions || [];
      } else {
        filteredQuestions = questionsConfig.advanced_questions || [];
      }
      
      this.setData({ 
        questions: filteredQuestions,
        progress: 0,
        isLoading: false
      });
      
      wx.hideLoading();
      
      if (filteredQuestions.length === 0) {
        wx.showModal({
          title: '提示',
          content: '暂无题目',
          showCancel: false,
          success: () => {
            wx.navigateBack();
          }
        });
      }
      
    } catch (error) {
      console.error('加载题目失败:', error);
      wx.hideLoading();
      wx.showModal({
        title: '加载失败',
        content: '题目加载失败，请重试',
        confirmText: '重试',
        cancelText: '返回',
        success: (res) => {
          if (res.confirm) {
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
    const { questionId, optionId } = e.currentTarget.dataset;
    
    this.setData({
      [`answers.${questionId}`]: optionId
    });
    
    // 更新进度
    this.updateProgress();
    
    // 保存答题进度（断点续答）
    this.saveProgress();
    
    // 自动跳到下一题
    setTimeout(() => {
      this.onNext();
    }, 300);
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
  onPrevious() {
    if (this.data.currentIndex > 0) {
      this.setData({
        currentIndex: this.data.currentIndex - 1
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
  onNext() {
    const { currentIndex, questions, answers } = this.data;
    const currentQuestion = questions[currentIndex];
    
    // 检查是否已回答当前题目
    if (!answers[currentQuestion.id]) {
      wx.showToast({
        title: '请先选择答案',
        icon: 'none'
      });
      return;
    }
    
    // 如果是最后一题，显示提交按钮提示
    if (currentIndex === questions.length - 1) {
      wx.showToast({
        title: '已完成所有题目，请点击提交',
        icon: 'none'
      });
      return;
    }
    
    this.setData({
      currentIndex: currentIndex + 1
    });
    
    // 滚动到顶部
    wx.pageScrollTo({
      scrollTop: 0,
      duration: 300
    });
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
      console.error('提交失败:', error);
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
    
    try {
      // 调用基础评估接口
      const result = await api.evaluation.evaluateBasic(answers);
      
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
              // 返回首页
              wx.switchTab({
                url: '/pages/welcome/welcome'
              });
            }
          }
        });
      } else {
        // 不需要进阶题，提交完整评估获取详细结果
        const fullResult = await api.evaluation.evaluateFull(answers);
        this.navigateToResult(fullResult);
      }
    } catch (error) {
      throw error;
    }
  },

  /**
   * 加载进阶题
   */
  async loadAdvancedQuestions() {
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
    
    try {
      // 调用完整评估接口
      const result = await api.evaluation.evaluateFull(allAnswers);
      
      // 跳转到结果页
      this.navigateToResult(result);
    } catch (error) {
      throw error;
    }
  },

  /**
   * 跳转到结果页
   */
  navigateToResult(result) {
    // 缓存结果
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
