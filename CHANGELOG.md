# Changelog

## 0.2.4 - 2026-09-04

- 优化根入口和各 runtime 入口的 marketplace 描述，加入典型失败场景、适用任务和最终交付物。
- 重写 README 首屏价值主张，补充研究流程、交付物和适用边界，降低首次使用门槛。

## 0.2.3 - 2026-09-04

- 重写各 runtime 入口 description，明确适用场景、核心差异和可审计交付结果，提升 marketplace 发现与转化。
- 同步根入口和 README 的版本信息。

## 0.2.2 - 2026-09-02

- 扩展 capability 协议，区分 `discover_sources`、`fetch_source`、`read_source`，并记录 `available`、`tested`、`mode`、`evidence`。
- 保留旧版 `search` 字段兼容映射，同时对未实际 smoke test 的能力给出警告。
- 将高影响 claim 的最小证据数和独立来源组要求落实到 `check_claim_coverage.py` 门禁。
- 补充 OpenCode 的多路径 discovery、on-demand 加载、权限过滤、last-wins 和无热重载边界。

## 0.2.1 - 2026-09-02

- 按 OpenClaw 上游文档补齐 workspace/project/personal/managed skill roots、allowlist、snapshot、ClawHub verify 和 `sessions_spawn` 完成事件语义。
- 按 HermesAgent 上游文档补齐项目技能 trust、`skill_view` 渐进加载、platform disabled、toolset 继承和 `delegate_task` 单任务/批量/恢复边界。
- 修正 OpenClaw/HermesAgent capability fixture 的说明，明确研究 bundle 与 runtime session state 的区别，不把协议 fixture 当作黑盒测试结果。
- 完成 OpenCode Desktop `1.18.26` 真实运行验证：skill discovery、两轮澄清、完整研究流程和六项 gates 通过；记录无搜索服务、无并行委派、无 durable checkpoint 的降级边界。

## 0.2.0 - 2026-09-02

- 将共享研究协议整理到 `core/`，为 OpenClaw、HermesAgent、Codex、OpenCode、Claude Code 和 generic 提供独立薄适配入口。
- 新增 `build_adapters.py`，生成带 references、scripts、profiles 的自包含 runtime 安装包。
- 新增 `test_runtime_matrix.py`，在临时目录构建并验证所有适配包及 capability fixture。
- 保留根目录兼容入口，并扩展 release check 与 capability fixture 覆盖。

## 0.1.1 - 2026-09-02

- 增加 Codex、OpenCode 和 Claude Code runtime profile 与 capability fixture。
- 增加五个平台 fixture 的统一 release 检查和单元测试覆盖。
- 记录 Codex smoke、Claude Code 模型调用限制和 OpenCode Desktop skill discovery 的真实验证边界。

## 0.1.0 - 2026-09-02

首个可发布版本：

- 固化 N 轮需求澄清、方向侦察隔离和证据优先研究工作流。
- 提供 claim-evidence-source 工件协议、冲突/未知状态和可恢复 run bundle。
- 提供来源、引用覆盖、澄清、manifest、secret/PII 和路径安全门禁。
- 补齐 OpenClaw、HermesAgent 和 generic runtime capability profile。
- 新增离线 capability probe、skill bundle validator、四类 benchmark 和 release check。
- 默认外部只读；没有子 Agent 或搜索能力时透明降级并披露限制。
