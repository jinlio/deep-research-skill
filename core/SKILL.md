---
name: deep-research
description: 用于竞品、行业、方案选型、风险判断和学术/资料调研的纯工作流。只复用宿主已授权工具，先 N 轮追问明确目标，再保存原文证据、核验冲突并通过质量门禁，交付可审计、可恢复的报告和证据包。
version: 0.2.7
license: MIT
homepage: https://github.com/jinlio/deep-research-skill
---

# Deep Research

这是一个运行时无关的研究工作流。先阅读 `references/workflow.md`；运行时适配规则见 `profiles/`，工件字段见 `references/artifact-schema.md`。

角色输入/输出契约见 `references/agent-contracts.md`；宿主 Agent 必须优先复用其已有搜索、浏览、文件和 MCP 工具。

硬规则：

1. 正式搜索前完成需求澄清和用户确认；方向侦察只能标记为 `orientation_only`。
2. 搜索摘要不是证据；事实 claim 必须绑定可定位的原文片段或结构化数据。高影响 claim 默认需要至少两条来自不同 `independence_group` 的 evidence。
3. 冲突、未知、检索失败和低置信度必须显式记录。
4. 只使用宿主 Agent 已有工具；不得假设或安装特定搜索服务。
5. 最终报告只能消费通过核验和反方审查的工件。
6. 默认只读；不得更改权限、审批、沙箱、工具配置、网络配置或凭据。任何远程写入或发布都需要用户明确授权。

## 执行顺序

1. 读取 `references/workflow.md`、当前 runtime profile 和 `references/adapter-contract.md`。
2. 用宿主已有的来源发现/抓取/浏览工具做有限方向侦察（如需要），并记录为 `orientation_only`；不要把工具存在误认为 capability 已测试。
3. 按深度模式完成澄清并得到用户确认的 `research_spec.yaml`：`quick` 0 轮（假设写入规格并展示）、`standard` 1 轮、`deep` 2–3 轮；显式 `clarification_rounds: N` 优先。用户可随时说"按当前理解开始"提前结束。
4. 按 Plan → Discover → Extract → Verify → Challenge → Synthesize → Audit 执行；每阶段只消费上一阶段通过门禁的工件。
5. 使用适配包内置的 gate script，以 `--require-final --fail-on-pii` 验收，通过后才交付 `final_report.md` 和完整 run bundle。

没有子 Agent、结构化输出或持久 checkpoint 时，按照 profile 的降级路径串行执行；降级原因必须写入 `run_manifest.json`，不得假装完整模式。
