---
name: deep-research
description: 用于竞品、行业、方案比较、风险判断和学术/资料调研等需要多来源核验的任务。先进行 N 轮需求澄清，再复用宿主工具建立证据账本、处理冲突并通过质量门禁，生成可审计报告。
version: 0.2.3
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
6. 默认只读；任何远程写入或发布都需要用户明确授权。

## 执行顺序

1. 读取 `references/workflow.md`、当前 runtime profile 和 `references/adapter-contract.md`。
2. 用宿主已有的来源发现/抓取/浏览工具做有限方向侦察（如需要），并记录为 `orientation_only`；不要把工具存在误认为 capability 已测试。
3. 完成 `clarification_rounds`（默认 `auto`，通常 2 轮，最多 5 轮），得到用户确认的 `research_spec.yaml`。
4. 按 Plan → Discover → Extract → Verify → Challenge → Synthesize → Audit 执行；每阶段只消费上一阶段通过门禁的工件。
5. 使用适配包内置的 gate script，以 `--require-final --fail-on-pii` 验收，通过后才交付 `final_report.md` 和完整 run bundle。

没有子 Agent、结构化输出或持久 checkpoint 时，按照 profile 的降级路径串行执行；降级原因必须写入 `run_manifest.json`，不得假装完整模式。
