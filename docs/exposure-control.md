# Guru's exposure control: implementation draft

Status: added as a provisional fifth arm. Scientific review by Emi/Guru pending.
No live model harness, checkpoint serialization or experiment runner is implemented yet.

## Contrast

Compare `reset_b` (A retains history, B reset, normal interaction) with
`reset_b_neutral_peer_replay` (same reset, reviewed neutral interaction delivered
to B). The four core arms remain unchanged. The mirrored reset-A exposure arm is
deferred to avoid doubling scope before the pilot.

This is a communication-content intervention, not complete absence of exposure.
Verdict feedback, rewards and other observable actions remain potential influence
channels. Do not label this a definitive behavioral-transmission test.

## Implemented primitives

`build_branches` deep-copies an in-memory checkpoint and applies each reset once.
New history can accumulate afterward. The adapter remains responsible for all
runtime state not represented in that checkpoint, including files and sessions.

`route_peer_message` separates permitted task evidence from peer interaction.
The exposure arm changes only A-to-B peer interaction using a pre-reviewed,
slot-matched neutral fixture. Task evidence must match exactly or routing fails.
The communication cap applies to both messages; there is no silent truncation.
The returned audit event records condition, direction, slot, review reference,
fingerprints and message lengths. The caller must persist it alongside original
and delivered content in access-controlled raw logs.

No LLM rewrites, automatic suspiciousness classifier or live provider is added.
The review-reference check is an operational guard, not proof of scientific approval.

## Required before live execution

- [ ] Emi/Guru specify and approve what counts as evidence versus interaction.
- [ ] Identify the neutral fixture source and matching by task, episode and turn.
- [ ] Check that the replacement does not introduce legitimate evidence, hidden
      verdict cues or a new instruction to comply.
- [ ] Define how content, length and naturalness differences affect interpretation.
- [ ] Inspect feedback and tool channels; declare which exposure remains.
- [ ] Adapt real upstream messages without leaking the experimental condition.
- [ ] Validate restoration, filesystem isolation and request assembly in the live harness.
- [ ] Persist routing events and raw delivery records; test the analysis schema.
- [ ] Predeclare the secondary newcomer outcome: B's directional unsupported
      acceptance. Mutual approval and recurrence remain additional outcomes.
- [ ] Update inference budget: fifth-arm tail adds 25% to continuation episodes,
      not necessarily 25% to total tokens or whole-project cost.

Do not run a generically generated neutral reply and interpret any difference as
transmission. If legitimate evidence cannot be separated and matched, keep this
arm blocked, redesign it, or narrow the claim.

## Offline test command (PowerShell)

```powershell
$env:PYTHONPATH = 'src'
python -m unittest discover -s tests -v
```

These are engineering fixture tests only, not LLM results or pilot findings.
