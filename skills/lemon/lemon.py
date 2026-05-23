#!/usr/bin/env python3
"""
Lemon Agent Team Launcher
启动 Amazon 市场分析 Agent Team 的协调器
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# 配置路径
AGENTS_DIR = Path.home() / ".claude" / "agents"
REPORTS_DIR = Path.home() / "Desktop" / "amazon-reports"

# 团队配置
TEAM = {
    "lead": "lemon",
    "members": ["researcher", "analyst", "skeptic-auditor", "policy-guard"]
}

# 站点映射
SITES = {
    "US": "amazon.com",
    "UK": "amazon.co.uk",
    "DE": "amazon.de",
    "JP": "amazon.co.jp",
    "CN": "amazon.cn"
}

# 分析模式
MODES = {
    "quick": "快速筛查 (15-20分钟)",
    "deep": "深度分析 (60-90分钟)"
}


def parse_input(user_input: str) -> dict:
    """解析用户输入，提取分析参数"""
    parts = user_input.strip().split()

    if not parts or parts[0] != "/lemon":
        return {"error": "不是 /lemon 命令"}

    result = {
        "keyword": "",
        "site": "US",
        "mode": "deep"
    }

    # 跳过 /lemon
    parts = parts[1:] if len(parts) > 1 else []

    # 解析参数
    for i, part in enumerate(parts):
        part_upper = part.upper()
        if part_upper in SITES:
            result["site"] = part_upper
        elif part_upper in ["QUICK", "FAST"]:
            result["mode"] = "quick"
        elif part_upper in ["DEEP", "FULL"]:
            result["mode"] = "deep"
        elif part_upper not in ["SITE", "ANALYSIS", " feasibility".upper().split()]:
            # 累积关键词
            result["keyword"] += (" " if result["keyword"] else "") + part

    return result


def build_team_prompt(params: dict) -> str:
    """构建 team 启动 prompt"""

    keyword = params.get("keyword", "").strip()
    site = params.get("site", "US")
    mode = params.get("mode", "deep")

    if not keyword:
        return build_interactive_prompt()

    # 读取 Lemon agent 配置
    lemon_path = AGENTS_DIR / "lemon.md"
    if not lemon_path.exists():
        return f"""⚠️ Lemon agent 文件不存在: {lemon_path}

请确保以下文件已复制到 ~/.claude/agents/:
- lemon.md
- analyst.md
- researcher.md
- skeptic-auditor.md
- policy-guard.md"""

    prompt = f"""# 🍋 Lemon Agent Team 启动

**任务**: Amazon 类目市场可行性分析
**目标关键词**: {keyword}
**目标站点**: {site} ({SITES.get(site, site)})
**分析模式**: {MODES.get(mode, mode)}
**启动时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 团队状态

✅ Lemon (指挥官) - 已就位
✅ Researcher (数据员) - 待命
✅ Analyst (分析员) - 待命
✅ Skeptic (审计员) - 待命
✅ PolicyGuard (合规官) - 待命

---

## 执行指令

你现在作为 **Lemon** 指挥官，请按以下流程执行分析：

### Phase 0: 任务澄清
- 目标类目/niche: {keyword}
- 目标站点: {site}
- 分析深度: {mode}

### Phase 1-4: 按标准流程执行
参考 `~/.claude/agents/lemon.md` 中定义的完整工作流。

### 输出要求
1. 在当前会话完整展示决策备忘录
2. 将报告保存到: `~/Desktop/amazon-reports/{keyword.replace(' ', '_')}_分析备忘录_{datetime.now().strftime('%Y%m%d')}.md`

---

**现在开始执行分析。** 遵循所有铁律，特别是：
- 不编造数据
- 每个数据点标注来源
- 推测与事实分离
- 不利信息等权重呈现
- 置信度显式标注"""

    return prompt


def build_interactive_prompt() -> str:
    """构建交互式 prompt"""
    return """# 🍋 Lemon Agent Team

欢迎启动 Amazon 市场分析团队！请提供以下信息：

---

## 📋 分析任务信息

**1. 目标类目/Niche/产品关键词**
> 你想分析哪个类目或产品？例如：yoga mat, 智能手表, wireless earbuds

**2. 目标站点 (可选，默认 US)**
> - US (美国)
> - UK (英国)
> - DE (德国)
> - JP (日本)
> - CN (中国)

**3. 分析深度 (可选，默认深度分析)**
> - quick: 快速筛查 (15-20分钟)
> - deep: 深度分析 (60-90分钟)

---

请提供以上信息，格式如：
```
关键词: yoga mat
站点: US
深度: deep
```

或直接说：`/lemon yoga mat US deep`
"""


def main():
    """主入口"""
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        user_input = sys.stdin.read().strip() if not sys.stdin.isatty() else ""

    params = parse_input(user_input)
    prompt = build_team_prompt(params)

    print(prompt)


if __name__ == "__main__":
    main()
