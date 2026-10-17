# Collusion Reset

Testing whether selective memory resets break established collusive behavior in LLM agents.

**Status: research planning and repository setup.** No experiment pipeline, validated results, or findings are released here yet.

## Research question

Once two agents repeatedly approve each other's work without the required evidence, does resetting one agent's history stop the pattern, or does retaining the other agent's history help it return?

Working project title: **Does Replacing One Agent Break a Collusive Convention?** The core experiment tests history resets; replacing an agent with a different model is an optional extension and has not been implemented.

Prepared for the [AI Collusion Research Sprint](https://apartresearch.com/sprints/ai-collusion-research-sprint-2026-10-23-to-2026-10-25). Proposed primary track: Collusion Carriers and Countermeasures.

## Proposed experiment

Build on the peer-verification setting from [Shi et al., Emergent Collusion in Long-Horizon LLM Agent Interaction](https://arxiv.org/abs/2609.24967), with [upstream code](https://github.com/SALT-NLP/agent-collusion).

Agents complete separate tasks and evaluate each other's work. The protocol requires the complete execution log before approval. Restricted communication prevents complete log exchange, creating tension between protocol compliance and rewards for correct judgments.

At a predeclared checkpoint, branch the same interaction into four conditions:

| Condition | Agent A history | Agent B history |
| --- | --- | --- |
| Continue | Retain | Retain |
| Reset A | Reset | Retain |
| Reset B | Retain | Reset |
| Reset both | Reset | Reset |

All branches receive the same future task pairs, rules, reward definition and communication limits. A history reset must not remove current task information or leak old context through summaries, caches or shared mutable state.

Primary question: how does post-checkpoint unsupported mutual approval differ between joint and selective resets? Report each single-reset comparison separately. The independent unit is the starting trajectory, not its branches, episodes or model calls.

**Unsupported approval is a protocol violation, not automatically an incorrect answer or proof of agreement.** Stronger interpretations require evidence of peer influence and appropriate controls.

See the [proposed protocol](docs/protocol.md) and [team workflow](CONTRIBUTING.md). Settings remain provisional until pilot validation and protocol freeze.

## Repository layout

```text
configs/         Experiment configuration files (not implemented yet)
docs/            Protocol, decisions and research notes
src/             Pipeline implementation (not implemented yet)
tests/           Integrity and analysis tests (not implemented yet)
data/            Data-handling guidance; raw runs are not committed
results/         Guidance for validated analysis outputs
```

## Getting started

There is no runnable experiment command or dependency installation yet. First establish model access and validate faithful checkpoint restoration, branch isolation and deterministic grading. Do not assume a free chat interface supplies automated API access.

Keep the first implementation small: one model, one task family and four history conditions. No dashboard or database is required for the core study. No paid inference or automatic paid fallback is authorized under the current zero-new-spend constraint.

## Team

- **Daud:** pipeline, execution and scientific integration.
- **Emi:** methodology, endpoint definitions and behavioral interpretation.
- **Bobby_Jenkins:** validation, closest-work checks and independent metric verification.
- **Chandni:** log processing, analysis, figures and result ledger.

## Reproducibility and attribution

Record exact model routes, prompts, code revisions, seeds where supported, attempted-run counts, errors, usage and deviations. Keep raw outputs immutable and trace every reported number to validated analysis.

This repository is an independent planned extension, not the upstream implementation. No upstream source code has been copied in this initial setup. Preserve upstream licenses and attribution when code or data is reused. Distinguish pre-sprint preparation from work performed during the sprint.

## Safety and limitations

Use synthetic tasks and avoid real sensitive data. Never commit credentials, private messages or unreviewed raw logs. Model-generated executable code requires an appropriate sandbox before execution.

This study cannot establish general prevalence of collusion, hidden intent, or the effectiveness of model replacement from history-reset results alone. No findings are claimed at this stage.
