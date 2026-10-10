import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(__file__), "analyze_transcripts.py")


def line(ts, model, out, rid, cw=5):
    return json.dumps({"type": "assistant", "timestamp": ts, "requestId": rid,
                       "message": {"model": model, "usage": {
                           "input_tokens": 1, "cache_read_input_tokens": 10,
                           "cache_creation_input_tokens": cw, "output_tokens": out}}})


class AppendTokensTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        repo = "/work/my.repo"
        proj = os.path.join(self.tmp, "projects", "-work-my-repo")
        sess = os.path.join(proj, "s1")
        os.makedirs(os.path.join(sess, "subagents"))
        with open(os.path.join(proj, "s1.jsonl"), "w") as f:
            f.write(line("2026-10-01T10:00:30.500Z", "claude-opus-5-5", 100, "o1") + "\n")
            f.write(line("2026-10-01T10:02:00.000Z", "claude-opus-5-5", 10, "o0", cw=150_000) + "\n")
            f.write(line("2026-10-01T10:20:00.000Z", "claude-opus-5-5", 200, "o2") + "\n")
        for name, desc, ts, model, out in [
            ("a1", "Implement T1", "2026-10-01T10:01:00.000Z", "claude-sonnet-5-5", 50),
            ("a2", "Review T1 diff", "2026-10-01T10:05:00.000Z", "claude-opus-5-5", 70),
        ]:
            base = os.path.join(sess, "subagents", f"agent-{name}")
            with open(base + ".jsonl", "w") as f:
                f.write(line(ts, model, out, name) + "\n")
            with open(base + ".meta.json", "w") as f:
                json.dump({"description": desc}, f)
        self.log = os.path.join(self.tmp, "metrics.jsonl")
        with open(self.log, "w") as f:
            f.write(json.dumps({"run": "R", "ts": "2026-10-01T10:00:00Z", "event": "start", "repo": repo}) + "\n")
            f.write(json.dumps({"run": "R", "ts": "2026-10-01T10:10:00Z", "event": "batch",
                                "repo": repo, "tasks": ["T1"]}) + "\n")
        self.root = os.path.join(self.tmp, "projects")

    def run_script(self):
        return subprocess.run([sys.executable, "-I", SCRIPT, "--append-tokens", "--log", self.log,
                               "--root", self.root], capture_output=True, text=True, check=True)

    def events(self):
        with open(self.log) as f:
            return [json.loads(l) for l in f]

    def test_appends_window_tokens_by_role_and_is_idempotent(self):
        self.run_script()
        tokens = [e for e in self.events() if e["event"] == "tokens"]
        self.assertEqual(len(tokens), 1)
        t = tokens[0]
        self.assertEqual(t["orch"]["opus"]["out"], 110)  # the 10:20 turn is outside the window
        self.assertEqual((t["cache_breaks"], t["max_uncached"]), (1, 150_001))
        self.assertEqual(t["impl"]["sonnet"]["out"], 50)
        self.assertEqual(t["rev"]["opus"]["out"], 70)
        self.assertEqual((t["impl_agents"], t["rev_agents"]), (1, 1))
        self.run_script()
        self.assertEqual(len([e for e in self.events() if e["event"] == "tokens"]), 1)


if __name__ == "__main__":
    unittest.main()
