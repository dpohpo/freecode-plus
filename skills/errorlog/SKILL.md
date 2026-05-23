# ERRORLOG 错误分类记录系统

## Superpower 系统身份

我是 Superpower 决策引擎的 **错误分类记录** 模块。

**系统使命**：谋定而后动，深度思考，动态更新

**我的职责**：
- 对错误进行分类和记录
- 建立错误模式库
- 实现"圣斗士模式" - 同样的错误不犯两次

**兄弟模块**：
| 模块 | 职责 | 协作关系 |
|------|------|----------|
| /superpower | 协调器 | 执行前检查错误库 |
| /bail | 错误恢复 | 恢复后调用我记录 |
| /supermemory | 任务记忆 | 共享错误上下文 |

---

## 核心哲学（共享）

谋定而后动 | 不重复造轮子 | **不带伤前行** | 不赌博式推进

**圣斗士原则**：同样的错误不会犯两次，同样的招式也不会对我两次奏效。

---

## 错误分类体系

### Level 1: 大类（Seven Pernicious Kingdoms 参考）

| 类别 | 描述 | 示例 |
|------|------|------|
| **信息不足** | 缺少必要信息就行动 | 未验证 API 就调用 |
| **假设错误** | 基于错误假设推理 | 假设文件存在但实际不存在 |
| **逻辑错误** | 推理过程有缺陷 | 条件判断错误 |
| **工具误用** | 工具使用方式错误 | 参数传递错误 |
| **环境问题** | 外部环境导致的错误 | 网络超时、权限不足 |
| **规划幻觉** | 虚构不存在的步骤或能力 | 假设有不存在的命令 |

### Level 2: AI Agent 特有错误

| 类别 | 描述 | 来源 |
|------|------|------|
| **Planning Hallucination** | 虚构不存在的步骤 | [Galileo](https://galileo.ai/blog/agent-failure-modes-guide) |
| **Reasoning Loop** | 循环逻辑，永不收敛 | [awesome-agent-failures](https://github.com/vectara/awesome-agent-failures) |
| **Hallucination Cascade** | 错误信息累积放大 | [arXiv](https://arxiv.org/html/2509.18970v1) |
| **Sub-intention Error** | 遗漏子目标 | [Cleanlab](https://cleanlab.ai/blog/tau-bench/) |
| **Premature Success** | 未完成就声称完成 | [Medium](https://medium.com/@sahin.samia) |

---

## 错误记录格式

```markdown
# 错误 #[ID] - [错误名称]

## 分类
- 大类: [信息不足/假设错误/逻辑错误/工具误用/环境问题/规划幻觉]
- 子类: [AI Agent 特有错误类型]
- 严重程度: [LOW/MEDIUM/HIGH/CRITICAL]

## 错误描述
[具体发生了什么]

## 根因分析
[为什么会发生]

## 触发条件
[什么情况下会触发]

## 解决方案
[如何解决]

## 预防措施
[如何避免再次发生]

## 发现时间
[日期和任务ID]

## 类似错误
[关联的其他错误ID]
```

---

## 工作流程

### 错误发生时
```
1. /bail 捕获错误
2. /errorlog 分类
   - 检查是否是已知错误类型
   - 如果是新类型 → 创建新分类
   - 如果是已知类型 → 更新计数和案例
3. 记录完整上下文
4. 返回预防建议
```

### 执行前检查
```
1. /errorlog check [任务关键词]
2. 搜索相关历史错误
3. 返回警告：
   "注意：上次做类似任务时遇到 [错误类型]，原因是 [根因]，建议 [预防措施]"
4. 执行时避免重复错误
```

---

## 圣斗士模式实现

```python
def before_execution(task):
    # 检查是否有相关的历史错误
    past_errors = errorlog.search(task.keywords)

    if past_errors:
        print("⚠️ 历史错误警告:")
        for error in past_errors:
            print(f"  - {error.type}: {error.prevention}")

    return task

def after_error(error):
    # 记录新错误或更新已知错误
    error_type = classify(error)

    if error_type.is_new:
        errorlog.create_category(error_type)
        print("🔬 发现新错误类型！")
    else:
        error_type.count += 1
        error_type.cases.append(error.context)

    # 触发学习
    learn_from_error(error)
```

---

## 错误统计

```
错误类型        | 次数 | 最后发生    | 趋势
----------------|------|-------------|------
假设错误        | 12   | 2026-03-09  | ↓
信息不足        | 8    | 2026-03-08  | →
规划幻觉        | 5    | 2026-03-07  | ↓
工具误用        | 3    | 2026-03-05  | ↓
```

---

## 存储位置

```
~/.claude/memory/errorlog/
├── errors/
│   ├── ERR-001-assumption-error.md
│   ├── ERR-002-planning-hallucination.md
│   └── ...
├── taxonomy.json   # 错误分类体系
└── stats.json      # 错误统计
```

---

## 快速命令

| 命令 | 作用 |
|------|------|
| `/errorlog check [关键词]` | 执行前检查相关错误 |
| `/errorlog record` | 记录新错误 |
| `/errorlog stats` | 查看错误统计 |
| `/errorlog learn [错误ID]` | 深入学习某类错误 |
