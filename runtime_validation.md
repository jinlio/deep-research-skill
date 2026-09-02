# Runtime Validation

本文件记录 2026-09-02 在本机执行的最小 smoke test。`*.example.json` 是协议 fixture，不等同于黑盒通过；真实 runtime 结果按“通过 / 阻塞 / 未通过”区分。

| Runtime | 安装/版本 | 已验证 | 结果 | 边界 |
|---|---|---|---|---|
| Codex CLI | `codex-cli 0.151.0-alpha.7.2` | 读取 `SKILL.md`、`references/adapter-contract.md`，运行 `python scripts/validate_skill.py .` | 通过，退出码 0 | 本次未验证多 session delegation；当前 profile 默认串行降级 |
| Claude Code | `2.1.156 (Claude Code)` | CLI 启动与版本查询 | 阻塞 | `--print` 在模型调用前返回 HTTP 403：当前 Kimi provider 月度额度耗尽；未执行仓库读取 |
| OpenCode Desktop | `1.18.25`，`OpenCode.exe` | Desktop 启动；`~/.opencode/skills/deep-research/SKILL.md` 与 references 文件可见 | 部分通过 | 新会话中 `/deep-research` 未出现在命令匹配，当前 workspace/discovery 刷新链路尚未确认；未执行模型请求 |
| OpenClaw | 未安装可执行程序 | capability fixture/protocol probe | 未做黑盒 | 需要安装 runtime 后按 `profiles/openclaw.md` 执行 |
| HermesAgent | 未安装可执行程序 | capability fixture/protocol probe | 未做黑盒 | 需要安装 runtime 后按 `profiles/hermesagent.md` 执行 |

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

OpenCode Desktop 的 skill discovery 需要在全新项目会话中重启/刷新后检查 `/deep-research` 命令；不要把 UI 命令匹配失败误报为协议或 validator 失败。
