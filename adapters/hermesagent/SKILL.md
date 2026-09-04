---
name: deep-research
description: HermesAgent 深度调研工作流：适合竞品、行业、方案比较、风险判断和资料研究。先 N 轮追问再检索，用多来源证据账本核验冲突，最后通过质量门禁交付可审计报告。
version: 0.2.3
license: MIT
homepage: https://github.com/jinlio/deep-research-skill
---

# Deep Research for HermesAgent

先读取 `references/workflow.md`、`references/adapter-contract.md`、`profiles/hermesagent.md` 和 `references/agent-contracts.md`。

严格按核心工作流执行：先完成 N 轮需求澄清和用户确认，再进行正式搜索；所有事实 claim 必须绑定可定位证据；冲突、未知和检索失败必须显式记录；最终交付前运行 `scripts/run_gates.py`。

复用 HermesAgent 已有的 web、file、skills 和 `delegate_task` 能力。缺少某项 capability 时，按 profile 串行降级并在 `run_manifest.json` 记录原因。默认外部只读，只允许写入 `research-run/`。
