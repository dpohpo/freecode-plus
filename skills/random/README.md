# /random - 随机数字生成器

快速生成随机数字的命令行工具。

## 🚀 快速开始

```bash
# 生成3个默认随机数字（1-100）
random

# 生成5个随机数字
random 5

# 生成10个1-1000之间的随机数字
random 10 1 1000

# 生成不重复的随机数字
random 5 1 20 --unique

# 排序输出
random 5 --sort

# JSON格式输出
random --json

# 数组格式输出
random --array
```

## 📋 参数说明

| 位置参数 | 说明 | 默认值 |
|---------|------|--------|
| count | 要生成的随机数个数 | 3 |
| min | 随机数的最小值 | 1 |
| max | 随机数的最大值 | 100 |

## 🎨 输出格式选项

| 选项 | 说明 |
|------|------|
| --json | JSON格式输出 |
| --csv | CSV格式输出 |
| --array | 数组格式输出 |
| --sum-only | 只显示总和 |
| --unique, -u | 生成不重复的数字 |
| --sort, -s | 排序输出 |

## 💡 使用示例

### 测试数据生成
```bash
# 生成测试用户ID
random 10 1000 9999

# 生成测试分数（0-100）
random 20 0 100
```

### 随机选择
```bash
# 生成3个索引（用于从数组中随机选择）
random 3 0 9 --unique
```

### 演示数据
```bash
# 生成演示价格
random 5 10 500

# 生成演示坐标
random 2 -180 180
```

### JSON格式（用于脚本）
```bash
# 生成JSON格式的随机数据
random 3 1 100 --json
```

输出：
```json
{
  "numbers": [42, 87, 15],
  "count": 3,
  "min": 15,
  "max": 87,
  "avg": 48.0,
  "sum": 144
}
```

## 📦 安装位置

- 技能文件：`~/.claude/skills/random/SKILL.md`
- 执行脚本：`~/.claude/skills/random/random_gen.py`

## 🔧 技术细节

- 使用Python标准库`random`模块
- 支持高质量随机数生成
- 自动计算统计信息（最小值、最大值、平均值、总和）
- 支持多种输出格式

---

*Created by Poincare - 2026*
