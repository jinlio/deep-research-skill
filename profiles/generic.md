# Generic Runtime Profile

当宿主不是 OpenClaw、HermesAgent、Codex、OpenCode 或 Claude Code，按 `references/adapter-contract.md` 提供的七项抽象能力运行。先调用 `scripts/probe_runtime.py` 验证能力，再选择完整、多 Agent 或串行降级模式。

最小实现必须能：读取 `SKILL.md` 和 references、调用宿主已有只读搜索/浏览工具、在 run 目录追加 JSONL、运行 audit。缺少 `delegate` 时串行执行；缺少 `checkpoint` 时在会话结束导出 run bundle；缺少搜索能力时仅使用用户材料并披露覆盖限制。
