# Source and Scope

- Requested review commit: `2c0d06089f558c537069e80b6b4015891cbf47e6` in `daudibrahimhasan/collusion-reset`.
- The raw fixture's `study.json` declares `code_revision=2955c582afe9d405005ce7676ace5dd2e0526a98` and `code_dirty=true`. That SHA is the parent of the requested review commit. Exact generation from commit `2c0d060` is therefore not verified; request the dirty diff/snapshot or regenerate the fixture from a clean checkout.
- The checker was written as a standalone Python standard-library script and does not import `collusion_reset.study.episode_metrics`, `summarize`, or other pipeline metrics.
- Raw fixture and reference-analysis ZIPs are intentionally not duplicated in this bundle. Supply the two extracted directories via CLI arguments as documented in README.md.
- All results are synthetic, not agent/model findings.
