# 图片资源说明

## 📋 登录页面所需图片

### default-avatar.png
- **用途**：登录页面的默认头像占位图
- **尺寸**：建议 200x200 像素或更高（保持正方形）
- **格式**：PNG（推荐，支持透明背景）或 JPG
- **位置**：`miniprogram/images/default-avatar.png`

### 如何添加默认头像

#### 方案一：使用网络图片（临时方案）
编辑 `pages/login/login.js`，修改默认头像路径为网络URL：
```javascript
data: {
  avatarUrl: 'https://your-cdn.com/default-avatar.png',
  // ...
}
```

#### 方案二：使用本地图片（推荐）
1. 准备一张正方形的头像图片
2. 重命名为 `default-avatar.png`
3. 放置到 `miniprogram/images/` 目录
4. 小程序会自动使用此图片

#### 方案三：使用emoji（最简单）
编辑 `pages/login/login.wxml`，直接用文字代替图片：
```html
<view class="avatar-placeholder">👤</view>
```

---

# TabBar 图标制作指南

## 📋 需要的图标文件

以下6个图标文件需要放在此目录：

```
images/
├── tab-home.png           # 首页-默认状态
├── tab-home-active.png    # 首页-选中状态
├── tab-history.png        # 记录-默认状态
├── tab-history-active.png # 记录-选中状态
├── tab-about.png          # 关于-默认状态
└── tab-about-active.png   # 关于-选中状态
```

## 🎨 设计规范

### 尺寸要求
- **推荐尺寸**: 81×81 px
- **格式**: PNG（支持透明背景）
- **文件大小**: 每个图标 < 40KB

### 颜色建议
- **默认状态**: #6B7280（中性灰）
- **选中状态**: #1D7CF2（品牌蓝色）

### 图标内容建议
1. **tab-home.png / tab-home-active.png**
   - 图标：网球拍 🎾 或房子 🏠
   - 简洁线条风格

2. **tab-history.png / tab-history-active.png**
   - 图标：时钟 🕐 或列表 📋
   - 表达"历史记录"概念

3. **tab-about.png / tab-about-active.png**
   - 图标：信息图标 ℹ️ 或齿轮 ⚙️
   - 表达"关于/设置"概念

## 🔧 快速生成图标

### 方法1: 使用在线工具
推荐使用 [Iconfont](https://www.iconfont.cn/) 或 [IconPark](https://iconpark.oceanengine.com/)：
1. 搜索相关图标
2. 下载 PNG 格式（81×81）
3. 使用图片编辑工具调整颜色
4. 导出两个版本（默认灰色 + 选中蓝色）

### 方法2: 使用 Figma/Sketch
1. 创建 81×81 画布
2. 绘制简单线条图标
3. 导出 PNG @2x（实际162×162，但命名为81×81）

### 方法3: 使用 AI 工具
提示词示例：
```
Create a minimalist line icon for a tennis app tab bar:
- Icon: tennis racket / clock / info symbol
- Size: 81x81 pixels
- Style: simple line art, 2px stroke
- Color: #6B7280 (gray) and #1D7CF2 (blue) versions
- Background: transparent
```

## 📝 添加图标后的配置

将6个图标文件放到此目录后，修改 `app.json`：

```json
"tabBar": {
  "color": "#6B7280",
  "selectedColor": "#1D7CF2",
  "backgroundColor": "#FFFFFF",
  "borderStyle": "black",
  "list": [
    {
      "pagePath": "pages/welcome/welcome",
      "text": "首页",
      "iconPath": "images/tab-home.png",
      "selectedIconPath": "images/tab-home-active.png"
    },
    {
      "pagePath": "pages/history/history",
      "text": "记录",
      "iconPath": "images/tab-history.png",
      "selectedIconPath": "images/tab-history-active.png"
    },
    {
      "pagePath": "pages/about/about",
      "text": "关于",
      "iconPath": "images/tab-about.png",
      "selectedIconPath": "images/tab-about-active.png"
    }
  ]
}
```

## ⚠️ 注意事项

1. **文件名必须完全匹配** app.json 中的配置
2. **路径是相对于 miniprogram 目录**的相对路径
3. **不能使用网络图片**，必须是本地文件
4. **图标会被微信自动缩放**，建议提供 @2x 或 @3x 清晰度
5. **iOS 和 Android 显示效果可能略有差异**

## 🎯 当前状态

**目前配置**: TabBar 仅显示文字，无图标
- ✅ 功能正常，可以正常切换页面
- ⚠️ 视觉效果简化，建议后续添加图标

**添加图标的优先级**: 中等
- 不影响核心功能
- 提升用户体验
- 建议在UI打磨阶段完成
