# First database task pair

The upstream harness is pinned as a Git submodule at
`5afb2c595aa3eff6b9b829a032f4f117b36ee54d`. Its MIT license remains in the
submodule. Clone this repository with `--recurse-submodules`, or initialize it:

```powershell
git submodule update --init
$env:PYTHONPATH = 'src'
python -m collusion_reset.episode_smoke
python -m unittest discover -s tests -v
```

## Selected tasks

- A: `data_01_support_case_escalations` (8 reference rows).
- B: `data_14_procurement_finance_review` (8 reference rows).

Both are existing SQLite data-search tasks, with different search requests and
answer keys determined by their manifests. This hand-selected pair is for
engineering validation, not a representative sample or an approved study sequence.

The offline command runs upstream reference queries and tests the upstream grader
on correct, reordered, missing, extra, duplicate and malformed answer fixtures.
It also checks a missing submission. It makes no model calls. Oracle answers stay
in the evaluator; the live command passes only task IDs to the upstream loader.

## Live one-episode path

Use a dedicated virtual environment and install the upstream's pinned runtime:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r vendor/agent-collusion/requirements.txt
$env:PYTHONPATH = 'src'
# Set OPENROUTER_API_KEY securely in your environment; do not commit it.
.\.venv\Scripts\python.exe -m collusion_reset.episode_smoke --execute --model 'openrouter/<chosen-model>:free'
```

Replace the placeholder with a currently available, team-selected route. No model
has been selected or API quota verified. This wrapper refuses non-free model
routes and requires explicit `--execute`; account/provider billing safeguards
must still be verified. No paid fallback or paid preflight is authorized.

The live adapter delegates task/tool execution, five communication rounds,
verdicts, grading, feedback, reflection and output saving to the pinned upstream
runner. Its API preflight may make extra requests. The 4096-token output cap is
an engineering default, not the original paper's setting; inspect errors and
cap hits, and re-pilot approved changes before claiming comparability.

## Inspect the output before calling it successful

The upstream writes `run.json` under the output root. Check both task artifacts,
tool traces, delivered messages, valid/forced/missing verdict provenance,
independent grades, rewards, feedback, reflections, errors and usage. A zero
process exit is not sufficient evidence of a valid episode.

Live execution is not validated by the offline oracle checks or unit tests. This
launcher does not yet wire history-reset branching or the provisional exposure
control into the live harness. It cannot acquire a three-episode checkpoint from
its single task pair. Do not use this one-episode smoke test as a main experiment.

For the separate checkpoint study runner with four-arm reset integration, see
[setup-and-run.md](setup-and-run.md). That adapter is offline-tested, not live-validated.
