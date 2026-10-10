#!/usr/bin/env python3
"""Estimate how much of a tasklist-run session goes to TODO bookkeeping.

Reads Claude Code transcripts (~/.claude/projects/*/<session>.jsonl plus the
<session>/subagents/*.jsonl files) and reports, per session and in total:

  - orchestrator vs subagent spend, in input-equivalent token units
  - bookkeeping spend: turns whose tool calls only touch the TODO or run log,
    plus the TODO's cost of sitting in context, plus delegation-prompt output
  - bookkeeping failures (errored or rejected calls, repeated edits)

Units: input 1.0, cache read 0.1, cache write 1.25 (5m) or 2.0 (1h), output 5.0,
then scaled by a per-model weight. The unit ratios and the default model weights
are ASSUMPTIONS; override the weights with --weights and check current pricing.
Only the share (bookkeeping / total) matters for the build decision, so a
consistent weighting is enough.

Scope limit: a session is measured from its first tasklist-run mention to its
end, so unrelated work later in the same session inflates the orchestrator side.
Look at the per-session turn counts before trusting a row.

Usage:
  analyze_transcripts.py [--root DIR] [--project SUBSTR] [--since YYYY-MM-DD]
                         [--weights opus=1,sonnet=0.6,haiku=0.2] [--json]
  analyze_transcripts.py --append-tokens [--log PATH] [--root DIR] [--dry-run]

--append-tokens adds one `tokens` event per `batch` line of the task-workflow
metrics log, with raw token counts for the orchestrator, implementer and reviewer
in that batch's time window (previous batch, or the run's `start`, up to this
batch), plus `cache_breaks` (turns with more than 100k uncached input, i.e. input
plus cache-write tokens, across all roles) and `max_uncached` (the largest such turn). Batches that already have a `tokens` event are skipped, so it is safe to
re-run. Windows are matched to transcripts by repo path; parallel sessions in the
same repo during a run would be mixed in.
"""
import argparse
import datetime
import glob
import json
import os
import re
import sys
from collections import defaultdict

RATIO = {"input": 1.0, "read": 0.1, "write5m": 1.25, "write1h": 2.0, "output": 5.0}
BOOKKEEPING_PATH = re.compile(r"TODO[^\s\"']*\.md|\.tasklist-runlog\.md|tasklist-runlog")
START_MARK = re.compile(r"tasklist-run")


def model_weight(model, weights):
    m = (model or "").lower()
    for name, w in weights.items():
        if name in m:
            return w
    return 1.0


def units(usage, model, weights):
    cc = usage.get("cache_creation") or {}
    w1h = cc.get("ephemeral_1h_input_tokens", 0)
    w5m = cc.get("ephemeral_5m_input_tokens", 0)
    if not cc:
        w5m = usage.get("cache_creation_input_tokens", 0)
    raw = (
        usage.get("input_tokens", 0) * RATIO["input"]
        + usage.get("cache_read_input_tokens", 0) * RATIO["read"]
        + w5m * RATIO["write5m"]
        + w1h * RATIO["write1h"]
        + usage.get("output_tokens", 0) * RATIO["output"]
    )
    return raw * model_weight(model, weights)


def records(path):
    with open(path, errors="replace") as f:
        for line in f:
            try:
                yield json.loads(line)
            except ValueError:
                continue


def is_bookkeeping_call(block):
    inp = block.get("input") or {}
    name = block.get("name", "")
    if name in ("Read", "Edit", "Write"):
        return bool(BOOKKEEPING_PATH.search(inp.get("file_path", "")))
    if name == "Bash":
        return bool(BOOKKEEPING_PATH.search(inp.get("command", "")))
    return False


def text_of(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(b.get("text", "") for b in content if isinstance(b, dict))
    return ""


def analyze_session(path, weights):
    """Return metrics for one session, or None if tasklist-run never appears."""
    turns = {}  # requestId -> dict(ts, model, usage, tools)
    start = None
    results = {}  # tool_use_id -> (is_error, chars)
    uses = {}  # tool_use_id -> (name, input, bookkeeping)
    order = []
    session_id = os.path.basename(path)[:-6]

    for d in records(path):
        ts = d.get("timestamp")
        t = d.get("type")
        msg = d.get("message") if isinstance(d.get("message"), dict) else {}
        if start is None and ts and t in ("user", "assistant"):
            blob = json.dumps(msg.get("content", ""))
            if START_MARK.search(blob) and ("tasklist-run" in blob):
                start = ts
        if t == "assistant" and start is not None:
            rid = d.get("requestId") or d.get("uuid")
            turn = turns.setdefault(
                rid, {"ts": ts, "model": msg.get("model"), "usage": {}, "tools": []}
            )
            if msg.get("usage"):
                turn["usage"] = msg["usage"]  # later blocks repeat/refine usage
            for b in msg.get("content", []) if isinstance(msg.get("content"), list) else []:
                if b.get("type") == "tool_use":
                    bk = is_bookkeeping_call(b)
                    turn["tools"].append((b["id"], b["name"], bk))
                    uses[b["id"]] = (b["name"], b.get("input") or {}, bk)
                    if rid not in order:
                        order.append(rid)
        elif t == "user" and start is not None and isinstance(msg.get("content"), list):
            for b in msg["content"]:
                if b.get("type") == "tool_result":
                    results[b.get("tool_use_id")] = (
                        bool(b.get("is_error")),
                        len(text_of(b.get("content"))),
                    )
    if start is None:
        return None

    ordered = sorted(turns.items(), key=lambda kv: kv[1]["ts"] or "")
    orch_total = 0.0
    bk_turns = 0.0
    bk_turn_count = 0
    bk_mixed_output = 0.0
    todo_resident = 0.0
    todo_reads = 0
    prompt_out = 0.0
    delegations = 0
    bk_calls = 0
    bk_failed = 0
    edit_targets = defaultdict(int)
    models = defaultdict(float)

    for i, (_, turn) in enumerate(ordered):
        u = turn["usage"]
        cost = units(u, turn["model"], weights)
        orch_total += cost
        models[turn["model"] or "?"] += cost
        tools = turn["tools"]
        if tools and all(bk for _, _, bk in tools):
            bk_turns += cost
            bk_turn_count += 1
        elif any(bk for _, _, bk in tools):
            bk_mixed_output += (
                u.get("output_tokens", 0) * RATIO["output"] * model_weight(turn["model"], weights)
            )
        remaining = len(ordered) - i - 1
        for tid, name, bk in tools:
            if bk:
                bk_calls += 1
                err = results.get(tid, (False, 0))[0]
                if err:
                    bk_failed += 1
                inp = uses[tid][1]
                if name in ("Edit", "Write"):
                    edit_targets[inp.get("file_path", "")] += 1
            if name == "Read" and bk:
                todo_reads += 1
                tokens = results.get(tid, (False, 0))[1] / 4
                todo_resident += (
                    tokens * (RATIO["write5m"] + RATIO["read"] * remaining)
                    * model_weight(turn["model"], weights)
                )
            if name in ("Agent", "SendMessage"):
                delegations += 1
                inp = uses[tid][1]
                chars = len(inp.get("prompt", "") or inp.get("message", ""))
                prompt_out += (chars / 4) * RATIO["output"] * model_weight(turn["model"], weights)

    # Subagents spawned in this session, from the start mark onward.
    sub_total = 0.0
    sub_by_role = defaultdict(float)
    sub_count = 0
    sub_dir = path[:-6] + "/subagents"
    for sp in glob.glob(sub_dir + "/agent-*.jsonl"):
        meta = {}
        try:
            with open(sp[:-6] + ".meta.json") as f:
                meta = json.load(f)
        except (OSError, ValueError):
            pass
        sturns = {}
        first_ts = None
        for d in records(sp):
            if d.get("type") != "assistant":
                continue
            first_ts = first_ts or d.get("timestamp")
            m = d.get("message") or {}
            if m.get("usage"):
                sturns[d.get("requestId") or d.get("uuid")] = (m.get("model"), m["usage"])
        if first_ts is None or first_ts < start:
            continue
        cost = sum(units(u, mdl, weights) for mdl, u in sturns.values())
        desc = (meta.get("description") or "").lower()
        role = "reviewer" if "review" in desc else "implementer/other"
        sub_total += cost
        sub_by_role[role] += cost
        sub_count += 1
        for mdl, u in sturns.values():
            models[mdl or "?"] += units(u, mdl, weights)

    repeated_edits = sum(max(0, n - 1) for n in edit_targets.values())
    return {
        "session": session_id,
        "project": os.path.basename(os.path.dirname(path)),
        "start": start,
        "orch_turns": len(ordered),
        "bookkeeping_turns": bk_turn_count,
        "orch_units": orch_total,
        "sub_units": sub_total,
        "sub_agents": sub_count,
        "sub_by_role": dict(sub_by_role),
        "bk_turn_units": bk_turns,
        "bk_mixed_output_units": bk_mixed_output,
        "todo_resident_units": todo_resident,
        "todo_reads": todo_reads,
        "delegation_prompt_units": prompt_out,
        "delegations": delegations,
        "bk_calls": bk_calls,
        "bk_failed": bk_failed,
        "bk_repeated_edits": repeated_edits,
        "units_by_model": dict(models),
    }


def pct(a, b):
    return f"{100 * a / b:5.1f}%" if b else "   n/a"


def fmt(n):
    return f"{n / 1000:,.0f}k"


def report(rows):
    print(f"{'session':10} {'project':28} {'turns':>5} {'bk':>4} {'orch':>8} {'subs':>8} "
          f"{'bk-turn':>8} {'todo-ctx':>8} {'prompts':>8}  {'saveable%':>9} {'orch%':>6} {'fail':>4}")
    tot = defaultdict(float)
    for r in rows:
        saveable = (r["bk_turn_units"] + r["bk_mixed_output_units"]
                    + r["todo_resident_units"] + r["delegation_prompt_units"])
        total = r["orch_units"] + r["sub_units"]
        print(f"{r['session'][:8]:10} {r['project'][-28:]:28} {r['orch_turns']:>5} "
              f"{r['bookkeeping_turns']:>4} {fmt(r['orch_units']):>8} {fmt(r['sub_units']):>8} "
              f"{fmt(r['bk_turn_units']):>8} {fmt(r['todo_resident_units']):>8} "
              f"{fmt(r['delegation_prompt_units']):>8}  {pct(saveable, total):>9} "
              f"{pct(r['orch_units'], total):>6} {r['bk_failed']:>4}")
        for k in ("orch_turns", "bookkeeping_turns", "orch_units", "sub_units", "bk_turn_units",
                  "bk_mixed_output_units", "todo_resident_units", "delegation_prompt_units",
                  "bk_calls", "bk_failed", "bk_repeated_edits"):
            tot[k] += r[k]
    total = tot["orch_units"] + tot["sub_units"]
    saveable = (tot["bk_turn_units"] + tot["bk_mixed_output_units"]
                + tot["todo_resident_units"] + tot["delegation_prompt_units"])
    print()
    print(f"sessions: {len(rows)}   total spend: {fmt(total)} units (model-weighted, input-equivalent)")
    print(f"orchestrator share of spend:        {pct(tot['orch_units'], total)}")
    print(f"bookkeeping-only turns:             {int(tot['bookkeeping_turns'])} of {int(tot['orch_turns'])} orchestrator turns")
    print(f"upper bound a CLI could save:       {pct(saveable, total)}  "
          f"(bk turns {pct(tot['bk_turn_units'], total)}, TODO in context {pct(tot['todo_resident_units'], total)}, "
          f"delegation prompts {pct(tot['delegation_prompt_units'], total)})")
    print(f"realistic saving (about 60% of it): {pct(0.6 * saveable, total)}   "
          f"(a CLI still costs one call per batch and some output)")
    print(f"bookkeeping calls: {int(tot['bk_calls'])}, failed/rejected: {int(tot['bk_failed'])}, "
          f"repeated edits to the same file: {int(tot['bk_repeated_edits'])}")
    print()
    print("Decision rule: >= ~8% realistic saving -> build for cost; 3-8% -> build only for monitor/IDs/"
          "reliability; < 3% -> skip.")


DEFAULT_LOG = os.path.expanduser("~/.local/state/danny-agent-skills/task-workflow/metrics.jsonl")
ZERO = {"in": 0, "cr": 0, "cw": 0, "out": 0}
CACHE_BREAK_UNCACHED = 100_000  # a turn with more uncached input than this is a "cache break"


def parse_ts(ts):
    return datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))


def raw_usage(usage):
    return {
        "in": usage.get("input_tokens", 0),
        "cr": usage.get("cache_read_input_tokens", 0),
        "cw": usage.get("cache_creation_input_tokens", 0),
        "out": usage.get("output_tokens", 0),
    }


def short_model(model):
    m = (model or "").lower()
    for name in ("opus", "sonnet", "haiku", "fable"):
        if name in m:
            return name
    return model or "?"


def add_raw(bucket, model, raw):
    slot = bucket.setdefault(short_model(model), dict(ZERO))
    for k in ZERO:
        slot[k] += raw[k]


def transcript_turns(path):
    """(timestamp, model, raw usage) once per API request."""
    turns = {}
    for d in records(path):
        if d.get("type") != "assistant" or not d.get("timestamp"):
            continue
        m = d.get("message") or {}
        if m.get("usage"):
            turns[d.get("requestId") or d.get("uuid")] = (
                parse_ts(d["timestamp"]), m.get("model"), raw_usage(m["usage"]))
    return list(turns.values())


def project_dir(root, repo):
    return os.path.join(root, re.sub(r"[^A-Za-z0-9]", "-", repo))


def batch_tokens(root, repo, lo, hi):
    """Raw tokens by role and model for transcripts of `repo` between lo and hi."""
    out = {"orch": {}, "impl": {}, "rev": {}}
    counts = {"orch_turns": 0, "impl_agents": 0, "rev_agents": 0}
    uncached = []  # input + cache-write tokens of every turn, all roles
    for path in glob.glob(os.path.join(project_dir(root, repo), "*.jsonl")):
        if datetime.datetime.fromtimestamp(os.path.getmtime(path), datetime.timezone.utc) < lo:
            continue
        for ts, model, raw in transcript_turns(path):
            if lo < ts <= hi:
                add_raw(out["orch"], model, raw)
                uncached.append(raw["in"] + raw["cw"])
                counts["orch_turns"] += 1
        for sp in glob.glob(path[:-6] + "/subagents/agent-*.jsonl"):
            turns = transcript_turns(sp)
            if not turns or not (lo < min(t[0] for t in turns) <= hi):
                continue
            try:
                with open(sp[:-6] + ".meta.json") as f:
                    desc = (json.load(f).get("description") or "").lower()
            except (OSError, ValueError):
                desc = ""
            role = "rev" if "review" in desc else "impl"
            counts[role + "_agents"] += 1
            for _, model, raw in turns:
                add_raw(out[role], model, raw)
                uncached.append(raw["in"] + raw["cw"])
    out.update(counts)
    out["cache_breaks"] = sum(1 for u in uncached if u > CACHE_BREAK_UNCACHED)
    out["max_uncached"] = max(uncached, default=0)
    return out


def append_tokens(log, root, dry_run):
    lines = list(records(log)) if os.path.exists(log) else []
    done = {(d.get("run"), d.get("batch_ts")) for d in lines if d.get("event") == "tokens"}
    prev = {}  # run -> previous window edge
    new = []
    for d in lines:
        run, ev = d.get("run"), d.get("event")
        if ev == "start":
            prev[run] = parse_ts(d["ts"])
        elif ev == "batch":
            hi = parse_ts(d["ts"])
            lo = prev.get(run) or hi - datetime.timedelta(hours=2)
            prev[run] = hi
            if (run, d["ts"]) in done:
                continue
            t = batch_tokens(root, d["repo"], lo, hi)
            new.append({"v": 1, "run": run, "ts": d["ts"], "event": "tokens", "batch_ts": d["ts"],
                        "repo": d["repo"], "tasks": d.get("tasks"), **t})
    for rec in new:
        text = json.dumps(rec, separators=(",", ":"))
        if dry_run:
            print(text)
    if not dry_run and new:
        with open(log, "a") as f:
            for rec in new:
                f.write(json.dumps(rec, separators=(",", ":")) + "\n")
    print(f"{'would append' if dry_run else 'appended'} {len(new)} tokens event(s) to {log}",
          file=sys.stderr)
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--project", help="substring of the project directory name")
    ap.add_argument("--since", help="only sessions whose file changed on or after YYYY-MM-DD")
    ap.add_argument("--weights", default="opus=1,sonnet=0.6,haiku=0.2",
                    help="relative per-model price weights (placeholders; check real pricing)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--append-tokens", action="store_true",
                    help="append a tokens event for each batch in the metrics log")
    ap.add_argument("--log", default=DEFAULT_LOG)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    weights = {k: float(v) for k, v in (p.split("=") for p in a.weights.split(","))}
    if a.append_tokens:
        return append_tokens(a.log, a.root, a.dry_run)

    since = None
    if a.since:
        import datetime
        since = datetime.datetime.strptime(a.since, "%Y-%m-%d").timestamp()

    rows = []
    for path in sorted(glob.glob(os.path.join(a.root, "*", "*.jsonl"))):
        if a.project and a.project not in path:
            continue
        if since and os.path.getmtime(path) < since:
            continue
        # Cheap prefilter: skip files that never mention the skill.
        with open(path, errors="replace") as f:
            if not any("tasklist-run" in line for line in f):
                continue
        r = analyze_session(path, weights)
        if r:
            rows.append(r)
    if not rows:
        print("no tasklist-run sessions found", file=sys.stderr)
        return 1
    if a.json:
        json.dump(rows, sys.stdout, indent=2)
    else:
        report(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
