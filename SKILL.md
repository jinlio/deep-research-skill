---
name: deep-research
description: 用于需要多来源、可核验、可审计的深度调研任务。先进行 N 轮需求澄清，再复用宿主 Agent 已有的搜索/浏览工具，按证据账本和质量门禁生成报告。
version: 0.1.1
license: MIT
homepage: https://git.luckyguo.dpdns.org/chengge/deep-research-skill
---

# Deep Research

这是一个运行时无关的研究工作流。先阅读 `references/workflow.md`；运行时适配规则见 `profiles/`，工件字段见 `references/artifact-schema.md`。

角色输入/输出契约见 `references/agent-contracts.md`；宿主 Agent 必须优先复用其已有搜索、浏览、文件和 MCP 工具。

硬规则：

1. 正式搜索前完成需求澄清和用户确认；方向侦察只能标记为 `orientation_only`。
2. 搜索摘要不是证据；事实 claim 必须绑定可定位的原文片段或结构化数据。
3. 冲突、未知、检索失败和低置信度必须显式记录。
4. 只使用宿主 Agent 已有工具；不得假设或安装特定搜索服务。
5. 最终报告只能消费通过核验和反方审查的工件。
6. 默认只读；任何远程写入或发布都需要用户明确授权。

## 执行顺序

1. 读取 `references/workflow.md`、当前 runtime profile 和 `references/adapter-contract.md`。
2. 用宿主已有的 `search`/`web`/`browser` 工具做有限方向侦察（如需要），并记录为 `orientation_only`。
3. 完成 `clarification_rounds`（默认 `auto`，通常 2 轮，最多 5 轮），得到用户确认的 `research_spec.yaml`。
4. 按 Plan → Discover → Extract → Verify → Challenge → Synthesize → Audit 执行；每阶段只消费上一阶段通过门禁的工件。
5. 使用 `{baseDir}/scripts/run_gates.py <run-dir> --require-final --fail-on-pii` 验收，通过后才交付 `final_report.md` 和完整 run bundle。

没有子 Agent、结构化输出或持久 checkpoint 时，按照 profile 的降级路径串行执行；降级原因必须写入 `run_manifest.json`，不得假装完整模式。
