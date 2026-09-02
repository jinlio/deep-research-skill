# Scripts

计划提供以下确定性检查：

- `validate_artifacts`：工件 schema 和引用关系。
- `check_claim_coverage`：报告 claim 到 evidence 的覆盖率。
- `check_clarification`：N 轮澄清、最终确认和方向侦察隔离。
- `check_sources`：URL、来源去重和失效状态。
- `scan_sensitive_data`：secret/PII 扫描。
- `check_run_manifest`：运行、重试、成本和恢复记录。
- `probe_runtime`：验证 runtime capability JSON，并给出完整/降级模式。
- `validate_skill`：验证 `SKILL.md` frontmatter、引用文件和路径安全。
- `evaluate_benchmark`：对 golden cases 的 claim 覆盖、拒答和冲突召回做确定性评分。
- `release_check`：一次性执行 skill、fixture、capability、benchmark 和单元测试验收。
- `build_adapters`：从 `core/`、`adapters/` 和仓库级 profiles 生成各 runtime 的完整可安装包。
- `test_runtime_matrix`：在临时目录构建并验证所有适配包与 capability fixture。

统一运行：`python scripts/run_gates.py <research-run> --require-final --fail-on-pii`

创建新运行：`python scripts/init_run.py research-run --question "问题" --goal "决策目标"`
创建后可先运行预检：`python scripts/run_gates.py research-run --preflight`

运行时能力探测输入为 JSON，格式见 `profiles/capabilities/README.md`。探测只读取输入，不调用网络、不写 runtime 配置。
