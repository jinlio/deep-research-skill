# Scripts

计划提供以下确定性检查：

- `validate_artifacts`：工件 schema 和引用关系。
- `check_claim_coverage`：报告 claim 到 evidence 的覆盖率。
- `check_clarification`：N 轮澄清、最终确认和方向侦察隔离。
- `check_sources`：URL、来源去重和失效状态。
- `scan_sensitive_data`：secret/PII 扫描。
- `check_run_manifest`：运行、重试、成本和恢复记录。

统一运行：`python scripts/run_gates.py <research-run> --require-final --fail-on-pii`

创建新运行：`python scripts/init_run.py research-run --question "问题" --goal "决策目标"`
创建后可先运行预检：`python scripts/run_gates.py research-run --preflight`
