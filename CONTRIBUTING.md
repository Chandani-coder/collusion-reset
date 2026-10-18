# Team workflow

## Ownership

| Work package | Owner | Review |
| --- | --- | --- |
| Pipeline and execution | Daud | Salor for security/isolation; Emi for condition fidelity |
| Protocol and interpretation | Emi | Guru and Daud |
| Exposure controls and closest work | Guru | Daud and Emi |
| Analysis and independent metric checks | Chandni | Emi for interpretation; Daud for integration |
| Security and adversarial setup validation | Salor | Daud for implementation; Guru for independent review |

Work packages are proposed until each member confirms availability. Salor pairs with Daud on setup and Guru on validation; he does not replace the independent grading or statistical checks. All members may contribute research, model suggestions and the paper. Emi and Guru coordinate episode selection. See [the detailed handoff](docs/team-handoff.md).

## Salor's first deliverable

A reproducible security test report, not a general penetration test:

- [ ] Seed historical context with synthetic markers and check that reset branches do not retain them through prompts, summaries, caches or shared files.
- [ ] Mutate one branch's state and verify that other branches remain unchanged.
- [ ] Check that current instructions and task inputs remain intact after reset.
- [ ] Check logs and configuration examples for credential exposure.
- [ ] Review any model-generated code execution boundary before enabling it.
- [ ] Record failing tests, reproducible steps and fixes for review by Daud and Guru.

These are engineering integrity tests, not empirical evidence of collusion. Restrict testing to the team's local/sandboxed setup; do not test external provider infrastructure or use real secrets as markers.

## First milestone

- [ ] Confirm available automated inference access and limits without committing credentials.
- [ ] Inspect the upstream harness and document attribution.
- [ ] Validate task competence and checkpoint eligibility in a small pilot.
- [ ] Restore one checkpoint faithfully and clone isolated branches.
- [ ] Prove reset branches remove history but preserve current rules and tasks.
- [ ] Agree on the output schema and test malformed or missing outputs.
- [ ] Review the protocol and freeze main-run settings before inspecting main-run effects.

## Changes and reviews

Use short-lived branches and reviewable pull requests. Include what changed, how it was checked and any effect on the protocol or outputs. Do not force-push shared branches or overwrite another member's work.

Record methodological decisions and deviations in `docs/decisions.md`. Do not silently change a frozen endpoint or rerun data to obtain a more favorable result.

Source of truth: immutable raw outputs, validated analysis/result ledger, then figures and manuscript. A non-pipeline reviewer independently verifies headline numbers.

Keep code here and large raw artifacts in an access-controlled shared folder. Only release data after privacy, licensing and reproducibility review. Do not include keys, passwords or private team discussion in issues or commits.
