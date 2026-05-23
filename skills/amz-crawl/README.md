# Amazon Stealth Crawler - Quick Start

## 🚀 快速开始

### 安装依赖
```bash
pip install playwright beautifulsoup4
```

### 基本用法
```bash
# 爬取 ASIN 列表
python3 ~/.claude/skills/amz-crawl/scripts/amazon_stealth_crawler.py \
  --input ~/Desktop/glm-amazon/data/amazon_3c/bsr_new_releases/category_picks.json \
  --output ~/Desktop/glm-amazon/outputs/amazon_stealth
```

### 快速测试（10 个产品）
```bash
python3 ~/.claude/skills/amz-crawl/scripts/amazon_stealth_crawler.py \
  --input ~/Desktop/glm-amazon/data/amazon_3c/bsr_new_releases/category_picks.json \
  --output /tmp/amazon_test \
  --limit 10
```

## 📊 性能对比

| 方法 | 成功率 | 失败率 |
|------|--------|--------|
| requests | 5.6% | 94.4% |
| **Stealth Crawler** | **90%** | **10%** |

## 📁 输出格式

```
output/
├── products.json          # 完整产品数据
├── products_progress.json # 每 10 个产品自动保存
└── run_summary.json       # 统计信息
```

## 🔧 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--input` | 输入 JSON 文件（必需） | - |
| `--output` | 输出目录（必需） | - |
| `--limit` | 限制产品数量（测试用） | 全部 |
| `--headless` | 使用无头模式（易被检测） | False |
| `--retries` | 每个产品最大重试次数 | 3 |
| `--batch` | 批处理，如 `1/3`（分3批，第1批） | - |

## 📝 输入格式

```json
[
  {
    "asin": "B08N5WRWNW",
    "category_path": "Electronics",
    "category_url": "https://www.amazon.com/gp/new-releases/electronics"
  },
  ...
]
```

## ✅ 输出格式

```json
[
  {
    "asin": "B08N5WRWNW",
    "success": true,
    "title": "Apple AirTag (2nd Generation)...",
    "brand": "Visit the Apple Store",
    "price": "$29.99",
    "rating": "4.6",
    "review_count": "3,675",
    "image_url": "https://...",
    "error": "",
    "attempts": 2,
    "category_path": "Electronics",
    "category_url": "https://..."
  }
]
```

## 🎯 数据质量

- ✅ 标题：100% 完整
- ✅ 评分：4.5-5.0 星
- ✅ 评论数：22-3,675 条
- ✅ 图片 URL：高质量主图
- ⚠️ 价格：~30% 提取率
- ⚠️ 品牌：~60% 提取率

## ⚠️ 错误处理

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `captcha` | CAPTCHA 挑战 | 自动重试（仍有 10% 失败） |
| `http_503` | 限流 | 增加延迟，使用代理池 |
| `missing_title` | 页面被拦截 | 更换指纹重试 |

## 📈 高级用法

### 使用代理池
编辑脚本，在 `crawl_product()` 方法中添加：
```python
context = await browser.new_context(
    proxy={"server": "http://proxy:port"}
)
```

### 分布式爬取
```bash
# 分 3 批并行
python3 scripts/amazon_stealth_crawler.py --input asins.json --output out1 --batch 1/3 &
python3 scripts/amazon_stealth_crawler.py --input asins.json --output out2 --batch 2/3 &
python3 scripts/amazon_stealth_crawler.py --input asins.json --output out3 --batch 3/3 &
```

## 💡 最佳实践

1. **使用非 headless 模式**（成功率 3x）
2. **随机延迟 3-8 秒**（模拟人类）
3. **每 10 个产品保存进度**（防止中断）
4. **使用系统 Chrome**（启动更快）

## 🆘 故障排除

### Chrome 未安装
```bash
# Mac
brew install --cask google-chrome

# Linux
sudo apt-get install google-chrome-stable
```

### 所有请求失败
- 检查网络连接
- 减少延迟（3-8s → 2-5s）
- 使用代理池

### 高 CAPTCHA 率
- 增加延迟（3-8s → 5-10s）
- 使用代理池（不同 IP）
- 考虑 CAPTCHA 解决服务

## 📚 相关文档

- 完整文档：`SKILL.md`
- 测试报告：`~/Desktop/glm-amazon/Stealth_爬虫测试报告.md`
- Playwright 文档：https://playwright.dev/python/

---

**状态**: ✅ 生产就绪
**成功率**: 90%
**测试日期**: 2026-05-19
