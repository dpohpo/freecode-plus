#!/usr/bin/env python3
"""
Autonomous Agent Session Loop v2.0 - Self-Healing Edition
基于 Anthropic autonomous-coding 示例的会话循环实现，增加自愈机制

This module implements the core session loop for the Two-Agent Pattern:
1. Initializer Agent (Session 1): Creates feature_list.json and project structure
2. Coding Agent (Sessions 2+): Implements features one at a time
3. Self-Healing Mode: When consecutive failures >= 3, inject history context
4. Deep Failure Mode: When consecutive failures >= 10, trigger handoff

NEW in v2.0:
- Consecutive failure detection
- Self-healing trigger (read history.failed + decisions)
- Deep failure trigger (generate handoff report)
- Structured history.json and decisions.json

Usage:
    from agent import run_autonomous_agent

    asyncio.run(run_autonomous_agent(
        project_dir=Path("/path/to/project"),
        model="claude-sonnet-4-5-20250929",
        max_iterations=100
    ))
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Tuple, Optional, Dict, Any, List

from client import create_client

# Configuration
AUTO_CONTINUE_DELAY_SECONDS = 3
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"

# Self-healing thresholds
FAILED_TRIGGER_THRESHOLD = 3      # 连续3次失败触发自愈
DEEP_FAILED_THRESHOLD = 10        # 连续10次失败触发人工介入
MAX_HISTORY_ENTRIES = 50          # 保留最近50条历史记录


# ============================================================
# Data Structures
# ============================================================

class AgentHistory:
    """管理 Agent 的失败和成功历史"""

    def __init__(self, history_file: Path):
        self.history_file = history_file
        self._ensure_exists()

    def _ensure_exists(self):
        """确保历史文件存在"""
        if not self.history_file.exists():
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            self._write({"failed": [], "succeeded": [], "decisions": []})

    def _read(self) -> Dict[str, Any]:
        """读取历史数据"""
        try:
            return json.loads(self.history_file.read_text())
        except Exception:
            return {"failed": [], "succeeded": [], "decisions": []}

    def _write(self, data: Dict[str, Any]):
        """写入历史数据"""
        self.history_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def record_failure(self, iteration: int, reason: str, feature_id: Optional[str] = None):
        """记录一次失败"""
        data = self._read()
        entry = {
            "iteration": iteration,
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "feature_id": feature_id
        }
        data["failed"].append(entry)
        # 保留最近 N 条
        data["failed"] = data["failed"][-MAX_HISTORY_ENTRIES:]
        self._write(data)
        return entry

    def record_success(self, iteration: int, feature_id: Optional[str] = None, feature_desc: str = ""):
        """记录一次成功"""
        data = self._read()
        entry = {
            "iteration": iteration,
            "timestamp": datetime.now().isoformat(),
            "feature_id": feature_id,
            "feature_desc": feature_desc
        }
        data["succeeded"].append(entry)
        self._write(data)
        return entry

    def add_decision(self, decision_id: str, description: str, rationale: str,
                     alternatives: List[str] = None):
        """添加一条设计决策"""
        data = self._read()
        entry = {
            "id": decision_id,
            "description": description,
            "rationale": rationale,
            "alternatives": alternatives or [],
            "made_at": datetime.now().isoformat()
        }
        data["decisions"].append(entry)
        self._write(data)
        return entry

    def get_failed(self) -> List[Dict]:
        """获取失败历史"""
        return self._read().get("failed", [])

    def get_succeeded(self) -> List[Dict]:
        """获取成功历史"""
        return self._read().get("succeeded", [])

    def get_decisions(self) -> List[Dict]:
        """获取设计决策"""
        return self._read().get("decisions", [])

    def get_recent_failures(self, n: int = 5) -> List[Dict]:
        """获取最近 N 次失败"""
        return self.get_failed()[-n:]

    def get_failure_summary(self) -> str:
        """生成失败摘要（用于注入 prompt）"""
        failures = self.get_recent_failures(5)
        if not failures:
            return "暂无失败历史"

        summary = "最近失败记录：\n"
        for i, f in enumerate(failures, 1):
            summary += f"  {i}. [迭代{f['iteration']}] {f['reason'][:100]}\n"
        return summary

    def get_decisions_summary(self) -> str:
        """生成决策摘要（用于注入 prompt）"""
        decisions = self.get_decisions()
        if not decisions:
            return "暂无设计决策"

        summary = "已有设计决策：\n"
        for d in decisions[-5:]:
            summary += f"  [{d['id']}] {d['description']}\n"
            summary += f"    理由：{d['rationale'][:80]}\n"
        return summary


class FeatureList:
    """管理 feature_list.json，增加 ID 支持"""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._ensure_schema()

    def _ensure_schema(self):
        """确保文件存在且有正确结构"""
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self._write([])

    def _read(self) -> List[Dict]:
        """读取 feature list"""
        try:
            return json.loads(self.file_path.read_text())
        except Exception:
            return []

    def _write(self, data: List[Dict]):
        """写入 feature list"""
        self.file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def ensure_ids(self):
        """确保每个 feature 都有 ID"""
        features = self._read()
        modified = False
        for i, f in enumerate(features):
            if "id" not in f:
                f["id"] = f"F{str(i+1).zfill(3)}"
                modified = True
        if modified:
            self._write(features)

    def count_passes(self) -> int:
        """计算已通过的数量"""
        return sum(1 for f in self._read() if f.get("passes", False))

    def count_total(self) -> int:
        """计算总数"""
        return len(self._read())

    def get_current_feature(self) -> Optional[Dict]:
        """获取当前需要实现的 feature（第一个 passes=false）"""
        for f in self._read():
            if not f.get("passes", False):
                return f
        return None

    def get_current_feature_id(self) -> Optional[str]:
        """获取当前 feature 的 ID"""
        f = self.get_current_feature()
        return f.get("id") if f else None

    def is_complete(self) -> bool:
        """检查是否全部完成"""
        features = self._read()
        return all(f.get("passes", False) for f in features) if features else False

    def get_status_string(self) -> str:
        """获取状态字符串"""
        return f"{self.count_passes()}/{self.count_total()}"

    def update_passes(self, feature_id: str, passes: bool = True) -> bool:
        """
        更新指定 feature 的 passes 状态
        这是唯一允许修改的字段
        """
        features = self._read()
        for f in features:
            if f.get("id") == feature_id:
                f["passes"] = passes
                f["updated_at"] = datetime.now().isoformat()
                self._write(features)
                return True
        return False


# ============================================================
# Prompt Generators
# ============================================================

def generate_self_healing_prompt(
    consecutive_failures: int,
    history: AgentHistory,
    feature_list: FeatureList
) -> str:
    """
    生成自愈模式的 prompt
    当连续失败 >= 3 次时触发
    """
    current_feature = feature_list.get_current_feature()
    current_feature_id = current_feature.get("id", "unknown") if current_feature else "unknown"
    current_feature_desc = current_feature.get("feature", "") if current_feature else ""

    failures_summary = history.get_failure_summary()
    decisions_summary = history.get_decisions_summary()

    prompt = f"""
═══════════════════════════════════════════════════════════════
⚠️ 自愈模式激活 (SELF-HEALING MODE)
═══════════════════════════════════════════════════════════════

你已连续 {consecutive_failures} 次尝试未能完成当前 feature。
在继续之前，你【必须】执行以下步骤：

───────────────────────────────────────────────────────────────
📌 第 1 步：读取失败历史
───────────────────────────────────────────────────────────────
{failures_summary}

请分析：
- 哪些方法已经尝试过但失败了？
- 失败的共同原因是什么？
- 如何避免重复这些失败？

───────────────────────────────────────────────────────────────
📌 第 2 步：读取设计决策
───────────────────────────────────────────────────────────────
{decisions_summary}

请确认：
- 你的新方案是否与已有决策一致？
- 如果需要做出新决策，请先记录。

───────────────────────────────────────────────────────────────
📌 第 3 步：制定新方案
───────────────────────────────────────────────────────────────
当前 feature: [{current_feature_id}] {current_feature_desc}

基于失败历史和设计决策，制定一个【不同的】实现方案：
- 这个方案与之前失败的方法有什么不同？
- 为什么这个方案更有可能成功？

───────────────────────────────────────────────────────────────
📌 第 4 步：确认后执行
───────────────────────────────────────────────────────────────
在开始实现之前，请先回复：

"我已分析失败历史和设计决策：
- 学到的关键教训：...
- 我的新方案与之前的不同之处：...
- 预期成功的原因：..."

然后再开始实现。

═══════════════════════════════════════════════════════════════
当前 feature_list.json 状态: {feature_list.get_status_string()} features passing
═══════════════════════════════════════════════════════════════
"""
    return prompt


def generate_deep_failure_prompt(
    consecutive_failures: int,
    history: AgentHistory,
    feature_list: FeatureList,
    handoff_file: Path
) -> str:
    """
    生成深度故障的 prompt
    当连续失败 >= 10 次时触发
    """
    prompt = f"""
═══════════════════════════════════════════════════════════════
🚨 深度故障模式 (DEEP FAILURE MODE)
═══════════════════════════════════════════════════════════════

你已连续 {consecutive_failures} 次尝试失败，这表明可能存在系统性问题。

当前状态：
- Feature 进度：{feature_list.get_status_string()}
- 失败次数：{consecutive_failures}
- 已生成的 handoff 文件：{handoff_file}

【重要】请执行以下操作：

1. 停止尝试实现当前 feature
2. 生成一份详细的诊断报告，包括：
   - 尝试过的所有方法
   - 每次失败的具体原因
   - 可能的系统性问题
   - 需要的人工干预建议

3. 将诊断报告保存到：{handoff_file}

4. 报告生成后，回复：
   "深度故障诊断报告已生成，请人工审查：{handoff_file}"

═══════════════════════════════════════════════════════════════
"""
    return prompt


# ============================================================
# Core Session Functions
# ============================================================

async def run_agent_session(client, message: str, project_dir: Path) -> Tuple[str, str]:
    """
    Run a single agent session.

    Args:
        client: ClaudeSDKClient instance
        message: User message to send
        project_dir: Project directory path

    Returns:
        Tuple of (result_type, result)
        - ("continue", response_text) on success
        - ("error", error_message) on failure
    """
    try:
        response_text = ""

        async for msg in client.run(messages=[{"role": "user", "content": message}]):
            if hasattr(msg, 'content'):
                response_text += str(msg.content)
            elif isinstance(msg, str):
                response_text += msg

        return ("continue", response_text)

    except Exception as e:
        return ("error", str(e))


def update_progress_file(progress_file: Path, feature: str, passed: int, total: int,
                         consecutive_failures: int = 0, self_healing_triggered: bool = False):
    """Update the progress notes file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    status_line = f"- Status: {passed}/{total} features passing"
    if consecutive_failures > 0:
        status_line += f" | 连续失败: {consecutive_failures}"

    entry = f"""
## Session {timestamp}
- Implemented: {feature}
{status_line}
"""

    if self_healing_triggered:
        entry += f"- 🔄 自愈模式已触发\n"

    current_content = ""
    if progress_file.exists():
        current_content = progress_file.read_text()

    progress_file.write_text(current_content + entry)


# ============================================================
# Main Agent Loop (v2.0 with Self-Healing)
# ============================================================

async def run_autonomous_agent(
    project_dir: Path,
    model: str = DEFAULT_MODEL,
    max_iterations: int = 100,
    initializer_prompt: Optional[str] = None,
    coding_prompt: Optional[str] = None,
    failed_trigger: int = FAILED_TRIGGER_THRESHOLD,
    deep_failed_trigger: int = DEEP_FAILED_THRESHOLD
):
    """
    Run the autonomous agent loop with self-healing mechanism.

    This implements the Two-Agent Pattern + Self-Healing:
    - First session: Initializer Agent creates feature_list.json
    - Subsequent sessions: Coding Agent implements features one at a time
    - Self-healing mode: When consecutive failures >= failed_trigger
    - Deep failure mode: When consecutive failures >= deep_failed_trigger

    Args:
        project_dir: Path to the project directory
        model: Claude model to use
        max_iterations: Maximum number of sessions to run
        initializer_prompt: Custom prompt for Initializer Agent
        coding_prompt: Custom prompt for Coding Agent
        failed_trigger: Threshold for self-healing mode (default: 3)
        deep_failed_trigger: Threshold for deep failure mode (default: 10)
    """
    # Initialize data structures
    tests_file = project_dir / "feature_list.json"
    progress_file = project_dir / "claude-progress.txt"
    history_file = project_dir / "agent_history.json"
    handoff_file = project_dir / "handoff" / f"handoff-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"

    feature_list = FeatureList(tests_file)
    history = AgentHistory(history_file)

    # Ensure feature IDs exist
    feature_list.ensure_ids()

    # Determine if this is first run or continuation
    is_first_run = not tests_file.exists() or feature_list.count_total() == 0

    # Load prompts
    if initializer_prompt is None:
        initializer_prompt_file = project_dir / "initializer_prompt.md"
        if initializer_prompt_file.exists():
            initializer_prompt = initializer_prompt_file.read_text()
        else:
            initializer_prompt = "Create the feature_list.json and initialize the project."

    if coding_prompt is None:
        coding_prompt_file = project_dir / "coding_prompt.md"
        if coding_prompt_file.exists():
            coding_prompt = coding_prompt_file.read_text()
        else:
            coding_prompt = "Continue implementing features from feature_list.json."

    # Create client
    client = create_client(project_dir, model)

    # Select initial prompt
    message = initializer_prompt if is_first_run else coding_prompt

    # Print startup info
    print("=" * 60)
    print("Starting autonomous agent v2.0 (Self-Healing Edition)")
    print("=" * 60)
    print(f"  Project: {project_dir}")
    print(f"  Model: {model}")
    print(f"  First run: {is_first_run}")
    print(f"  Max iterations: {max_iterations}")
    print(f"  Self-healing trigger: {failed_trigger} consecutive failures")
    print(f"  Deep failure trigger: {deep_failed_trigger} consecutive failures")
    print(f"  Current progress: {feature_list.get_status_string()}")
    print()

    # === Core loop with self-healing ===
    consecutive_failures = 0
    total_attempts = 0
    self_healing_count = 0

    iteration = 0
    while iteration < max_iterations:
        iteration += 1
        total_attempts += 1

        # Record passes before session
        passes_before = feature_list.count_passes()
        current_feature = feature_list.get_current_feature()
        current_feature_id = current_feature.get("id") if current_feature else None

        print()
        print("=" * 60)
        print(f"Iteration {iteration}/{max_iterations} | Progress: {feature_list.get_status_string()}")
        if consecutive_failures > 0:
            print(f"⚠️  Consecutive failures: {consecutive_failures}")
        print("=" * 60)

        # === Self-healing mode check ===
        if consecutive_failures >= failed_trigger and consecutive_failures < deep_failed_trigger:
            print(f"\n🔄 SELF-HEALING MODE TRIGGERED (failures: {consecutive_failures})")
            message = generate_self_healing_prompt(consecutive_failures, history, feature_list)
            self_healing_count += 1
            # Reset counter after triggering self-healing
            consecutive_failures = 0

        # === Deep failure mode check ===
        elif consecutive_failures >= deep_failed_trigger:
            print(f"\n🚨 DEEP FAILURE MODE TRIGGERED (failures: {consecutive_failures})")
            message = generate_deep_failure_prompt(
                consecutive_failures, history, feature_list, handoff_file
            )
            # After deep failure, reset and continue
            consecutive_failures = 0

        # Run session
        print(f"\n▶️  Running session...")
        result_type, result = await run_agent_session(client, message, project_dir)

        if result_type == "error":
            print(f"❌ Session error: {result}")
            consecutive_failures += 1
            history.record_failure(iteration, f"Session error: {result}", current_feature_id)
            message = "Continue. Try a different approach."
            await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)
            continue

        print(f"✅ Session completed ({len(result)} chars)")

        # Check if progress was made
        passes_after = feature_list.count_passes()
        # Re-read to get latest state
        feature_list = FeatureList(tests_file)
        passes_after = feature_list.count_passes()

        if passes_after > passes_before:
            # Success!
            consecutive_failures = 0
            print(f"🎉 Feature completed! {passes_before} → {passes_after}")
            history.record_success(iteration, current_feature_id,
                                   current_feature.get("feature", "") if current_feature else "")
            update_progress_file(progress_file,
                               current_feature.get("feature", "unknown") if current_feature else "unknown",
                               passes_after, feature_list.count_total())
        else:
            # No progress
            consecutive_failures += 1
            print(f"⚠️  No progress made. Consecutive failures: {consecutive_failures}")
            history.record_failure(iteration, "No passes change after session", current_feature_id)

        # Check completion
        if feature_list.is_complete():
            print()
            print("=" * 60)
            print("🎉 ALL FEATURES IMPLEMENTED!")
            print(f"   Total: {feature_list.count_total()} features")
            print(f"   Iterations used: {iteration}")
            print(f"   Self-healing triggered: {self_healing_count} times")
            print("=" * 60)
            break

        # Prepare for next iteration
        if consecutive_failures == 0:
            message = "Continue implementing features. Follow the 10-step workflow."
        else:
            message = f"You have failed {consecutive_failures} times. Try a completely different approach."

        # Delay before next session
        print(f"\nWaiting {AUTO_CONTINUE_DELAY_SECONDS}s before next session...")
        await asyncio.sleep(AUTO_CONTINUE_DELAY_SECONDS)

    # Loop ended
    if iteration >= max_iterations:
        print()
        print("=" * 60)
        print(f"Reached maximum iterations ({max_iterations})")
        print(f"Final progress: {feature_list.get_status_string()}")
        print(f"Self-healing triggered: {self_healing_count} times")
        print("=" * 60)


# ============================================================
# Demo / Test
# ============================================================

async def demo():
    """Demo the self-healing agent with a sample project."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        project_dir = Path(tmpdir)

        # Create minimal project structure
        (project_dir / "frontend").mkdir()
        (project_dir / "backend").mkdir()

        # Create a simple feature list with IDs
        feature_list = [
            {
                "id": "F001",
                "feature": "User can see a welcome message",
                "test_code": "const text = await page.textContent('h1'); expect(text).toContain('Welcome');",
                "passes": False
            },
            {
                "id": "F002",
                "feature": "User can click a button",
                "test_code": "await page.click('button'); await page.waitForSelector('.clicked');",
                "passes": False
            }
        ]
        (project_dir / "feature_list.json").write_text(json.dumps(feature_list, indent=2))

        # Test FeatureList class
        fl = FeatureList(project_dir / "feature_list.json")
        print(f"Feature list status: {fl.get_status_string()}")
        print(f"Current feature: {fl.get_current_feature()}")
        print(f"Is complete: {fl.is_complete()}")

        # Test AgentHistory class
        history_file = project_dir / "agent_history.json"
        history = AgentHistory(history_file)

        # Record some failures
        history.record_failure(1, "Could not find selector #welcome", "F001")
        history.record_failure(2, "Timeout waiting for element", "F001")
        history.record_failure(3, "Element not visible", "F001")

        print(f"\nFailure summary:\n{history.get_failure_summary()}")

        # Test self-healing prompt
        prompt = generate_self_healing_prompt(3, history, fl)
        print(f"\nSelf-healing prompt generated ({len(prompt)} chars)")

        # Simulate success
        history.record_success(4, "F001", "User can see a welcome message")
        print(f"\nSuccess recorded. Total succeeded: {len(history.get_succeeded())}")


if __name__ == "__main__":
    asyncio.run(demo())
