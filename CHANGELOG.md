# Changelog

## 0.2.0 - 2026-09-02

- 将共享研究协议整理到 `core/`，为 OpenClaw、HermesAgent、Codex、OpenCode、Claude Code 和 generic 提供独立薄适配入口。
- 新增 `build_adapters.py`，生成带 references、scripts、profiles 的自包含 runtime 安装包。
- 新增 `test_runtime_matrix.py`，在临时目录构建并验证所有适配包及 capability fixture。
- 保留根目录兼容入口，并扩展 release check 与 capability fixture 覆盖。

## 0.1.1 - 2026-09-02

- 增加 Codex、OpenCode 和 Claude Code runtime profile 与 capability fixture。
- 增加五个平台 fixture 的统一 release 检查和单元测试覆盖。
- 记录 Codex smoke、Claude Code 认证额度和 OpenCode Desktop skill discovery 的真实验证边界。

## 0.1.0 - 2026-09-02

首个可发布版本：

- 固化 N 轮需求澄清、方向侦察隔离和证据优先研究工作流。
- 提供 claim-evidence-source 工件协议、冲突/未知状态和可恢复 run bundle。
- 提供来源、引用覆盖、澄清、manifest、secret/PII 和路径安全门禁。
- 补齐 OpenClaw、HermesAgent 和 generic runtime capability profile。
- 新增离线 capability probe、skill bundle validator、四类 benchmark 和 release check。
- 默认外部只读；没有子 Agent 或搜索能力时透明降级并披露限制。
