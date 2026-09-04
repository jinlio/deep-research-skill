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
