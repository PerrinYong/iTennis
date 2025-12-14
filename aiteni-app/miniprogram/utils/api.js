/**
 * API 接口工具
 * 封装所有后端API调用
 */

const CONFIG = {
  // 后端API地址
  // 本地开发环境
  BASE_URL: "http://182.92.109.59/api",
  
  // 生产环境（已部署SSL证书）
  // BASE_URL: 'https://perrin-minigame.cloud/api',
  
  TIMEOUT: 30000 // 请求超时时间（毫秒）- 增加到30秒，因为需要调用微信接口
}

/**
 * 通用请求方法
 */
function request(options) {
  const { url, method = 'GET', data = {}, needAuth = true } = options
  const fullUrl = `${CONFIG.BASE_URL}${url}`;
  
  console.log(`[API] 发起请求: ${method} ${fullUrl}`);
  if (method !== 'GET' && Object.keys(data).length > 0) {
    console.log('[API] 请求数据:', data);
  }

  return new Promise((resolve, reject) => {
    // 构建请求头
    const header = {
      'Content-Type': 'application/json'
    }

    // 添加认证token
    if (needAuth) {
      const token = wx.getStorageSync('token')
      if (token) {
        header['Authorization'] = `Bearer ${token}`
      }
    }

    wx.request({
      url: fullUrl,
      method,
      data,
      header,
      timeout: CONFIG.TIMEOUT,
      enableHttp2: false,      // 禁用HTTP2
      enableQuic: false,        // 禁用QUIC
      enableCache: false,       // 禁用缓存
      success: (res) => {
        const { statusCode, data } = res
        console.log(`[API] 响应状态: ${statusCode}`);
        console.log('[API] 响应数据:', data);

        // 处理HTTP状态码
        if (statusCode >= 200 && statusCode < 300) {
          // 处理业务状态码
          if (data.code === 200) {
            console.log('[API] 请求成功');
            resolve(data.data)
          } else {
            // 业务错误
            console.error('[API] 业务错误:', data.errorMsg || '未知错误');
            wx.showToast({
              title: data.errorMsg || '操作失败',
              icon: 'none'
            })
            reject(data)
          }
        } else if (statusCode === 401) {
          // 未授权，清除token并跳转到登录
          console.warn('[API] 未授权，需要重新登录');
          wx.removeStorageSync('token')
          wx.showToast({
            title: '请重新登录',
            icon: 'none'
          })
          // TODO: 跳转到登录页
          reject(data)
        } else {
          // HTTP错误
          console.error(`[API] HTTP错误: ${statusCode}`);
          wx.showToast({
            title: `请求失败 (${statusCode})`,
            icon: 'none'
          })
          reject(data)
        }
      },
      fail: (err) => {
        console.error('[API] 请求失败:', err)
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        })
        reject(err)
      }
    })
  })
}

/**
 * 用户认证相关API
 */
const authAPI = {
  /**
   * 微信登录
   * @param {Object} data - 登录数据 {code, avatarUrl, nickName}
   */
  wxLogin(data) {
    return request({
      url: '/auth/login',
      method: 'POST',
      data: data,
      needAuth: false
    })
  },

  /**
   * 验证Token
   */
  verifyToken() {
    return request({
      url: '/auth/verify',
      method: 'POST',
      needAuth: true
    })
  }
}

/**
 * 问卷配置相关API
 */
const questionnaireAPI = {
  /**
   * 获取问卷配置
   */
  getConfig() {
    return request({
      url: '/evaluation/questions',
      method: 'GET',
      needAuth: false
    })
  },

  /**
   * 获取维度配置
   */
  getDimensions() {
    return request({
      url: '/evaluation/config',
      method: 'GET',
      needAuth: false
    })
  }
}

/**
 * 评估相关API
 */
const evaluationAPI = {
  /**
   * 提交基础题评测（第一阶段）
   * @param {Object} answers - 基础题答案
   * @returns {Promise} 包含初步等级和是否需要进阶题
   */
  evaluateBasic(answers) {
    return request({
      url: '/evaluation/basic',
      method: 'POST',
      data: { answers },
      needAuth: false
    })
  },

  /**
   * 提交完整评测（第二阶段或直接完整评测）
   * @param {Object} answers - 所有题目答案
   * @returns {Promise} 完整评估结果
   */
  evaluateFull(answers) {
    return request({
      url: '/evaluation/full',
      method: 'POST',
      data: { answers },
      needAuth: false
    })
  },

  /**
   * 提交评测答案（兼容旧接口）
   */
  submit(answers) {
    return this.evaluateFull(answers)
  },

  /**
   * 提交评测答案（兼容旧接口）
   */
  submit(answers) {
    return this.evaluateFull(answers)
  },

  /**
   * 获取评测结果
   */
  getResult(resultId) {
    return request({
      url: `/evaluation/result/${resultId}`,
      method: 'GET'
    })
  },

  /**
   * 获取评测历史
   */
  getHistory(page = 1, pageSize = 10) {
    return request({
      url: '/evaluation/history',
      method: 'GET',
      data: { page, pageSize }
    })
  },

  /**
   * 删除评测记录
   */
  deleteResult(resultId) {
    return request({
      url: `/evaluation/result/${resultId}`,
      method: 'DELETE'
    })
  }
}

/**
 * 训练建议相关API
 */
const trainingAPI = {
  /**
   * 获取训练计划
   */
  getPlan(resultId) {
    return request({
      url: `/training/plan/${resultId}`,
      method: 'GET'
    })
  }
}

// 导出所有API
module.exports = {
  // 认证相关
  wechatLogin: authAPI.wxLogin,
  verifyToken: authAPI.verifyToken,
  
  // 问卷和评估相关（保持向后兼容）
  auth: authAPI,
  questionnaire: questionnaireAPI,
  evaluation: evaluationAPI,
  training: trainingAPI,
  
  // 直接导出评估方法（简化调用）
  getQuestions: questionnaireAPI.getConfig,
  getDimensions: questionnaireAPI.getDimensions,
  evaluateBasic: evaluationAPI.evaluateBasic,
  evaluateFull: evaluationAPI.evaluateFull,
  getResult: evaluationAPI.getResult,
  getHistory: evaluationAPI.getHistory,
  deleteResult: evaluationAPI.deleteResult
}
