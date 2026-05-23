#!/usr/bin/env python3
"""
Error Clarify - 错误澄清与预防系统

用法：
  python error_clarify.py                  # 查看所有错误
  python error_clarify.py record           # 交互式记录新错误
  python error_clarify.py <类型> <性质> <根源> "描述" "修复"  # 快速记录
  python error_clarify.py search <关键词>  # 搜索错误
  python error_clarify.py stats            # 统计分析
"""

import sys
import os
from datetime import datetime
from pathlib import Path
import json

# 路径配置
SCRIPT_DIR = Path(__file__).parent
SKILL_DIR = SCRIPT_DIR.parent
ERROR_LOG = Path.home() / "Desktop" / "error_log.md"
ERROR_DB = Path.home() / ".claude" / "data" / "errors.json"

# 确保数据目录存在
ERROR_DB.parent.mkdir(parents=True, exist_ok=True)


# =============================================================================
# 错误分类定义
# =============================================================================

ERROR_TYPES = {
    "理解性": {
        "定义": "误解意图、遗漏需求、过度解读",
        "检查点": ["用户意图是否明确？", "是否遗漏了隐含需求？", "是否过度解读了简单请求？"]
    },
    "逻辑性": {
        "定义": "推理断裂、因果倒置、假设错误、既定假设谬误",
        "检查点": ["推理链条是否完整？", "因果关系是否正确？", "假设在什么情况下会失效？", "是否忽略了边缘 Case？"]
    },
    "技术性": {
        "定义": "代码失败、命令错误、环境问题",
        "检查点": ["命令/代码是否测试过？", "环境依赖是否满足？", "是否有并发/递归风险？"]
    },
    "事实性": {
        "定义": "与客观现实不符、数据过时",
        "检查点": ["信息来源是否可靠？", "数据是否过时？", "是否与实际验证过？"]
    },
    "表达性": {
        "定义": "说明不清、格式混乱、术语不当",
        "检查点": ["表达是否清晰？", "格式是否符合预期？", "术语是否准确？"]
    },
}

ERROR_NATURE = {
    "遗漏": "缺少必要部分",
    "偏差": "细节有误但方向正确",
    "错位": "做了不该做的",
    "混淆": "概念/边界不清",
}

ERROR_SOURCE = {
    "认知局限": "模型能力边界、既定假设谬误",
    "上下文丢失": "记忆/状态问题",
    "信息不足": "用户输入模糊",
    "环境变化": "依赖/配置变更",
}


# =============================================================================
# 数据结构
# =============================================================================

def load_db() -> dict:
    """加载错误数据库"""
    if ERROR_DB.exists():
        try:
            return json.loads(ERROR_DB.read_text(encoding="utf-8"))
        except:
            pass
    return {"errors": [], "tags": [], "patterns": []}


def save_db(data: dict) -> None:
    """保存错误数据库"""
    ERROR_DB.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def add_error(error_type: str, nature: str, source: str,
              description: str, process: str, root_cause: str,
              prevention: str, next_note: str) -> str:
    """添加错误记录"""
    db = load_db()

    error_id = f"ERR-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    error_record = {
        "id": error_id,
        "timestamp": datetime.now().isoformat(),
        "type": error_type,
        "nature": nature,
        "source": source,
        "description": description,
        "process": process,
        "root_cause": root_cause,
        "prevention": prevention,
        "next_note": next_note,
        "occurrences": 1,
    }

    # 检查是否是重复错误
    for existing in db["errors"]:
        if (existing["type"] == error_type and
            existing["nature"] == nature and
            existing["source"] == source and
            existing["description"][:50] == description[:50]):
            existing["occurrences"] += 1
            existing["last_seen"] = datetime.now().isoformat()
            save_db(db)
            return f"[重复错误] {existing['id']}，已发生 {existing['occurrences']} 次"

    db["errors"].insert(0, error_record)  # 最新的在前
    save_db(db)

    # 同步到 Markdown 日志
    sync_to_markdown(error_record)

    return error_id


def sync_to_markdown(error: dict) -> None:
    """同步错误到 Markdown 日志"""
    entry = f"""## [{error['type']}{error['nature']}] {error['description'][:50]}...

**时间**: {error['timestamp'][:19]}
**ID**: {error['id']}
**分类**: `{error['type']}[{error['nature']}] ← {error['source']}`

**发生过程**
{error['process']}

**根本原因**
{error['root_cause']}

**预防措施**
{error['prevention']}

**下次注意**
{error['next_note']}

---
"""

    # 确保文件存在
    if not ERROR_LOG.exists():
        ERROR_LOG.write_text("# 错误记录日志\n\n由 MECE 分类系统自动记录\n\n", encoding="utf-8")

    # 追加记录
    with open(ERROR_LOG, "a", encoding="utf-8") as f:
        f.write(entry)


# =============================================================================
# 查询与统计
# =============================================================================

def show_stats() -> None:
    """显示错误统计"""
    db = load_db()
    errors = db.get("errors", [])

    if not errors:
        print("[ERROR_CLARIFY] 暂无错误记录", file=sys.stderr)
        return

    print("\n=== 错误统计 ===", file=sys.stderr)

    # 按类型统计
    type_stats = {}
    for err in errors:
        et = err["type"]
        type_stats[et] = type_stats.get(et, 0) + err.get("occurrences", 1)

    print("\n【按类型】", file=sys.stderr)
    for et, count in sorted(type_stats.items(), key=lambda x: -x[1]):
        print(f"  {et}: {count}", file=sys.stderr)

    # 按性质统计
    nature_stats = {}
    for err in errors:
        nat = err["nature"]
        nature_stats[nat] = nature_stats.get(nat, 0) + err.get("occurrences", 1)

    print("\n【按性质】", file=sys.stderr)
    for nat, count in sorted(nature_stats.items(), key=lambda x: -x[1]):
        print(f"  [{nat}]: {count}", file=sys.stderr)

    # 按来源统计
    source_stats = {}
    for err in errors:
        src = err["source"]
        source_stats[src] = source_stats.get(src, 0) + err.get("occurrences", 1)

    print("\n【按来源】", file=sys.stderr)
    for src, count in sorted(source_stats.items(), key=lambda x: -x[1]):
        print(f"  ← {src}: {count}", file=sys.stderr)

    # 重复错误
    recurring = [e for e in errors if e.get("occurrences", 1) > 1]
    if recurring:
        print(f"\n【重复错误】{len(recurring)} 个", file=sys.stderr)
        for err in recurring[:5]:
            print(f"  {err['id']}: {err['description'][:30]}... ({err['occurrences']}次)", file=sys.stderr)

    print("", file=sys.stderr)


def show_errors(limit: int = 10) -> None:
    """显示最近的错误"""
    db = load_db()
    errors = db.get("errors", [])[:limit]

    if not errors:
        print("[ERROR_CLARIFY] 暂无错误记录", file=sys.stderr)
        return

    print("\n=== 最近错误 ===", file=sys.stderr)
    for err in errors:
        print(f"\n{err['id']} | {err['type']}[{err['nature']}] ← {err['source']}", file=sys.stderr)
        print(f"  {err['description'][:80]}", file=sys.stderr)
        if err.get("occurrences", 1) > 1:
            print(f"  ⚠️  已发生 {err['occurrences']} 次", file=sys.stderr)


def search_errors(keyword: str) -> None:
    """搜索错误"""
    db = load_db()
    errors = db.get("errors", [])

    keyword_lower = keyword.lower()
    results = []

    for err in errors:
        text = f"{err['type']} {err['nature']} {err['source']} {err['description']} {err.get('root_cause', '')}"
        if keyword_lower in text.lower():
            results.append(err)

    if not results:
        print(f"[ERROR_CLARIFY] 未找到包含 '{keyword}' 的错误", file=sys.stderr)
        return

    print(f"\n=== 搜索结果: '{keyword}' ({len(results)} 条) ===", file=sys.stderr)
    for err in results:
        print(f"\n{err['id']} | {err['type']}[{err['nature']}] ← {err['source']}", file=sys.stderr)
        print(f"  {err['description']}", file=sys.stderr)
        print(f"  下次注意: {err.get('next_note', '')[:100]}", file=sys.stderr)


# =============================================================================
# 交互式记录
# =============================================================================

def interactive_record() -> None:
    """交互式记录错误"""
    print("\n=== 错误澄清 - 交互式记录 ===\n", file=sys.stderr)

    # 选择类型
    print("【错误类型】", file=sys.stderr)
    for i, (et, info) in enumerate(ERROR_TYPES.items(), 1):
        print(f"  {i}. {et}: {info['定义']}", file=sys.stderr)
    type_choice = input("\n选择类型 (1-5): ").strip()
    type_list = list(ERROR_TYPES.keys())
    error_type = type_list[int(type_choice) - 1] if type_choice.isdigit() else "理解性"

    # 显示检查点
    print(f"\n【{error_type}检查点】", file=sys.stderr)
    for i, point in enumerate(ERROR_TYPES[error_type]["检查点"], 1):
        print(f"  {i}. {point}", file=sys.stderr)

    # 选择性质
    print("\n【错误性质】", file=sys.stderr)
    for i, (nat, desc) in enumerate(ERROR_NATURE.items(), 1):
        print(f"  {i}. [{nat}]: {desc}", file=sys.stderr)
    nature_choice = input("\n选择性质 (1-4): ").strip()
    nature_list = list(ERROR_NATURE.keys())
    nature = nature_list[int(nature_choice) - 1] if nature_choice.isdigit() else "混淆"

    # 选择根源
    print("\n【错误根源】", file=sys.stderr)
    for i, (src, desc) in enumerate(ERROR_SOURCE.items(), 1):
        print(f"  {i}. ← {src}: {desc}", file=sys.stderr)
    source_choice = input("\n选择根源 (1-4): ").strip()
    source_list = list(ERROR_SOURCE.keys())
    source = source_list[int(source_choice) - 1] if source_choice.isdigit() else "认知局限"

    # 描述
    description = input("\n【简短描述】: ").strip()

    # 发生过程
    print("\n【发生过程】(多行，空行结束):", file=sys.stderr)
    process_lines = []
    while True:
        line = input()
        if not line:
            break
        process_lines.append(line)
    process = "\n".join(process_lines) if process_lines else "待补充"

    # 根本原因
    root_cause = input("\n【根本原因】: ").strip() or "待分析"

    # 预防措施
    prevention = input("\n【预防措施】: ").strip() or "待制定"

    # 下次注意
    next_note = input("\n【下次注意】: ").strip() or "待补充"

    # 记录
    error_id = add_error(error_type, nature, source, description, process, root_cause, prevention, next_note)

    print(f"\n✅ 错误已记录: {error_id}", file=sys.stderr)


def quick_record(args: list) -> None:
    """快速记录错误"""
    if len(args) < 4:
        print("用法: error_clarify.py <类型> <性质> <根源> \"描述\"", file=sys.stderr)
        return

    error_type = args[0]
    nature = args[1]
    source = args[2]
    description = args[3]

    # 默认值
    process = "待补充"
    root_cause = "待分析"
    prevention = "待制定"
    next_note = "待补充"

    add_error(error_type, nature, source, description, process, root_cause, prevention, next_note)
    print(f"[ERROR_CLARIFY] 已记录: {error_type}[{nature}] ← {source}", file=sys.stderr)


# =============================================================================
# 主程序
# =============================================================================

def main() -> int:
    if len(sys.argv) < 2:
        show_errors()
        show_stats()
        return 0

    cmd = sys.argv[1]

    if cmd == "record":
        interactive_record()
    elif cmd == "stats":
        show_stats()
    elif cmd == "search":
        if len(sys.argv) > 2:
            search_errors(sys.argv[2])
        else:
            print("用法: error_clarify.py search <关键词>", file=sys.stderr)
    elif cmd in ERROR_TYPES:
        # 快速记录: error_clarify.py 技术性 遗漏 环境变化 "描述"
        quick_record(sys.argv[1:])
    else:
        print(f"未知命令: {cmd}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
