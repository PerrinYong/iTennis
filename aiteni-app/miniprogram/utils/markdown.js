/**
 * Markdown渲染工具
 * 用于将简单的Markdown语法（如 **粗体**）转换为富文本HTML
 * 
 * 由于微信小程序WXSS不支持深度选择器（>>>），
 * 我们使用内联样式来实现高亮效果
 */

const { debug } = require('./debug');

// 普通状态下的高亮样式
const normalStyle = 'background: rgba(255, 216, 74, 0.28); border-radius: 6rpx; padding: 2rpx 8rpx; font-weight: 650;';

// 选中状态下的高亮样式
const selectedStyle = 'background: rgba(29, 124, 242, 0.15); color: #1D7CF2; border-radius: 6rpx; padding: 2rpx 8rpx; font-weight: 700;';

/**
 * 渲染Markdown文本为HTML
 * @param {string} text - 原始文本，可能包含 **粗体** 标记
 * @param {boolean} isSelected - 是否为选中状态
 * @returns {string} 渲染后的HTML字符串
 */
function renderMarkdown(text, isSelected = false) {
  if (!text) return '';
  
  const style = isSelected ? selectedStyle : normalStyle;
  
  // 将 **text** 转换为 <span style="...">text</span>
  const renderedHtml = text.replace(/\*\*([^*]+)\*\*/g, `<span style="${style}">$1</span>`);
  
  debug('markdown', `渲染Markdown: "${text.substring(0, 30)}..." -> "${renderedHtml.substring(0, 50)}..."`, `选中状态: ${isSelected}`);
  
  return renderedHtml;
}

/**
 * 批量处理选项文本，为每个选项渲染HTML
 * @param {Array} options - 选项数组，每个选项包含 id 和 text 字段
 * @param {string} selectedOptionId - 当前选中的选项ID
 * @returns {Array} 处理后的选项数组，每个选项增加 htmlText 字段
 */
function renderOptionsText(options, selectedOptionId = '') {
  if (!Array.isArray(options)) {
    debug('markdown', '警告：传入的options不是数组', typeof options);
    return [];
  }
  
  debug('markdown', `处理 ${options.length} 个选项，选中ID: ${selectedOptionId}`);
  
  return options.map((option, index) => {
    const isSelected = option.id === selectedOptionId;
    const htmlText = renderMarkdown(option.text, isSelected);
    
    if (index === 0) {
      // 打印第一个选项的详细信息用于调试
      debug('markdown', '第一个选项:', {
        id: option.id,
        isSelected,
        原始文本预览: option.text.substring(0, 50) + '...',
        HTML预览: htmlText.substring(0, 50) + '...',
        包含粗体标记: option.text.includes('**')
      });
    }
    
    return {
      ...option,
      htmlText
    };
  });
}

module.exports = {
  renderMarkdown,
  renderOptionsText
};

