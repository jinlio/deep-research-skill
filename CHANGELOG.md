# Changelog

## 0.3.0 - 2026-10-24

- 新增引用回贴核验引擎 `scripts/verify_evidence.py`：重新抓取来源并逐条定位 evidence 原文摘录，生成 `verification.jsonl`（verified / verified_fuzzy / mismatch / unavailable / unverifiable）；网络模式仅允许 http/https，拒绝解析到环回/私有/保留地址的主机；本地来源限定在 run 目录与工作目录内。
- 门禁新增 `--verify-network` 与 `--require-verified`：高影响 claim 必须至少有一条回贴成功的证据，任何 mismatch 直接失败。
- 落地深度模式：`quick`（0 轮澄清，假设显式入档）/ `standard`（1 轮）/ `deep`（2–3 轮）；`check_clarification.py` 按 depth 设默认轮次上限，显式 `clarification_rounds` 仍然优先。
- 仓库根目录可直接作为 skill 安装（`npx skills add jinlio/deep-research-skill`）；新增 `.claude-plugin/marketplace.json` 支持 Claude Code 插件市场。
- 新增 `scripts/render_report.py`：零依赖单文件 HTML 证据链报告，[C-xxx]/[S-xxx] 引用悬浮展示原文摘录与核验徽标；账本内容全部转义。
- 新增真实示例 `examples/deep-dive/`（SQLite vs DuckDB）：三个官方来源、7 条证据全部 verified，边界结论诚实标注 insufficient；附回归测试。
- benchmark 新增造假引文陷阱类 case 与 `must_not_support_claim_ids` 评分；新增 `benchmarks/RESULTS.md` 评测协议与指标定义（首跑前不填数字）。
- 新增 `core/references/source-playbook.zh.md`（中文来源方法论）与 `domain-overlays.md`（医疗/金融/法律/市场证据标准收紧）。
- CI：打 tag 自动构建并上传六套 runtime 安装包到 GitHub Release；新增每周兼容巡检。
- 文档：英文主 README + 中文 README.zh-CN.md；OpenClaw/HermesAgent 转入维护模式。

## 0.2.7 - 2026-09-18

- 进一步收紧 OpenClaw 运行时 profile：移出安装、配置和管理员诊断说明，运行时不得枚举或读取宿主设置。
- 保留研究所需的已授权能力映射，并规定不能执行校验时应披露待验收状态，不尝试获得额外能力。

## 0.2.6 - 2026-09-18

- 收敛 runtime 安装包：每个包只分发自身 capability profile，移除其它平台无关的命令、沙箱和委派示例。
- 明确最小权限边界：只复用当前会话已授权的工具；不得改动权限、审批、沙箱、配置、网络设置或凭据。

## 0.2.5 - 2026-09-04

- 将“纯工作流、不绑定模型或搜索服务”提升为核心卖点，明确与搜索工具类 skill 的边界。
- 补充 README 的亮点说明：宿主工具复用、能力降级、结构化证据包和确定性质量门禁。

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
