/**
 * Markdown渲染工具
 * 用于将简单的Markdown语法（如 **粗体**）转换为富文本HTML
 * 
 * 由于微信小程序WXSS不支持深度选择器（>>>），
 * 我们使用内联样式来实现高亮效果
 */

const { debug } = require('./debug');

// 普通状态下的高亮样式 - 现代化的荧光笔效果（下半部分高亮）
// 这种设计既醒目又不会遮挡文字，看起来更有设计感
const normalStyle = 'background: linear-gradient(transparent 60%, rgba(255, 214, 10, 0.3) 60%); font-weight: 700; padding: 0 4rpx; color: inherit;';

// 选中状态下的高亮样式 - 保持一致，仅稍微加深一点底色以适应选中态的视觉重心
// 用户反馈不需要明显变化，所以去掉了反色设计
const selectedStyle = 'background: linear-gradient(transparent 60%, rgba(255, 214, 10, 0.4) 60%); font-weight: 700; padding: 0 4rpx; color: inherit;';

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
  
  return options.map((option, index) => {
    const isSelected = option.id === selectedOptionId;
    const htmlText = renderMarkdown(option.text, isSelected);
    
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
