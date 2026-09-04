# Runtime Validation

本文件记录 2026-09-02 执行的最小 smoke test。它只公开可复现的版本、能力和结果，不包含本机路径、账号、凭据、provider 或原始终端日志。`*.example.json` 是协议 fixture，不等同于黑盒通过；真实 runtime 结果按“通过 / 阻塞 / 未完成”区分。

源码仓库中的 `core/` 和 `adapters/` 通过 `python scripts/build_adapters.py --output dist` 组装为完整安装包；`python scripts/test_runtime_matrix.py` 会在临时目录重复该过程并验证相对路径。

| Runtime | 安装/版本 | 已验证 | 结果 | 边界 |
|---|---|---|---|---|
| Codex CLI | `0.151.0-alpha.7.2` | 读取 `SKILL.md`、`references/adapter-contract.md`，运行 validator | 通过 | 未验证多 session delegation；profile 默认串行降级 |
| Claude Code | `2.1.156` | CLI 启动与版本查询 | 未完成 | 模型调用受当前环境认证/额度限制，未执行仓库读取 |
| OpenCode Desktop | `1.18.26` | Desktop 新会话加载 `deep-research`；2 轮澄清；Plan → Discover → Extract → Verify → Challenge → Synthesize → Audit；6 个 gates | 通过（降级模式） | 本次运行由 OpenCode CLI/windows backend 执行；无 source discovery/search、无并行子 Agent、无 durable checkpoint，使用 webfetch/已知 URL、串行任务和 run bundle 恢复 |
| OpenClaw | 未提供可执行版本 | capability fixture/protocol probe | 未完成 | 需要在安装 runtime 的环境按 `profiles/openclaw.md` 执行 |
| HermesAgent | 未提供可执行版本 | capability fixture/protocol probe | 未完成 | 需要在安装 runtime 的环境按 `profiles/hermesagent.md` 执行 |

## Reproduce

Codex smoke（只读）：

```bash
codex exec --ephemeral --json --sandbox read-only -C <repo> \
  "Read SKILL.md and references/adapter-contract.md. Run python scripts/validate_skill.py . and report the exit status. Do not modify files."
```

Claude Code smoke（只读计划权限）：

```bash
claude --print --permission-mode plan --allowed-tools Read,Bash \
  "Read SKILL.md and report the first heading. Do not modify files."
```

OpenCode Desktop 的 skill discovery 已在全新会话中由用户确认成功，并完成一轮真实研究运行。运行 bundle 位于用户本机的 OpenCode workspace，不纳入本仓库；可用同样的 prompt 和 `scripts/run_gates.py` 复现。该结果证明 skill 加载和核心工作流可运行，不代表 OpenCode 的 web search、并行 delegation 或 durable checkpoint 在所有安装/模型配置中都可用。

## OpenCode 真实运行摘要

用户提供的 OpenCode 运行 `run_2026-09-02_opencode-skill-loading` 记录了：17 个来源、43 条 evidence、25 个 claims（24 条有证据支持，1 条 insufficient）、7 个冲突；澄清轮次为 1–2，引用覆盖率 1.0，敏感信息扫描通过，最终 `GATES: PASS (0 failed)`。本次能力声明为 `fetch_source`、`read_source`、`artifact_io`、`audit` 可用，`discover_sources` 不可用，`delegate` 可用但未并行，`checkpoint` 不可用。

## 公开报告边界

公开报告应保留：runtime 版本、测试类型、通过/未完成状态、可复现命令和已知限制。

不要公开：本机绝对路径、用户目录、账号标识、API key、provider/额度详情、代理地址、原始日志和用户研究材料。
