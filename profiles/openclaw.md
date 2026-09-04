# OpenClaw Capability Profile

本 profile 对应 OpenClaw 官方 skill/sub-agent 文档（核对日期：2026-09-02）。它只把 OpenClaw 能力映射到通用协议，不改变研究规则。若本地版本的命令或工具名不同，以 `openclaw --help`、`openclaw skills list --json` 和当前会话暴露的工具为准，并在 capability JSON 中记录实际观察结果。

官方参考：

- [Skills](https://docs.openclaw.ai/tools/skills)
- [Creating skills](https://docs.openclaw.ai/tools/creating-skills)
- [Sub-agents](https://docs.openclaw.ai/tools/subagents)
- [Skills config](https://docs.openclaw.ai/tools/skills-config)
- [Sandboxing](https://docs.openclaw.ai/gateway/sandboxing)
- [Permission modes](https://docs.openclaw.ai/tools/permission-modes)
- [CLI skills](https://docs.openclaw.ai/cli/skills)
- [Tool/security configuration](https://docs.openclaw.ai/gateway/config-tools)

## 安装和加载

OpenClaw 会按以下优先级发现包含 `SKILL.md` 的技能（同名时高优先级覆盖低优先级）：

1. `<workspace>/skills`（当前 agent）
2. `<workspace>/.agents/skills`（项目 agent）
3. `~/.agents/skills`（默认 state 下的个人 agent）
4. `<state-dir>/skills`（managed/local）
5. bundled skills
6. `skills.load.extraDirs` 和 plugin skills

配置 root 下最多 6 层的任意 `SKILL.md` 都可被发现；技能名来自 frontmatter 的 `name`，缺省才回退到目录名。先用 `python scripts/build_adapters.py --output dist` 生成 `dist/openclaw/deep-research/`，再安装这个完整包：

```bash
mkdir -p <workspace>/skills/deep-research
cp -R dist/openclaw/deep-research/. <workspace>/skills/deep-research/
openclaw skills list
openclaw skills info deep-research
openclaw skills check --agent <agent-id>
```

也可以使用 OpenClaw 的本地安装入口：

```bash
openclaw skills install ./dist/openclaw/deep-research --as deep-research
```

也可从 ClawHub 或 Git 安装，但安装前应阅读 skill 内容并运行 verify；第三方 skill 是不受信任代码。启用 `skills.load.watch` 时，`SKILL.md` 改动会刷新后续 turn 的 snapshot；已有 session 仍可能保留旧的 skill 选择，应在新会话或显式 refresh 后验证。

确认名称为 `deep-research` 后，在新会话中使用 `/deep-research`，或显式要求 agent 加载该 skill。skill 内部用 `{baseDir}` 定位 `references/` 和 `scripts/`，不依赖固定用户目录。

## 能力映射

| 通用能力 | OpenClaw 典型实现 | 约束和验收 |
|---|---|---|
| `load_skill` | workspace/project-agent/personal/managed roots、`skills.load.extraDirs`、`openclaw skills list/info` | `SKILL.md` 和所有引用文件可读；frontmatter `name` 与 agent allowlist 生效 |
| `search` | 当前 agent 暴露的 `web_search`、搜索插件或 MCP | 工具名由 host/plugin 决定；只复用当前会话已有工具，搜索摘要只能生成候选 source |
| `read_source` | `web_fetch`、浏览器工具、用户提供的本地文件 | evidence 必须来自打开后的正文并带位置 |
| `delegate` | `sessions_spawn`，每个独立子问题一个 `taskName` | 调用只返回 accepted receipt（`runId`/`childSessionKey`）；用完成事件或 `sessions_yield` 接收结果，不轮询等待；子 Agent 只写自己的 packet，失败也要回传状态 |
| `artifact_io` | workspace 文件工具或受控 `exec` 写入 `research-run/` | 仅允许 run 目录内追加/新建；原始 source 不覆盖 |
| `checkpoint` | `run_manifest.json`、任务状态和保留的子 Agent 记录 | OpenClaw session/gateway state 不是研究事实源；重启后仍以 run bundle 为准，不重复覆盖 JSONL |
| `audit` | `{baseDir}/scripts/run_gates.py` | 交付前必须 `--require-final --fail-on-pii` 通过 |

典型 `sessions_spawn` 任务形状如下（字段以当前 OpenClaw 工具 schema 为准）：

```json
{
  "task": "读取指定 research-run 工件，逐 claim 提取可定位 evidence；不要写最终报告。",
  "taskName": "verify-q001",
  "label": "Verify q001",
  "cwd": "<workspace>",
  "runTimeoutSeconds": 1800,
  "cleanup": "keep"
}
```

这是概念形状，`sessions_spawn` 的可用字段以当前 runtime schema 为准；不要把 `taskName` 当作 session key。

`cwd` 应指向包含 run bundle 的 workspace；不要把私有材料放入公共或不受控 workspace。独立性要求来自研究计划：不同子 Agent 必须使用不同来源路径或检索入口，不能把子 Agent 数量当作证据数量。

## 只读和权限边界

研究默认是“外部只读、工作区受控写入”：允许读取公开网页和用户明确提供的材料，允许在 `research-run/` 中写入工件，但禁止发布、推送、发送消息或修改外部资源。需要运行校验脚本时，优先使用 allowlist 的 Python 命令；不需要命令执行时可把 `tools.exec.mode` 设为 `deny`。OpenClaw 的 skill allowlist 不是 shell 授权边界，必须同时检查 exec policy、sandbox 和凭据范围。`agents.entries.<id>.skills` 是最终可见集合，不会和 defaults 合并；`tools.sessions.visibility`、`tools.agentToAgent` 和 sandbox tool allowlist 还会分别限制会话可见性、跨 agent 通信和子 Agent 工具。

建议验收：

```bash
openclaw skills list
openclaw exec-policy show
openclaw approvals get
```

若 runtime 无法提供 workspace 文件写入，切换到“会话内工件 + 结束前导出 run bundle”；若无 `sessions_spawn`，切换到串行阶段并在 manifest 写入 `delegation: unavailable`。

## 恢复和失败处理

每次阶段完成后更新 `run_manifest.json` 的 status、attempt、artifact hash 和 retrieval event。OpenClaw 子 Agent 的后台完成事件可能晚于当前 turn；收到 `failed`、超时或失联状态时，保留 packet 并将 claim 标记为 `unknown`/`insufficient`，不得当作没有发现问题。`/stop` 或父会话取消会请求级联停止，但清理是异步的，不能把取消回执当成所有 child 已完成。继续运行前先执行：

```bash
python <skill-root>/scripts/run_gates.py <workspace>/research-run --preflight
```

恢复时只重试缺失或失败的 task，使用幂等 task id；不要删除或改写已有 JSONL 记录。
