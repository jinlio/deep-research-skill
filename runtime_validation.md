# Runtime Validation

本文件记录 2026-09-02 执行的最小 smoke test。它只公开可复现的版本、能力和结果，不包含本机路径、账号、凭据、provider 或原始终端日志。`*.example.json` 是协议 fixture，不等同于黑盒通过；真实 runtime 结果按“通过 / 阻塞 / 未完成”区分。

源码仓库中的 `core/` 和 `adapters/` 通过 `python scripts/build_adapters.py --output dist` 组装为完整安装包；`python scripts/test_runtime_matrix.py` 会在临时目录重复该过程并验证相对路径。

| Runtime | 安装/版本 | 已验证 | 结果 | 边界 |
|---|---|---|---|---|
| Codex CLI | `0.151.0-alpha.7.2` | 读取 `SKILL.md`、`references/adapter-contract.md`，运行 validator | 通过 | 未验证多 session delegation；profile 默认串行降级 |
| Claude Code | `2.1.156` | CLI 启动与版本查询 | 未完成 | 模型调用受当前环境认证/额度限制，未执行仓库读取 |
| OpenCode Desktop | `1.18.25` | Desktop 启动；安装包文件可见性检查 | 部分通过 | 当前会话未发现 `/deep-research` 命令，尚未完成新项目会话的 discovery 验证 |
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

OpenCode Desktop 的 skill discovery 需要在全新项目会话中重启/刷新后检查 `/deep-research` 命令；命令发现失败只代表当前 runtime 集成尚未验证，不代表核心协议或 validator 失败。

## 公开报告边界

公开报告应保留：runtime 版本、测试类型、通过/未完成状态、可复现命令和已知限制。

不要公开：本机绝对路径、用户目录、账号标识、API key、provider/额度详情、代理地址、原始日志和用户研究材料。
