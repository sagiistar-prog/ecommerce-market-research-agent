# Maintenance log

## 0.4.0 — 2026-09-18

- Added local hypothesis import, citation readback, explicit reviewer choices and reasons, undo, JSON restore and Markdown export.
- Bound choices to the exact evidence and proposal snapshots; stale proposals and fabricated quotes fail validation.
- Added browser task regression in CI at desktop and mobile widths. Safe Demo remains network-free; browser tooling is development-only.
- No customer results or measured product outcomes are inferred from a completed review. [Acceptance](docs/hypothesis-review-acceptance.md).

## 0.3.0 — 2026-09-18

- Replaced fixed desk-product advice with category-independent evidence analysis.
- Added declared comparable groups, missing-price handling, source metadata and synthetic/provided separation.
- Added exact snapshot-bound citation checks for host-authored product hypotheses.
- Added CSV import with undo, evidence navigation, stale-result warnings and structured export.
- Output schema advances to 2.0; input remains compatible. Ungrouped legacy rows remain visible but do not create price benchmarks.
- Validation scope and limitations: [acceptance](docs/evidence-review-acceptance.md).

## 0.2.0 — 2026-09-17

- Added a versioned Codex plugin manifest with the existing Skill.
- Added validated JSON input/output, a fictional input fixture and an explicit artifact export path.
- Documented the actual offline capability and its limitations.
- Added executable contract and regression checks; see `tests/`.
- Product decision: 先验证输入列，再生成报告。报告绑定提交时的输入版本，修改输入后提示重新生成，避免导出过期结论。

The version labels a repository iteration, not a hosted product launch or a marketplace release.

## 2026-09-17 Product reliability release

从商品样本到研究初稿。补齐产品案例、能力证据、指标契约、开源取舍与持续检查。验证范围和未验收项见 docs/validation.md。
