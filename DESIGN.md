---
name: E-commerce Market Research Agent
description: 让研究输入与可复核初稿并列的本地工作台
colors:
  bg: "#f5f7fc"
  surface: "#ffffff"
  surface-muted: "#eef4f7"
  ink: "#1f2933"
  muted: "#566176"
  line: "#cfd9df"
  accent: "#405aca"
  accent-dark: "#30449e"
  accent-soft: "#e5eafb"
  warn: "#8a5a00"
  warn-surface: "#fff8e7"
  secondary-hover: "#e2ecef"
typography:
  body:
    fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
  headline:
    fontSize: "32px"
    lineHeight: 1.12
    letterSpacing: "0em"
  title:
    fontSize: "18px"
    lineHeight: 1.3
  input:
    fontSize: "16px"
    lineHeight: 1.45
  label:
    fontSize: "13px"
    fontWeight: 700
rounded:
  control: "8px"
  section-control: "6px"
spacing:
  page: "24px"
  panel: "18px"
  field: "12px"
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.surface}"
    rounded: "{rounded.control}"
    padding: "0 14px"
  button-primary-hover:
    backgroundColor: "{colors.accent-dark}"
  button-secondary:
    backgroundColor: "{colors.surface-muted}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "0 14px"
---

# Design System: E-commerce Market Research Agent

## Overview

**Creative North Star: "可复核的研究桌"**

浅灰蓝背景、白色双栏与蓝色主动作组织输入和初稿。密度服务于研究人员核对材料，装饰保持安静。当前工作台没有点阵或大型渐变装饰，后续页面无需为了统一而添加。

规则依据 web/styles.css、web/index.html 与 web/app.js。界面中的本地分析说明和虚构数据性质是持续约束，不是可删除的多余注释。

## Colors

Accent 为当前蓝色动作，accent-dark 用于 hover 和报告分节。Neutral 提供背景、工作面、表头与边界；warn 配合错误文字。样式文件中的历史 teal 注释不代表当前配色。

## Typography

正文使用本机无衬线栈；Inter 未在此样式中自托管。主标题在 560px 以下变为 26px；报告标题为 28px，正文行高 1.58。竞品 CSV 输入保留 Cascadia Mono / Consolas 回退，字号为 16px，区别于普通输入。

主副标题与字段标签分工清楚，不把技术说明铺满输入区。长报告保留标题、段落、列表和表格层级。

## Layout

整体最大宽度 1440px，常规外边距 24px。双栏按 0.82:1.18 分配，最小轨道分别为 360px 和 480px，栏距 18px。980px 以下转为单列并缩小到 16px 外边距；560px 以下动作纵向排列并占满宽度。

产品问题输入最小高 290px，CSV 输入最小高 180px；报告面保持独立滚动及长词换行，宽表格可横向滚动。空状态留出真实报告工作面，不填充装饰数据。

## Elevation & Depth

两块主工作面使用细边框，内部依靠分隔线与留白。按钮背景与阴影过渡为 160ms ease-out，按下位移 1px；reduced-motion 关闭过渡和动画。

## Shapes

主工作面、字段和按钮共用 control 圆角。输入背景略区别于纯白工作面，边框表达可编辑范围。表格是直线结构，不将每个单元格变成独立卡片。

## Components

- 主动作、辅助按钮、分区与引用按钮最小高度为 44px。
- 文本域 focus 使用浅蓝外圈和蓝边框；按钮及链接有独立 focus-visible 轮廓。禁用控件降低透明度并显示不可用指针。
- 加载示例和生成有实际 busy 状态；复制、下载仅在当前输入对应有效结果时可用，编辑材料后旧结果不能继续导出。
- CSV 格式说明按需展开；报告区域支持真实错误、空状态与生成结果。样例始终标明虚构。

## Do's and Don'ts

- **Do** 让输入材料与研究初稿直接对应，明确下一步验证任务。
- **Do** 保留可复核表格与数据错误文字，使用克制的蓝灰层次。
- **Don't** 用无依据市场数据、假进度、间隔点或重复帮助文案填充页面。
- **Don't** 从样式声明推导全站对比度或触控尺寸已经通过认证。

## 0.3 研究复核

结果按 Summary、Next actions、Evidence 分区，用普通按钮及 aria-pressed 表达当前视图。输入保留左侧，宽屏结果独立滚动并保留导出操作；移动端单列，完成分析后滚动到结果。引用按钮进入具体原始记录并聚焦展开项。

CSV 导入与示例替换均可撤销。输入变化显示旧结果提示，导出禁用；没有结果时隐藏导出动作。证据使用浏览器原生 details 和定义列表。空价格显示 Not provided，不显示零。表格类遗留样式仅供旧报告内容，不影响当前结构化复核。

新增复核标题为 21px，正文为 16px；辅助文本为 14px，使用数值的区域启用 tabular-nums。沿用本机字体栈保证离线，无外部字体请求。当前字体选择服务于操作型界面的可读性，没有将其描述为独特品牌字体。
