---
name: deep-research
description: OpenClaw 纯工作流深度调研：不绑定模型或搜索服务，把宿主工具编排成可复核流程。适合竞品、行业、选型、风险和资料研究；N 轮追问、多来源原文核验、冲突披露，交付可审计报告和证据包。
version: 0.2.5
license: MIT
homepage: https://github.com/jinlio/deep-research-skill
---

# Deep Research for OpenClaw

先读取 `references/workflow.md`、`references/adapter-contract.md`、`profiles/openclaw.md` 和 `references/agent-contracts.md`。

严格按核心工作流执行：先完成 N 轮需求澄清和用户确认，再进行正式搜索；所有事实 claim 必须绑定可定位证据；冲突、未知和检索失败必须显式记录；最终交付前运行 `scripts/run_gates.py`。

复用 OpenClaw 已有的搜索、浏览、文件和 `sessions_spawn` 能力。缺少某项 capability 时，按 profile 串行降级并在 `run_manifest.json` 记录原因。默认外部只读，只允许写入 `research-run/`。
