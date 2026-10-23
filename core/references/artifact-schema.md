# 工件协议

每次运行建议生成：

```text
research-run/
  research_spec.yaml
  clarification_log.jsonl
  orientation_notes.md
  plan.yaml
  sources.jsonl
  evidence.jsonl
  claims.jsonl
  conflicts.jsonl
  agent_packets/
  review.md
  audit.json
  run_manifest.json
  final_report.md
```

核心关系：`claim -> evidence -> source`。原始来源不可覆盖；JSONL 追加写入；最终报告可从账本重建。

Claim 可选字段：`impact: low|medium|high` 与 `minimum_evidence`。未显式设置时，`high` 影响 claim 默认至少需要 2 条证据，其余 resolved claim 至少 1 条。高影响 claim 的证据必须来自至少两个不同 `independence_group`（缺省使用 source_id）。

`research_spec.yaml` 顶层字段 `depth: quick|standard|deep` 决定默认澄清预算（`quick` 0 轮、`standard` 1 轮、`deep` 2–3 轮）；显式 `clarification_rounds: N` 优先于 depth 默认值。

`verification.jsonl`（可选）由 `scripts/verify_evidence.py` 生成，每行记录一条 evidence 的回贴核验结果：`evidence_id`、`source_id`、`status: verified|verified_fuzzy|mismatch|unavailable|unverifiable`、`method`、`ratio`、`content_sha256`、`checked_at`、`error`。
