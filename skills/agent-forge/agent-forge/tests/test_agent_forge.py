"""
Unit tests for agent_forge.py — covers scout, evaluate, forge, register.
All tests use offline fixtures. No network required.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "agent_forge.py"
GH_FIXTURE = ROOT / "tests" / "fixtures" / "github_search.json"
NPM_FIXTURE = ROOT / "tests" / "fixtures" / "npm_search.json"


def run_forge(*args: str, stdin_data: str = "") -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(SCRIPT)] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, input=stdin_data or None)


class TestScoutGitHub(unittest.TestCase):
    def test_json_output(self):
        r = run_forge("scout", "github", "test", "--offline-file", str(GH_FIXTURE), "--format", "json")
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertEqual(data[0]["source"], "github")

    def test_markdown_output(self):
        r = run_forge("scout", "github", "test", "--offline-file", str(GH_FIXTURE), "--format", "markdown")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Repo", r.stdout)
        self.assertIn("all-agents-mcp", r.stdout)

    def test_contains_all_fields(self):
        r = run_forge("scout", "github", "test", "--offline-file", str(GH_FIXTURE), "--format", "json")
        data = json.loads(r.stdout)
        for item in data:
            for field in ["source", "name", "full_name", "description", "stars", "updated_at", "url", "language", "license", "topics"]:
                self.assertIn(field, item, f"Missing field: {field}")

    def test_max_results(self):
        r = run_forge("scout", "github", "test", "--offline-file", str(GH_FIXTURE), "--max-results", "1", "--format", "json")
        data = json.loads(r.stdout)
        self.assertEqual(len(data), 1)


class TestScoutNpm(unittest.TestCase):
    def test_json_output(self):
        r = run_forge("scout", "npm", "test", "--offline-file", str(NPM_FIXTURE), "--format", "json")
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(r.stdout)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertEqual(data[0]["source"], "npm")

    def test_markdown_output(self):
        r = run_forge("scout", "npm", "test", "--offline-file", str(NPM_FIXTURE), "--format", "markdown")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("@playwright/mcp", r.stdout)

    def test_popularity_extracted(self):
        r = run_forge("scout", "npm", "test", "--offline-file", str(NPM_FIXTURE), "--format", "json")
        data = json.loads(r.stdout)
        self.assertGreater(data[0]["popularity"], 0)


class TestEvaluate(unittest.TestCase):
    def test_evaluate_from_file(self):
        # First scout to get candidates
        r = run_forge("scout", "github", "test", "--offline-file", str(GH_FIXTURE), "--format", "json")
        candidates = r.stdout
        # Write to temp file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write(candidates)
            f.flush()
            r2 = run_forge("evaluate", "--capability", "mcp orchestrate codex gemini", "--input", f.name, "--format", "json")
        os.unlink(f.name)
        self.assertEqual(r2.returncode, 0, r2.stderr)
        data = json.loads(r2.stdout)
        self.assertIsInstance(data, list)
        for item in data:
            self.assertIn("score", item)
            self.assertIn("decision", item)
            s = item["score"]
            for axis in ["fitness", "freshness", "maturity", "integration", "scope", "total"]:
                self.assertIn(axis, s)
                self.assertGreaterEqual(s[axis], 0)
            self.assertIn(item["decision"], ["ADAPT", "HYBRID", "FORGE"])

    def test_evaluate_from_stdin(self):
        r = run_forge("scout", "github", "test", "--offline-file", str(GH_FIXTURE), "--format", "json")
        r2 = run_forge("evaluate", "--capability", "mcp", "--input", "-", "--format", "json", stdin_data=r.stdout)
        self.assertEqual(r2.returncode, 0, r2.stderr)
        data = json.loads(r2.stdout)
        self.assertGreater(len(data), 0)

    def test_evaluate_sorted_by_total(self):
        r = run_forge("scout", "github", "test", "--offline-file", str(GH_FIXTURE), "--format", "json")
        r2 = run_forge("evaluate", "--capability", "mcp orchestrate", "--input", "-", "--format", "json", stdin_data=r.stdout)
        data = json.loads(r2.stdout)
        totals = [x["score"]["total"] for x in data]
        self.assertEqual(totals, sorted(totals, reverse=True))

    def test_evaluate_markdown(self):
        r = run_forge("scout", "github", "test", "--offline-file", str(GH_FIXTURE), "--format", "json")
        r2 = run_forge("evaluate", "--capability", "mcp", "--input", "-", "--format", "markdown", stdin_data=r.stdout)
        self.assertEqual(r2.returncode, 0, r2.stderr)
        self.assertIn("Candidate", r2.stdout)
        self.assertIn("ADAPT", r2.stdout + r2.stdout)  # at least decision rule text


class TestForgeSkill(unittest.TestCase):
    def test_creates_complete_structure(self):
        with tempfile.TemporaryDirectory() as td:
            r = run_forge("forge", "skill", "--name", "test-skill", "--description", "A test", "--output", td)
            self.assertEqual(r.returncode, 0, r.stderr)
            skill_dir = Path(td) / "test-skill"
            self.assertTrue((skill_dir / "SKILL.md").exists())
            self.assertTrue((skill_dir / "HARNESS.md").exists())
            self.assertTrue((skill_dir / "scripts" / "oracle.sh").exists())
            self.assertTrue((skill_dir / "tests").is_dir())
            self.assertTrue((skill_dir / "references").is_dir())
            self.assertTrue((skill_dir / "assets").is_dir())

    def test_frontmatter_correct(self):
        with tempfile.TemporaryDirectory() as td:
            run_forge("forge", "skill", "--name", "my-skill", "--description", "Does things", "--output", td)
            text = (Path(td) / "my-skill" / "SKILL.md").read_text()
            self.assertIn("name: my-skill", text)
            self.assertIn("description: Does things", text)

    def test_oracle_is_executable(self):
        with tempfile.TemporaryDirectory() as td:
            run_forge("forge", "skill", "--name", "exec-test", "--description", "Test", "--output", td)
            oracle = Path(td) / "exec-test" / "scripts" / "oracle.sh"
            self.assertTrue(os.access(str(oracle), os.X_OK))

    def test_tests_exist(self):
        with tempfile.TemporaryDirectory() as td:
            run_forge("forge", "skill", "--name", "t-skill", "--description", "Test", "--output", td)
            tests = list((Path(td) / "t-skill" / "tests").glob("test_*.py"))
            self.assertGreaterEqual(len(tests), 1)

    def test_no_overwrite_without_force(self):
        with tempfile.TemporaryDirectory() as td:
            run_forge("forge", "skill", "--name", "dup", "--description", "First", "--output", td)
            r = run_forge("forge", "skill", "--name", "dup", "--description", "Second", "--output", td)
            self.assertEqual(r.returncode, 3)  # FileExistsError

    def test_overwrite_with_force(self):
        with tempfile.TemporaryDirectory() as td:
            run_forge("forge", "skill", "--name", "dup", "--description", "First", "--output", td)
            r = run_forge("forge", "skill", "--name", "dup", "--description", "Second", "--output", td, "--force")
            self.assertEqual(r.returncode, 0)

    def test_rejects_non_kebab(self):
        with tempfile.TemporaryDirectory() as td:
            r = run_forge("forge", "skill", "--name", "BadName", "--description", "Test", "--output", td)
            self.assertNotEqual(r.returncode, 0)


class TestForgeSubagent(unittest.TestCase):
    def test_creates_md_file(self):
        with tempfile.TemporaryDirectory() as td:
            r = run_forge("forge", "subagent", "--name", "test-agent", "--description", "A test agent", "--output", td)
            self.assertEqual(r.returncode, 0, r.stderr)
            path = Path(td) / "test-agent.md"
            self.assertTrue(path.exists())
            text = path.read_text()
            self.assertIn("name: test-agent", text)
            self.assertIn("model: sonnet", text)

    def test_preset_planner(self):
        with tempfile.TemporaryDirectory() as td:
            r = run_forge("forge", "subagent", "--name", "my-planner", "--description", "Plan things",
                          "--output", td, "--preset", "planner")
            self.assertEqual(r.returncode, 0, r.stderr)
            text = (Path(td) / "my-planner.md").read_text()
            self.assertIn("model: opus", text)
            self.assertIn("planning", text.lower())

    def test_preset_executor(self):
        with tempfile.TemporaryDirectory() as td:
            r = run_forge("forge", "subagent", "--name", "my-exec", "--description", "Execute things",
                          "--output", td, "--preset", "executor")
            text = (Path(td) / "my-exec.md").read_text()
            self.assertIn("model: sonnet", text)
            self.assertIn("full system access", text.lower())

    def test_preset_critic(self):
        with tempfile.TemporaryDirectory() as td:
            r = run_forge("forge", "subagent", "--name", "my-critic", "--description", "Verify things",
                          "--output", td, "--preset", "critic")
            text = (Path(td) / "my-critic.md").read_text()
            self.assertIn("model: opus", text)
            self.assertIn("VERDICT", text)

    def test_custom_model_and_tools(self):
        with tempfile.TemporaryDirectory() as td:
            r = run_forge("forge", "subagent", "--name", "custom-agent", "--description", "Custom",
                          "--output", td, "--model", "haiku", "--tools", "Read, Write, Bash, MCP")
            text = (Path(td) / "custom-agent.md").read_text()
            self.assertIn("model: haiku", text)
            self.assertIn("tools: Read, Write, Bash, MCP", text)

    def test_no_overwrite_without_force(self):
        with tempfile.TemporaryDirectory() as td:
            run_forge("forge", "subagent", "--name", "dup-agent", "--description", "First", "--output", td)
            r = run_forge("forge", "subagent", "--name", "dup-agent", "--description", "Second", "--output", td)
            self.assertEqual(r.returncode, 3)


class TestRegister(unittest.TestCase):
    def test_register_to_existing_store(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write("")  # empty store
            f.flush()
            r = run_forge("register", "--name", "test-skill", "--kind", "skill",
                          "--path", "/tmp/test", "--event-store", f.name)
            self.assertEqual(r.returncode, 0, r.stderr)
            data = json.loads(r.stdout)
            self.assertEqual(data["status"], "registered")
            # Verify event was written
            events = Path(f.name).read_text().strip().split("\n")
            self.assertEqual(len(events), 1)
            event = json.loads(events[0])
            self.assertEqual(event["type"], "agent_registered")
            self.assertEqual(event["payload"]["agent_name"], "test-skill")
        os.unlink(f.name)

    def test_register_no_store(self):
        r = run_forge("register", "--name", "test", "--kind", "subagent",
                      "--path", "/tmp/x", "--event-store", "/tmp/nonexistent-store-12345.jsonl")
        self.assertEqual(r.returncode, 0)
        data = json.loads(r.stdout)
        self.assertEqual(data["status"], "skipped")


class TestStructure(unittest.TestCase):
    """Verify agent-forge's own structure."""
    def test_skill_md(self):
        self.assertTrue((ROOT / "SKILL.md").exists())
    def test_harness_md(self):
        self.assertTrue((ROOT / "HARNESS.md").exists())
    def test_scripts_dir(self):
        self.assertTrue((ROOT / "scripts").is_dir())
    def test_tests_dir(self):
        self.assertTrue((ROOT / "tests").is_dir())
    def test_references_dir(self):
        self.assertTrue((ROOT / "references").is_dir())
    def test_frontmatter(self):
        text = (ROOT / "SKILL.md").read_text()
        self.assertIn("name: agent-forge", text)
    def test_word_count(self):
        text = (ROOT / "SKILL.md").read_text()
        words = len(re.findall(r"\b\w+\b", text))
        self.assertLessEqual(words, 5000, f"SKILL.md is {words} words")


if __name__ == "__main__":
    unittest.main()
