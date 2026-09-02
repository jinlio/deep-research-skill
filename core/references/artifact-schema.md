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

