---
name: long-running
description: 长时间运行Agent的完整工程实践系统。基于Anthropic官方工程博客"Effective Harnesses for Long-Running Agents"像素级还原。使用场景：(1)构建能跨越多个context window的autonomous agent (2)实现Two-Agent Pattern架构 (3)管理复杂项目的增量进度 (4)设计session handoff机制 (5)实现browser automation测试 (6)构建多层安全沙箱。核心能力：Initializer Agent + Coding Agent双角色设计、feature_list.json状态管理、10步workflow执行协议、三层安全模型、Puppeteer MCP集成。
user-invocable: "true"
---

# Long-Running Agent Engineering System

基于 Anthropic 官方工程实践，像素级还原长时间运行 Agent 的完整技术栈。

## 核心架构：Two-Agent Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                    Two-Agent Pattern                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Session 1: Initializer Agent                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 1. Analyze requirements from prompt                      │  │
│  │ 2. Create feature_list.json (200+ test cases)            │  │
│  │ 3. Initialize project structure                          │  │
│  │ 4. Write initializer_prompt.md → coding_prompt.md        │  │
│  │ 5. First git commit                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                     │
│                           ▼                                     │
│  Sessions 2+: Coding Agent (repeated until done)               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ STEP 1: GET BEARINGS (pwd, ls, git log, cat files)       │  │
│  │ STEP 2: START SERVERS (init.sh)                          │  │
│  │ STEP 3: VERIFICATION TEST (run passing tests)            │  │
│  │ STEP 4: CHOOSE ONE FEATURE from feature_list.json        │  │
│  │ STEP 5: IMPLEMENT THE FEATURE                            │  │
│  │ STEP 6: VERIFY WITH BROWSER AUTOMATION                   │  │
│  │ STEP 7: UPDATE feature_list.json (ONLY "passes" field)   │  │
│  │ STEP 8: COMMIT PROGRESS (git commit)                     │  │
│  │ STEP 9: UPDATE PROGRESS NOTES                            │  │
│  │ STEP 10: END SESSION CLEANLY                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                     │
│                           ▼ (repeat until all features pass)    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 为什么是 Two-Agent？

**逻辑天花板**：在 Context Window 约束下，Two-Agent 是必然最优解。

```
Long-Running = Initializer(creates state machine) + Σ[ Coding Agent(state transfer) ]

数学证明：
- 设 Context Window = W tokens
- 设项目需要 P tokens 的完整上下文
- 如果 P > W，则必须在多次 session 中完成
- Two-Agent 将 P 分解为：
  - Initializer: 创建状态机定义 (feature_list.json)
  - Coding Agent: 每次 session 读取状态 + 执行一步 + 更新状态
- 状态传递成本 = O(1) per session (只读取 feature_list.json)
```

## 关键组件实现

### 1. Feature List System

**核心数据结构**：`feature_list.json`

```json
[
  {
    "feature": "User can create a new todo item",
    "test_code": "await page.type('#new-todo', 'Buy groceries'); await page.click('#add-btn');",
    "passes": false
  },
  {
    "feature": "User can mark a todo as complete",
    "test_code": "await page.click('.todo-item:first-child .complete-btn');",
    "passes": false
  }
]
```

**设计原则**：
- 每个 feature 包含 3 个字段：`feature`（描述）、`test_code`（Puppeteer 验证代码）、`passes`（状态）
- Coding Agent **只能修改 `passes` 字段**，不能修改其他字段
- 这是防止 Agent "作弊"（自己改测试）的关键约束

### 2. Progress Tracking System

**claude-progress.txt** 格式：

```
# Progress Notes

## Session 2024-01-15 14:30
- Implemented: User can create a new todo item
- Next: User can mark a todo as complete
- Status: 1/10 features passing

## Session 2024-01-15 16:45
- Implemented: User can mark a todo as complete
- Next: User can delete a todo item
- Status: 2/10 features passing
```

**设计目的**：
- 人类可读的进度追踪
- 帮助新 session 快速理解上下文
- 与 feature_list.json 双重验证

### 3. Environment Management

**init.sh** 启动脚本模式：

```bash
#!/bin/bash

# Kill any existing servers
pkill -f "node.*server.js" 2>/dev/null || true
pkill -f "python.*app.py" 2>/dev/null || true

# Start backend
cd backend && npm install && npm start &

# Wait for backend to be ready
sleep 2

# Start frontend
cd ../frontend && npm install && npm start &

# Wait for all services
wait
```

**服务健康检查协议**：

```python
async def wait_for_server(url, timeout=30):
    """等待服务启动，超时报错"""
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except:
            pass
        await asyncio.sleep(1)
    raise TimeoutError(f"Server {url} not ready after {timeout}s")
```

### 4. Security Model (三层防护)

```
┌─────────────────────────────────────────────────────────────┐
│                    Layer 1: Sandbox                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ macOS Seatbelt / Linux namespaces                    │   │
│  │ - 文件系统隔离                                        │   │
│  │ - 网络访问控制                                        │   │
│  │ - 进程隔离                                            │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    Layer 2: Permissions                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Claude SDK permission system                         │   │
│  │ - allowed_tools whitelist                            │   │
│  │ - defaultMode: "acceptEdits"                         │   │
│  │ - 禁止危险工具（如 Delete, WebSearch）               │   │
│  └─────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    Layer 3: Bash Allowlist                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ PreToolUse Hook 验证                                 │   │
│  │ - 白名单命令: ls, cat, git, npm, node, ...          │   │
│  │ - 特殊验证: pkill, chmod, init.sh                   │   │
│  │ - 阻止所有未授权命令                                  │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Bash Allowlist 实现**：

```python
ALLOWED_COMMANDS = {
    "ls", "cat", "head", "tail", "wc", "grep", "cp", "mkdir",
    "chmod", "pwd", "npm", "node", "git", "ps", "lsof", "sleep",
    "pkill", "init.sh"
}

COMMANDS_NEEDING_EXTRA_VALIDATION = {"pkill", "chmod", "init.sh"}

async def bash_security_hook(input_data, tool_use_id=None, context=None):
    command = input_data.get("command", "")

    # Parse base command
    base_cmd = command.split()[0] if command.split() else ""

    # Check allowlist
    if base_cmd not in ALLOWED_COMMANDS:
        return {"decision": "block", "reason": f"Command '{base_cmd}' not in allowlist"}

    # Extra validation for sensitive commands
    if base_cmd in COMMANDS_NEEDING_EXTRA_VALIDATION:
        # Additional checks...
        pass

    return {}  # Allow
```

### 5. Claude Agent SDK 配置

```python
from claude_code_sdk import ClaudeSDKClient, ClaudeCodeOptions

PUPPETEER_TOOLS = [
    "mcp__puppeteer__puppeteer_navigate",
    "mcp__puppeteer__puppeteer_screenshot",
    "mcp__puppeteer__puppeteer_click",
    "mcp__puppeteer__puppeteer_type",
]

BUILTIN_TOOLS = ["Read", "Write", "Edit", "Glob", "Grep", "Bash"]

def create_client(project_dir, model):
    return ClaudeSDKClient(
        options=ClaudeCodeOptions(
            model=model,
            allowed_tools=[*BUILTIN_TOOLS, *PUPPETEER_TOOLS],
            mcp_servers={
                "puppeteer": {
                    "command": "npx",
                    "args": ["puppeteer-mcp-server"]
                }
            },
            hooks={
                "PreToolUse": [
                    HookMatcher(matcher="Bash", hooks=[bash_security_hook])
                ]
            },
            max_turns=1000,
            cwd=str(project_dir.resolve()),
        )
    )
```

### 6. Session Loop 实现

```python
AUTO_CONTINUE_DELAY_SECONDS = 3

async def run_autonomous_agent(project_dir, model, max_iterations):
    tests_file = project_dir / "feature_list.json"
    is_first_run = not tests_file.exists()

    client = create_client(project_dir, model)

    if is_first_run:
        message = initializer_prompt
    else:
        message = coding_prompt

    iteration = 0
    while iteration < max_iterations:
        iteration += 1

        result_type, result = await run_agent_session(client, message, project_dir)

        if result_type == "error":
            print(f"Error: {result}")
            break

        # Check if all features pass
        if tests_file.exists():
            tests = json.loads(tests_file.read_text())
            if all(t["passes"] for t in tests):
                print("All features implemented!")
                break

        # Prepare for next iteration
        message = "Continue implementing features."
        await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

async def run_agent_session(client, message, project_dir):
    """Run a single agent session, return ("continue", text) or ("error", exception)"""
    try:
        response_text = ""
        async for message in client.run(messages=[{"role": "user", "content": message}]):
            if hasattr(message, 'content'):
                response_text += str(message.content)

        return ("continue", response_text)
    except Exception as e:
        return ("error", str(e))
```

## Coding Agent 10 步 Workflow 详解

### STEP 1: GET YOUR BEARINGS

```
pwd                    # 确认工作目录
ls -la                 # 查看项目结构
git log --oneline -10  # 查看最近提交
cat feature_list.json  # 查看任务列表
cat claude-progress.txt # 查看进度笔记
```

**目的**：在新 session 建立上下文感知，理解"我在哪"、"做了什么"、"要做什么"。

### STEP 2: START SERVERS

```bash
./init.sh  # 或项目特定的启动脚本
```

**关键**：每次 session 重新启动服务，确保干净环境。

### STEP 3: VERIFICATION TEST

运行所有已通过的测试，确保代码处于健康状态：

```javascript
// 使用 Puppeteer 验证已实现功能
for (const feature of features.filter(f => f.passes)) {
    await page.goto('http://localhost:3000');
    await eval(feature.test_code);
    // 如果失败，修复 regression
}
```

### STEP 4: CHOOSE ONE FEATURE

从 `feature_list.json` 中选择第一个 `passes: false` 的 feature。

**为什么只选一个？**
- 单一职责：每个 session 只做一件事
- 可追溯：git commit 对应单个 feature
- 可回滚：出问题只需回退一个 commit

### STEP 5: IMPLEMENT THE FEATURE

实现代码，同时更新：
- 前端组件
- 后端 API
- 数据库 schema（如需要）

### STEP 6: VERIFY WITH BROWSER AUTOMATION

```javascript
// 使用 Puppeteer MCP 工具
await mcp__puppeteer__puppeteer_navigate({url: "http://localhost:3000"});
await mcp__puppeteer__puppeteer_screenshot({name: "before"});
await mcp__puppeteer__puppeteer_type({selector: "#new-todo", text: "Test"});
await mcp__puppeteer__puppeteer_click({selector: "#add-btn"});
await mcp__puppeteer__puppeteer_screenshot({name: "after"});
```

### STEP 7: UPDATE feature_list.json

**唯一允许的修改**：将对应 feature 的 `passes` 改为 `true`。

```json
{
  "feature": "User can create a new todo item",
  "test_code": "...",
  "passes": true  // 只改这里
}
```

### STEP 8: COMMIT PROGRESS

```bash
git add -A
git commit -m "Implement: User can create a new todo item"
```

**commit message 规范**：`Implement: <feature description>`

### STEP 9: UPDATE PROGRESS NOTES

```markdown
## Session 2024-01-15 14:30
- Implemented: User can create a new todo item
- Verified: Puppeteer test passes
- Next: User can mark a todo as complete
- Status: 1/10 features passing
```

### STEP 10: END SESSION CLEANLY

- 确保所有测试通过
- 确保代码已提交
- 确保服务仍在运行（供下次验证）
- 自然结束，让外层 loop 决定是否继续

## 失败模式与解决方案

### 失败模式 1: Agent 忘记之前的工作

**症状**：Agent 重复实现已完成的 feature

**解决方案**：
1. 强制 STEP 1 读取 `git log` 和 `claude-progress.txt`
2. feature_list.json 作为唯一真相来源
3. 已完成的 feature 标记为 `passes: true`

### 失败模式 2: Agent "作弊"

**症状**：Agent 修改 test_code 使其通过，而非真正实现功能

**解决方案**：
1. Coding Agent 不能修改 test_code（只在 STEP 7 修改 passes）
2. Initializer Agent 创建的 test_code 是不可变的
3. 人类审计时对比 git diff

### 失败模式 3: 服务状态污染

**症状**：服务在多次 session 后行为异常

**解决方案**：
1. init.sh 每次强制 kill 旧进程
2. 使用内存数据库（SQLite :memory:）或每次重置
3. STEP 3 验证测试确保基线正确

### 失败模式 4: 无限循环

**症状**：Agent 卡在某个 feature 无法完成

**解决方案**：
1. max_iterations 参数限制总循环次数
2. 人类监控 claude-progress.txt
3. 超过阈值触发人工介入

## 快速启动模板

### 项目结构

```
project/
├── feature_list.json      # 任务列表（Initializer 创建）
├── claude-progress.txt    # 进度笔记（Coding Agent 维护）
├── init.sh               # 启动脚本
├── initializer_prompt.md # Initializer Agent prompt
├── coding_prompt.md      # Coding Agent prompt
├── frontend/             # 前端代码
├── backend/              # 后端代码
└── tests/                # 测试代码
```

### 最小可运行示例

```python
# autonomous_agent_demo.py
import asyncio
from pathlib import Path
from agent import run_autonomous_agent

async def main():
    project_dir = Path.cwd()
    await run_autonomous_agent(
        project_dir=project_dir,
        model="claude-sonnet-4-5-20250929",
        max_iterations=100
    )

if __name__ == "__main__":
    asyncio.run(main())
```

## BHT 分析结论

```
🏔️ Two-Agent Pattern 极限综合结论
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔺 逻辑天花板：
   在 Context Window 有限的前提下，Two-Agent 是必然最优解。
   状态机模式（feature_list.json）将 O(n) 的上下文问题降为 O(1)。

🔺 直觉天花板：
   像"交接班"系统——Initializer 是白班，建立规则；
   Coding Agent 是夜班团队，按规则执行，每班只做一件事。

🔺 类比天花板：
   类比于编译器前端/后端、操作系统初始化/运行态、Git init/commit。
   本质是"一次性建立规则 + 多次执行规则"的模式。

🔺 元认知天花板：
   未来演进方向——Hierarchical Agents（多级代理）、
   Swarm Agents（群体智能）、Self-Healing Agents（自愈代理）。

🔺 系统天花板：
   这是一个稳态系统，feature_list.json 是状态变量。
   每次 Coding Agent 是一次"状态转移"，将 passes=false 变为 passes=true。

🔺 第一性原理天花板：
   底层约束：Context Window 有限
   核心洞察：将"无限上下文需求"转化为"有限状态机 + 多次执行"
   数学本质：Long-Running = Σ(Local-Execution)，其中 State Transfer Cost = O(1)

核心公式：
  Long-Running = Initializer(creates state machine)
               + Σ[ Coding Agent(read state → execute → write state) ]

最终置信度：95%（已通过 Anthropic 官方实践验证）
已知认知盲区：非编码类任务（如研究、写作）的 long-running 模式
```

## 标记系统

| 标记 | 含义 |
|------|------|
| 🔄 | Session 边界 |
| 📋 | Feature list 操作 |
| 🧪 | 测试验证 |
| 🔒 | 安全层触发 |
| 📸 | Puppeteer 截图 |
| 💾 | Git commit |
| ⚠️ | 潜在失败模式 |

## 铁律

1. **[HARD] Feature List 不可变** — Coding Agent 只能修改 `passes` 字段
2. **[HARD] 单 Feature 原则** — 每个 session 只实现一个 feature
3. **[HARD] 提交即检查点** — 每个 feature 完成后必须 git commit
4. **[HARD] 测试先行验证** — STEP 3 必须验证已通过的测试
5. **[HARD] 服务重启** — 每次 session 重新启动服务
6. **[HARD] 三层安全** — Sandbox + Permissions + Allowlist 缺一不可
7. **[HARD] max_iterations 上限** — 防止无限循环
8. **[SOFT] 人类监控** — 定期检查 claude-progress.txt

---

## 参考资料

- Anthropic Engineering Blog: [Effective Harnesses for Long-Running Agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- GitHub: [anthropics/claude-quickstarts/autonomous-coding](https://github.com/anthropics/claude-quickstarts/tree/main/autonomous-coding)
- Claude Agent SDK Documentation
