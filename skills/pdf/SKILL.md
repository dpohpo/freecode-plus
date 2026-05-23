# PDF Professional Report Generator

> **生成专业PDF报告的技能包**
>
> 核心能力：固定布局、打印优化、跨设备一致性、专业排版

---

## 技能概述

生成符合出版和商业标准的PDF报告，确保跨设备完美呈现和打印质量。

**适用场景**：
- 正式商业报告
- 合同和法律文件
- 学术论文
- 年度/季度报告
- 需要打印归档的文档

---

## 核心设计原则

### 1. 页面布局规范

```latex
% LaTeX 文档类设置
\documentclass[12pt,a4paper]{article}

% 页面边距（符合中文排版规范）
\usepackage[top=2.5cm,bottom=2.5cm,left=2cm,right=2cm]{geometry}

% 页眉页脚
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small 报告标题}
\fancyhead[R]{\small \today}
\fancyfoot[C]{\small 第\thepage页}
```

**中文排版规范**：
- 页边距：上下2.5cm，左右2cm
- 正文：12pt（小四号字）
- 行距：1.5倍
- 段落间距：段前0行，段后0.5行

### 2. 字体系统

```python
# 字体配置（中英文）
FONTS = {
    # 标题字体
    'heading_cn': 'Source Han Serif CN',  # 思源宋体
    'heading_en': 'Crimson Pro',           # Crimson Pro

    # 正文字体
    'body_cn': 'Source Han Sans CN',      # 思源黑体
    'body_en': 'Source Sans Pro',         # Source Sans Pro

    # 等宽字体
    'mono': 'Source Code Pro',            # Source Code Pro

    # 字号规范
    'h1': 22,       # 一级标题
    'h2': 18,       # 二级标题
    'h3': 16,       # 三级标题
    'body': 12,     # 正文
    'caption': 10,  # 图表说明
}
```

### 3. 配色方案

```css
/* PDF专用配色（考虑打印） */
:root {
  /* 主色调 - 打印友好 */
  --color-primary: #1a1a1a;
  --color-secondary: #4a4a4a;

  /* 强调色 - 适中饱和度 */
  --color-accent-blue: #2563eb;
  --color-accent-green: #059669;
  --color-accent-orange: #ea580c;

  /* 灰度 - 确保对比度 */
  --gray-900: #1a1a1a;
  --gray-700: #4a4a4a;
  --gray-500: #7a7a7a;
  --gray-300: #d4d4d4;
  --gray-100: #f5f5f5;

  /* 背景色 */
  --bg-white: #ffffff;
  --bg-light: #fafafa;
}
```

---

## PDF文档模板

### LaTeX 模板（学术/正式报告）

```latex
\documentclass[12pt,a4paper]{report}

% 中文支持
\usepackage[UTF8]{ctex}

% 页面设置
\usepackage[top=2.5cm,bottom=2.5cm,left=2cm,right=2cm]{geometry}
\usepackage{parskip} % 段落间距

% 字体和编码
\usepackage[T1]{fontenc}
\usepackage{fontspec}
\setmainfont{Source Han Serif CN}
\setsansfont{Source Han Sans CN}
\setmonofont{Source Code Pro}

% 图表支持
\usepackage{graphicx}
\usepackage{float}
\usepackage{caption}
\usepackage{subcaption}

% 表格支持
\usepackage{booktabs} % 优质表格线
\usepackage{longtable}
\usepackage{array}
\usepackage{colortbl}

% 颜色支持
\usepackage{xcolor}
\definecolor{primary}{HTML}{1a1a1a}
\definecolor{accent}{HTML}{2563eb}

% 链接
\usepackage[hidelinks]{hyperref}

% 页眉页脚
\usepackage{fancyhdr}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small \leftmark}
\fancyhead[R]{\small \today}
\fancyfoot[C]{\small 第\thepage页}

% 文档信息
\title{\textbf{报告标题}}
\subtitle{副标题}
\author{作者名称}
\date{\today}

\begin{document}

% 封面
\maketitle

% 目录
\tableofcontents
\newpage

% 正文
\chapter{引言}
\section{背景}
这里是正文内容...

\section{目标}
更多内容...

\chapter{数据分析}
\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\textwidth]{chart.png}
    \caption{图表标题}
    \label{fig:chart}
\end{figure}

% 参考文献
\bibliographystyle{plain}
\bibliography{references}

\end{document}
```

### Markdown + Pandoc 模板

````markdown
---
title: "报告标题"
subtitle: "副标题"
author: "作者名称"
date: "2025-01-10"
geometry: "top=2.5cm,bottom=2.5cm,left=2cm,right=2cm"
fontfamily: "sourcesanspro"
font-size: "12pt"
linestretch: "1.5"
linkcolor: "blue"
urlcolor: "blue"
citecolor: "blue"
toc: true
toc-depth: 3
numbersections: true
---

# 执行摘要

这里是报告的执行摘要部分...

## 关键发现

- 要点一
- 要点二
- 要点三

# 数据分析

## 图表展示

![图表标题](chart.png){ width=80% }

## 数据表格

| 指标 | Q1 | Q2 | Q3 | Q4 |
|------|----|----|----|-----|
| 收入 | 100万 | 120万 | 150万 | 180万 |
| 增长 | - | +20% | +25% | +20% |

# 结论

基于以上分析...
````

---

## 图表设计规范

### 表格样式

```latex
% 专业表格（三线表）
\begin{table}[H]
    \centering
    \caption{数据对比表}
    \begin{tabular}{llcc}
        \toprule
        指标 & 说明 & 2024年 & 2025年 \\
        \midrule
        收入 & 总营收 & ¥1,000万 & ¥1,200万 \\
        增长率 & 同比增长 & - & +20\% \\
        利润 & 净利润 & ¥200万 & ¥280万 \\
        \bottomrule
    \end{tabular}
\end{table}
```

### 图表插入

```latex
% 单图
\begin{figure}[H]
    \centering
    \includegraphics[width=0.8\textwidth]{figures/chart1.pdf}
    \caption{收入趋势图}
    \label{fig:revenue}
\end{figure}

% 双图并排
\begin{figure}[H]
    \centering
    \begin{subfigure}{0.48\textwidth}
        \includegraphics[width=\textwidth]{figures/chart1.pdf}
        \caption{收入趋势}
    \end{subfigure}
    \hfill
    \begin{subfigure}{0.48\textwidth}
        \includegraphics[width=\textwidth]{figures/chart2.pdf}
        \caption{用户增长}
    \end{subfigure}
    \caption{关键指标对比}
\end{figure}
```

---

## 核心组件样式

### 标题层级

```css
/* PDF专用标题样式 */
h1 {
  font-size: 22pt;
  font-weight: 700;
  color: #1a1a1a;
  margin-top: 0;
  margin-bottom: 16pt;
  page-break-after: avoid;
}

h2 {
  font-size: 18pt;
  font-weight: 600;
  color: #1a1a1a;
  margin-top: 24pt;
  margin-bottom: 12pt;
  page-break-after: avoid;
}

h3 {
  font-size: 16pt;
  font-weight: 600;
  color: #4a4a4a;
  margin-top: 16pt;
  margin-bottom: 10pt;
  page-break-after: avoid;
}

h4 {
  font-size: 14pt;
  font-weight: 600;
  color: #4a4a4a;
  margin-top: 14pt;
  margin-bottom: 8pt;
}
```

### 正文排版

```css
/* 正文基础样式 */
body {
  font-size: 12pt;
  line-height: 1.5;
  color: #1a1a1a;
  font-family: 'Source Han Sans CN', sans-serif;
}

/* 段落 */
p {
  margin-top: 0;
  margin-bottom: 12pt;
  text-align: justify;
  text-indent: 0;
}

/* 列表 */
ul, ol {
  margin-top: 0;
  margin-bottom: 12pt;
  padding-left: 20pt;
}

li {
  margin-bottom: 6pt;
}

/* 引用 */
blockquote {
  margin: 12pt 0;
  padding-left: 12pt;
  border-left: 4px solid #2563eb;
  color: #4a4a4a;
  font-style: italic;
}

/* 代码 */
code {
  font-family: 'Source Code Pro', monospace;
  font-size: 10pt;
  background: #f5f5f5;
  padding: 2pt 4pt;
  border-radius: 3pt;
}

pre {
  font-family: 'Source Code Pro', monospace;
  font-size: 10pt;
  background: #f5f5f5;
  padding: 12pt;
  border-radius: 4pt;
  overflow-x: auto;
  page-break-inside: avoid;
}
```

### 页面元素

```css
/* 分页控制 */
.page-break-before { page-break-before: always; }
.page-break-after { page-break-after: always; }
.no-break { page-break-inside: avoid; }

/* 页眉 */
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 40pt;
  border-bottom: 1pt solid #d4d4d4;
  padding: 8pt 20pt;
  font-size: 10pt;
}

/* 页脚 */
.footer {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 30pt;
  border-top: 1pt solid #d4d4d4;
  padding: 6pt 20pt;
  font-size: 9pt;
  text-align: center;
}
```

---

## 生成命令

### 使用Pandoc生成

```bash
# Markdown转PDF
pandoc input.md \
  --pdf-engine=xelatex \
  --template=template.tex \
  --toc \
  --number-sections \
  --highlight-style=tango \
  -o output.pdf

# 使用自定义配置文件
pandoc input.md \
  --pdf-engine=xelatex \
  --metadata-file=metadata.yaml \
  --reference-doc=reference.docx \
  -o output.pdf

# metadata.yaml 示例
title: "报告标题"
subtitle: "副标题"
author: "作者"
date: "2025-01-10"
geometry: "top=2.5cm,bottom=2.5cm,left=2cm,right=2cm"
font-size: "12pt"
linestretch: "1.5"
```

### 使用Python（ReportLab）

```python
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# 注册中文字体
pdfmetrics.registerFont(TTFont('SourceHanSans', 'SourceHanSansCN-Normal.ttf'))
pdfmetrics.registerFont(TTFont('SourceHanSerif', 'SourceHanSerifCN-Normal.ttf'))

# 创建PDF
def create_report(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=2.5*cm,
        bottomMargin=2.5*cm
    )

    # 样式
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='CustomTitle',
        fontName='SourceHanSerif',
        fontSize=22,
        leading=28,
        spaceAfter=12,
        textColor=colors.HexColor('#1a1a1a')
    ))

    # 内容
    story = []
    story.append(Paragraph("报告标题", styles['CustomTitle']))
    story.append(Spacer(1, 0.5*cm))

    # 添加更多内容...

    doc.build(story)
```

### 使用JavaScript（Puppeteer）

```javascript
const puppeteer = require('puppeteer');
const fs = require('fs');

async function generatePDF(htmlFile, outputFile) {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();

  // 加载HTML
  await page.goto(`file://${__dirname}/${htmlFile}`);

  // 生成PDF
  await page.pdf({
    path: outputFile,
    format: 'A4',
    margin: {
      top: '2.5cm',
      bottom: '2.5cm',
      left: '2cm',
      right: '2cm'
    },
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: `
      <div style="font-size: 10pt; color: #666; padding: 10px 20px;">
        <span class="title">报告标题</span>
      </div>
    `,
    footerTemplate: `
      <div style="font-size: 9pt; color: #666; padding: 5px 20px; text-align: center;">
        第<span class="pageNumber"></span>页
      </div>
    `
  });

  await browser.close();
}
```

---

## 最佳实践清单

### ✅ 页面布局

- [ ] 使用标准纸张大小（A4）
- [ ] 设置合适的页边距（上下2.5cm，左右2cm）
- [ ] 确保页眉页脚不与内容重叠
- [ ] 控制行距（1.5倍为宜）
- [ ] 段落间距一致（段后0.5行）

### ✅ 字体使用

- [ ] 最多使用2-3种字体
- [ ] 正文不小于10.5pt（中文12pt）
- [ ] 标题层级清晰（字号递减）
- [ ] 避免使用过多字体样式
- [ ] 确保嵌入字体（防止缺字）

### ✅ 颜色使用

- [ ] 主色打印友好（避免纯色）
- [ ] 确保文字对比度≥4.5:1
- [ ] 考虑黑白打印效果
- [ ] 避免使用过多颜色
- [ ] 使用CMYK模式（印刷）

### ✅ 图表规范

- [ ] 图表分辨率≥300dpi
- [ ] 使用矢量格式（PDF/EPS）
- [ ] 图表添加标题和编号
- [ ] 坐标轴标签清晰
- [ ] 颜色在黑白打印时可区分

### ✅ 内容组织

- [ ] 包含目录（自动生成）
- [ ] 页码连续且位置一致
- [ ] 章节标题避免孤立在页底
- [ ] 图表与其说明在同一页
- [ ] 长表格添加续表标识

---

## 快速开始命令

```bash
# 创建新PDF报告
/pdf create my-report

# 添加章节
/pdf add chapter --title "执行摘要"

# 添加图表
/pdf add chart --file chart.pdf --caption "收入趋势"

# 生成PDF
/pdf build --engine xelatex

# 预览PDF
/pdf preview

# 转换为PDF
/pdf convert input.docx --output output.pdf
```

---

## 文档结构模板

```yaml
# PDF报告结构
structure:
  - cover:          # 封面
      - title: "报告标题"
      - subtitle: "副标题"
      - author: "作者"
      - date: "2025-01-10"
      - logo: "logo.png"

  - toc:            # 目录
      depth: 3       # 目录层级

  - executive:      # 执行摘要
      - summary
      - key_findings
      - recommendations

  - chapters:       # 正文章节
      - chapter_1:
          - title: "第一章"
          - sections:
              - section_1
              - section_2

  - appendices:     # 附录
      - data_tables
      - methodology

  - references:     # 参考文献
      style: "APA"
```

---

## 技术栈建议

| 组件 | 推荐工具 | 说明 |
|------|----------|------|
| 核心 | LaTeX | 学术/正式报告首选 |
| 替代 | Pandoc | Markdown转PDF |
| 可视化 | Python (ReportLab) | 程序化生成 |
| Web转PDF | Puppeteer | HTML转PDF |
| 字体 | 思源字体 | 开源中文字体 |
| 编辑器 | Overleaf / VS Code | LaTeX编辑 |
| 模板 | 自定义 / 社区 | 报告模板 |

---

## 输出质量检查

```
✅ 生成后检查清单

□ 文件大小合理（<10MB）
□ 所有字体正确显示
□ 页面边距一致
□ 页眉页脚正确
□ 图表清晰可读
□ 颜色打印效果良好
□ 目录页码正确
□ 超链接有效
□ 在不同设备打开测试
□ 打印测试页
```

---

> **注意**：PDF是固定布局格式，适合正式分发和打印归档。对于需要交互或实时更新的内容，考虑使用HTML格式。
