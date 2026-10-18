"""Check a real task pair offline or explicitly launch one upstream episode.

This adapter delegates the live protocol to pinned upstream code. It does not
connect the reset/exposure primitives to that protocol yet.
"""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = ROOT / "vendor" / "agent-collusion"
UPSTREAM_REVISION = "5afb2c595aa3eff6b9b829a032f4f117b36ee54d"
MANIFEST = ROOT / "configs" / "one-episode.json"


def check_upstream():
    if not (UPSTREAM / "experiments" / "runner.py").is_file():
        raise ValueError("Initialize the upstream submodule: git submodule update --init")
    revision = subprocess.check_output(
        ["git", "-C", str(UPSTREAM), "rev-parse", "HEAD"], text=True
    ).strip()
    if revision != UPSTREAM_REVISION:
        raise ValueError("Upstream revision differs from the reviewed pin")
    dirty = subprocess.check_output(
        ["git", "-C", str(UPSTREAM), "status", "--porcelain", "--untracked-files=no"],
        text=True,
    )
    if dirty.strip():
        raise ValueError("Tracked upstream changes must be reviewed before execution")


def validate_pair():
    """Exercise upstream grading with oracle fixtures, not model-generated answers."""
    check_upstream()
    if str(UPSTREAM) not in sys.path:
        sys.path.insert(0, str(UPSTREAM))
    from experiments.tasks import read_task_pairs
    from experiments.evaluation import _reference_sql_rows, evaluate_data_search_artifact
    from experiments.protocol.submissions import _answer_format_error

    pairs = read_task_pairs(MANIFEST, UPSTREAM)
    if len(pairs) != 1:
        raise ValueError("Engineering smoke manifest must contain exactly one episode")
    report = {"mode": "offline-oracle-grader-check", "upstream_revision": UPSTREAM_REVISION,
              "live_model_calls": 0, "agents": {}}
    for agent, task in zip(("A", "B"), pairs[0]):
        rows = _reference_sql_rows(task, UPSTREAM)
        answer = [{key: row[key] for key in task["answer_key"]} for row in rows]
        if len(rows) != task["reference_row_count"] or not answer:
            raise ValueError("Reference count mismatch or empty task fixture")

        def grade(value):
            return evaluate_data_search_artifact(
                task, {"data_search_artifact": {"answer": json.dumps(value)}}, UPSTREAM
            )["quality_verdict"]

        extra_row = {key: "NONEXISTENT_FIXTURE_ID" for key in task["answer_key"]}
        checks = {
            "correct_passes": grade(answer) == "pass",
            "reordered_passes": grade(list(reversed(answer))) == "pass",
            "omitted_row_fails": grade(answer[:-1]) == "fail",
            "duplicate_row_fails": grade(answer + [answer[0]]) == "fail",
            "extra_row_fails": grade(answer + [extra_row]) == "fail",
            "wrong_format_rejected": _answer_format_error(
                {"task_type": "data_search"}, {"answer_key": task["answer_key"]}, "[1]"
            ) is not None,
            "missing_submission_fails": evaluate_data_search_artifact(task, {}, UPSTREAM)["quality_verdict"] == "fail",
        }
        if not all(checks.values()):
            raise ValueError(f"Upstream grading regression for {task['task_id']}: {checks}")
        report["agents"][agent] = {
            "task_id": task["task_id"], "prompt": task["search_prompt"],
            "answer_key_columns": task["answer_key"], "reference_row_count": len(rows),
            "checks": checks,
        }
    return report


def live_command(model, output_dir, max_output_tokens=4096):
    """Restrict this first launcher to explicitly named free OpenRouter routes."""
    if not model.startswith("openrouter/") or not model.endswith(":free"):
        raise ValueError("This launcher accepts only explicit openrouter/...:free routes")
    if max_output_tokens < 1:
        raise ValueError("Output-token cap must be positive")
    return [
        sys.executable, "-m", "experiments.runner",
        "--manifest", str(MANIFEST),
        "--alice-model", model, "--bob-model", model,
        "--alice-reasoning-effort", "default", "--bob-reasoning-effort", "default",
        "--alice-max-output-tokens", str(max_output_tokens),
        "--bob-max-output-tokens", str(max_output_tokens),
        "--max-rounds", "5", "--char-limit", "200", "--verdict-policy", "raw-only",
        "--output-dir", str(Path(output_dir).resolve()), "--run-label", "one-episode-smoke",
    ]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", help="Explicit LiteLLM route, openrouter/<model>:free")
    parser.add_argument("--execute", action="store_true", help="Opt in to live model requests")
    parser.add_argument("--output-dir", default=str(ROOT / "results" / "one-episode"))
    parser.add_argument("--max-output-tokens", type=int, default=4096)
    args = parser.parse_args()
    try:
        report = validate_pair()
        print(json.dumps(report, indent=2))
        if not args.execute:
            print("Offline checks only. No agent episode or model call was executed.")
            return
        if not args.model:
            raise ValueError("Choose a model explicitly with --model")
        command = live_command(args.model, args.output_dir, args.max_output_tokens)
        if not os.environ.get("OPENROUTER_API_KEY"):
            raise ValueError("Set OPENROUTER_API_KEY in the environment, not in a tracked file")
        if importlib.util.find_spec("litellm") is None:
            raise ValueError("Install the pinned upstream runtime requirements in an isolated environment")
        env = os.environ.copy()
        env["PYTHONPATH"] = str(UPSTREAM)
        result = subprocess.run(command, cwd=UPSTREAM, env=env, check=False)
        if result.returncode:
            raise ValueError(f"Upstream episode runner exited with code {result.returncode}")
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        parser.exit(2, f"Error: {error}\n")


if __name__ == "__main__":
    main()
