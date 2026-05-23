---
name: quote
description: 资产地契系统 - 你的GPS导航。记录偏好、查询资产、精准定位。触发场景：(1) /quote (2) /quote find <keyword> (3) /quote where <name> (4) /quote scan (5) 记录偏好/保存偏好
user-invocable: "true"
---

# Asset Cadastre System (资产地契系统)

> 你的Claude Code资产GPS导航系统

## 核心功能

1. **资产定位** - 指哪儿打哪儿，精准找到任何skill/agent/hook/项目
2. **偏好记录** - 持久化你的配置和偏好
3. **资产索引** - 167个资产的完整地图
4. **快速查询** - 语义搜索 + 关键词匹配 + 别名系统

## 使用方法

### 查询资产（GPS导航）
```
/quote find bht        # 找bht相关资产
/quote find voice      # 找voice相关
/quote find hook       # 找所有hook
/quote find 记忆       # 语义搜索
```

### 直接获取路径
```
/quote where bht       # 返回: /Users/.../.claude/skills/bht
/quote where settings  # 返回: /Users/.../.claude/settings.json
```

### 列出资产
```
/quote list            # 列出所有资产
/quote list skills     # 只列出skills
/quote list agents     # 只列出agents
```

### 记录偏好
```
/quote save            # 保存当前会话偏好到 ~/Desktop/quote.md
/quote                 # 同上
```

### 维护索引
```
/quote scan            # 重新扫描所有资产（新安装skill后使用）
/quote stats           # 查看索引统计
/quote export          # 导出完整markdown索引
```

## 资产统计

| 类型 | 数量 |
|------|------|
| Skills | 98 |
| Agents | 16 |
| Hooks | 36 |
| Configs | 4 |
| Projects | 10 |
| Memory | 3 |
| **总计** | **167** |

## 快速参考

### 常用Skills
- `/bht` - BHT极限思维系统
- `/hardest` - 最深层思考
- `/mece` - MECE分析
- `/voice` - 中文语音对话
- `/saveraw` - 保存对话记忆
- `/search` - 权威搜索引擎

### 常用Agents
- `codex-backend` - 后端开发
- `gemini-ui` - UI设计
- `lemon` - Amazon分析
- `researcher` - 数据采集

### 关键配置
- `~/.claude/settings.json` - 主设置
- `~/.claude/mcp.json` - MCP配置
- `~/.claude/hooks.json` - Hook配置
- `~/.claude/CLAUDE.md` - 全局指令

### 记忆系统
- `~/.immortal-agent/` - Immortal Agent状态
- `~/Desktop/memory/` - 桌面记忆库
- `~/.hcom/` - HCOM数据库

## 底层实现

```
~/.claude/cadastre/
├── schema.json           # 数据结构定义
├── registry.json         # 资产注册表
├── discovery_engine.py   # 发现引擎
├── cadastre.py           # 查询接口
├── cadastre              # Shell入口
└── CADASTRE.md           # Markdown导出
```

## 设计哲学

这个系统不是O(1)。它是：

1. **预计算 + 符号化** - 用空间换时间
2. **语义寻址** - 说人话就能定位
3. **人类标注** - 只有你能给资产赋予真正的语义
4. **自维护目标** - 朝着AGI自认知能力前进

---

## 执行协议

当用户触发 /quote 时：

1. 检查是否有参数
   - 有 `find` → 调用 `cadastre find`
   - 有 `where` → 调用 `cadastre where`
   - 有 `list` → 调用 `cadastre list`
   - 有 `scan` → 调用 `cadastre scan`
   - 有 `stats` → 调用 `cadastre stats`
   - 有 `export` → 调用 `cadastre export`
   - 无参数 → 执行偏好记录

2. 偏好记录流程：
   - 扫描当前会话使用的技能
   - 提取偏好和配置
   - 追加到 `~/Desktop/quote.md`

3. 输出格式：
   - 查询结果使用表格或列表
   - 包含路径、类型、触发方式
   - 精确匹配优先显示
