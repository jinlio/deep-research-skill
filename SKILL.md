---
name: deep-research
description: 跨 OpenClaw、HermesAgent、Codex、OpenCode 和 Claude Code 的深度调研工作流：先用 N 轮追问锁定问题，再建立 claim-evidence-source 证据账本，交叉核验冲突并通过确定性质量门禁，输出可审计、可恢复的研究报告。
version: 0.2.3
license: MIT
homepage: https://github.com/jinlio/deep-research-skill
---

# Deep Research Compatibility Entry Point

本文件只用于从源码仓库发现 skill。规范入口位于 `core/SKILL.md`；请先读取它，再按 `adapters/` 中对应 Agent 的入口选择工具和权限映射。

构建可安装包：

```bash
python scripts/build_adapters.py --output dist
```

不要把源码根目录直接当作 runtime 安装包；runtime 应安装 `dist/<runtime>/deep-research/`。
