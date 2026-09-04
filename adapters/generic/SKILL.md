---
name: deep-research
description: 通用 Agent 深度调研 skill：把“搜了很多却答错问题”变成可复核结论。适合竞品、行业、方案选型、风险和资料研究；N 轮追问锁定目标，多来源原文核验，显式披露冲突与缺口，交付可审计报告和可恢复证据包。
version: 0.2.4
license: MIT
homepage: https://github.com/jinlio/deep-research-skill
---

# Deep Research for Generic Agents

先读取 `references/workflow.md`、`references/adapter-contract.md`、`profiles/generic.md` 和 `references/agent-contracts.md`。

严格按核心工作流执行：先完成 N 轮需求澄清和用户确认，再进行正式搜索；所有事实 claim 必须绑定可定位证据；冲突、未知和检索失败必须显式记录；最终交付前运行 `scripts/run_gates.py`。

只复用宿主实际暴露的搜索、浏览、文件、shell、MCP 和 delegation 能力。任何缺失都必须按 profile 降级并在 `run_manifest.json` 记录。默认外部只读，只允许写入 `research-run/`。
