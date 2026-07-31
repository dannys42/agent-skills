# Local CLI integration measurements

Measured on 2026-07-31 with Python 3.14.6 on macOS 26.5.2 (arm64).

Command, run from `${REPO_ROOT}`:

```bash
RUN_SKILL_OPTIMIZER_BENCHMARKS=1 python3 -m unittest \
  plugins.skill-development-optimizer.tests.test_cli_integration.IntegratedCliTests.test_local_cli_medians_are_below_one_second_for_existing_plugins \
  -v
```

The test copied each existing plugin into a temporary Git repository, generated
a repository-relative optimizer configuration using the full example
distributable include set, and invoked each CLI ten times from a separate
working directory. Missing optional directories selected no files while
`SKILL.md` remained selected. Durations used `time.perf_counter()` and the
table reports the median of those ten sequential subprocess invocations.

| Temporary plugin fixture | CLI | Median seconds |
|---|---|---:|
| `swift-testing` | `inspect_skill` | 0.062131 |
| `swift-testing` | `classify_change` | 0.096422 |
| `swift-testing` | `hash_artifact` | 0.069894 |
| `swift-design-patterns` | `inspect_skill` | 0.062993 |
| `swift-design-patterns` | `classify_change` | 0.094278 |
| `swift-design-patterns` | `hash_artifact` | 0.073381 |

These values describe only this local run and environment.
