# Team workflow

## Ownership

| Work package | Owner | Review |
| --- | --- | --- |
| Pipeline and execution | Daud | Bobby for integrity; Emi for condition fidelity |
| Protocol and interpretation | Emi | Bobby and Daud |
| Validation and closest work | Bobby_Jenkins | Daud and Emi |
| Analysis and figures | Chandni | Bobby for numbers; Emi for interpretation |

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
