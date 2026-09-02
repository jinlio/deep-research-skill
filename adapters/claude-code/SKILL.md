---
name: deep-research
description: Claude Code 上的多来源、可核验、可审计深度调研工作流。
version: 0.2.0
license: MIT
homepage: https://git.luckyguo.dpdns.org/chengge/deep-research-skill
---

# Deep Research for Claude Code

先读取 `references/workflow.md`、`references/adapter-contract.md`、`profiles/claude-code.md` 和 `references/agent-contracts.md`。

严格按核心工作流执行：先完成 N 轮需求澄清和用户确认，再进行正式搜索；所有事实 claim 必须绑定可定位证据；冲突、未知和检索失败必须显式记录；最终交付前运行 `scripts/run_gates.py`。

复用当前 Claude Code 会话已有的搜索、浏览、文件、shell、MCP 和 sub-agent 能力。没有 delegation 或搜索能力时按 profile 串行降级并披露覆盖限制。默认外部只读，只允许写入 `research-run/`。
