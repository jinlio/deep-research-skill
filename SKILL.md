---
name: deep-research
description: 多 Agent 通用深度调研 skill 的兼容入口；正式安装请使用 adapters 构建出的 runtime 包。
version: 0.2.2
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
