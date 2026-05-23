---
name: random
description: 随机生成指定数量的数字（默认3个）
user-invocable: "true"
---

# Random Number Generator

> **/random** - 生成随机数字的快捷工具

---

## 功能说明

快速生成随机数字，用于测试、演示或任何需要随机数的场景。

---

## 基本用法

```bash
/random                    # 生成3个默认随机数字
/random 5                  # 生成5个随机数字
/random 10 1 100           # 生成10个1-100之间的随机数字
```

---

## 参数说明

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| 数量 | 要生成的随机数个数 | 3 | `/random 5` |
| 最小值 | 随机数的最小值 | 1 | `/random 3 10` |
| 最大值 | 随机数的最大值 | 100 | `/random 3 1 1000` |

---

## 输出格式

```
🎲 随机生成了 3 个数字：

42
87
15

统计信息：
- 最小值：15
- 最大值：87
- 平均值：48.0
- 总和：144
```

---

## 使用场景

1. **测试数据生成** - 为功能测试快速生成数字数据
2. **随机选择** - 从数组中随机选择索引
3. **演示示例** - 创建随机演示数据
4. **游戏开发** - 生成随机游戏参数
5. **统计分析** - 创建随机样本数据

---

## 高级用法

### 生成日期
```bash
# 生成3个随机日期（2024年1月1日到2024年12月31日）
/random 3 1 365  # 然后加到2024-01-01
```

### 生成百分比
```bash
# 生成3个0-100的百分比
/random 3 0 100
```

### 生成随机ID
```bash
# 生成5个4位随机ID
/random 5 1000 9999
```

### 生成随机坐标
```bash
# 生成10个-180到180的经度
/random 10 -180 180
```

---

## 代码示例

### Python
```python
import random

# 生成3个1-100的随机数
random_numbers = [random.randint(1, 100) for _ in range(3)]
print(random_numbers)  # [42, 87, 15]
```

### JavaScript
```javascript
// 生成3个1-100的随机数
const randomNumbers = Array.from({ length: 3 }, () => 
  Math.floor(Math.random() * 100) + 1
);
console.log(randomNumbers);  // [42, 87, 15]
```

### Bash
```bash
# 生成3个1-100的随机数
for i in {1..3}; do
  echo $((1 + RANDOM % 100))
done
```

---

## 输出选项

可以请求不同的输出格式：

```bash
/random --json          # JSON格式输出
/random --csv           # CSV格式输出
/random --array         # 数组格式输出 [42, 87, 15]
/random --sum-only      # 只显示总和
/random --sorted        # 排序输出
```

---

## 实现逻辑

```
输入: /random [数量=3] [最小值=1] [最大值=100]

1. 解析参数
2. 验证参数有效性
   - 数量 > 0
   - 最小值 < 最大值
3. 生成随机数
   - 使用高质量随机数生成器
   - 确保不重复（可选）
4. 计算统计信息
5. 格式化输出
```

---

$ARGUMENTS