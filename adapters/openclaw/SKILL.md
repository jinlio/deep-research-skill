---
name: deep-research
description: OpenClaw 纯工作流深度调研：不绑定模型或搜索服务，只复用已获授权的宿主工具。适合竞品、行业、选型、风险和资料研究；N 轮追问、多来源原文核验、冲突披露，交付可审计报告和证据包。
version: 0.3.0
license: MIT
homepage: https://github.com/jinlio/deep-research-skill
---

# Deep Research for OpenClaw

先读取 `references/workflow.md`、`references/adapter-contract.md`、`profiles/openclaw.md` 和 `references/agent-contracts.md`。

严格按核心工作流执行：先完成 N 轮需求澄清和用户确认，再进行正式搜索；所有事实 claim 必须绑定可定位证据；冲突、未知和检索失败必须显式记录；最终交付前运行 `scripts/run_gates.py`。

只复用当前 OpenClaw 会话已经可用的搜索、浏览、文件和 `sessions_spawn` 能力。不得修改权限、审批、沙箱、skill/tool allowlist、网络配置或凭据；不得安装、启用或调用会话中未暴露的工具。缺少某项 capability 时，按 profile 串行降级并在 `run_manifest.json` 记录原因。默认外部只读，只允许在 `research-run/` 写入工件；子 Agent 不得获得父会话之外的工具或写入范围。
