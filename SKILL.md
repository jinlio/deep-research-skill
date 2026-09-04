---
name: deep-research
description: 跨 OpenClaw、HermesAgent、Codex、OpenCode、Claude Code 的可审计深度调研：先 N 轮追问明确决策目标，再用多来源原文证据核验每条结论、标记冲突与未知，输出可恢复的研究报告和证据包。
version: 0.2.4
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
