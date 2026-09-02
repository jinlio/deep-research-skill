---
name: deep-research
description: 用于需要多来源、可核验、可审计的深度调研任务。先进行 N 轮需求澄清，再复用宿主 Agent 已有的搜索/浏览工具，按证据账本和质量门禁生成报告。
---

# Deep Research

这是一个运行时无关的研究工作流。先阅读 `references/workflow.md`；运行时适配规则见 `profiles/`，工件字段见 `references/artifact-schema.md`。

硬规则：

1. 正式搜索前完成需求澄清和用户确认；方向侦察只能标记为 `orientation_only`。
2. 搜索摘要不是证据；事实 claim 必须绑定可定位的原文片段或结构化数据。
3. 冲突、未知、检索失败和低置信度必须显式记录。
4. 只使用宿主 Agent 已有工具；不得假设或安装特定搜索服务。
5. 最终报告只能消费通过核验和反方审查的工件。
6. 默认只读；任何远程写入或发布都需要用户明确授权。

