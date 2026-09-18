# OpenClaw Capability Profile

本 profile 对应 OpenClaw 官方 skill/sub-agent 文档（核对日期：2026-09-02）。它只把当前会话已经授予的能力映射到通用协议，不改变研究规则，也不读取或调整宿主配置。若工具名或能力不可用，按降级规则执行并记录实际观察结果。

官方参考：

- [Skills](https://docs.openclaw.ai/tools/skills)
- [Creating skills](https://docs.openclaw.ai/tools/creating-skills)
- [Sub-agents](https://docs.openclaw.ai/tools/subagents)
- [Skills config](https://docs.openclaw.ai/tools/skills-config)
- [Sandboxing](https://docs.openclaw.ai/gateway/sandboxing)
- [Permission modes](https://docs.openclaw.ai/tools/permission-modes)
- [CLI skills](https://docs.openclaw.ai/cli/skills)
- [Tool/security configuration](https://docs.openclaw.ai/gateway/config-tools)

## 加载边界

本包由用户或宿主安装并加载；运行时只读取自己的 `SKILL.md`、`references/`、`profiles/openclaw.md` 和 `scripts/`。不要枚举 skill 根目录、读取宿主设置，或改变 skill 的可见性。skill 根目录可通过宿主提供的 `{baseDir}` 解析，不依赖固定用户目录。

## 能力映射

| 通用能力 | OpenClaw 典型实现 | 约束和验收 |
|---|---|---|
| `load_skill` | 当前会话已加载的 skill 目录 | 仅读取本包入口和引用文件；缺失文件即停止并报告 |
| `search` | 当前 agent 暴露的 `web_search`、搜索插件或 MCP | 工具名由 host/plugin 决定；只复用当前会话已有工具，搜索摘要只能生成候选 source |
| `read_source` | `web_fetch`、浏览器工具、用户提供的本地文件 | evidence 必须来自打开后的正文并带位置 |
| `delegate` | `sessions_spawn`，每个独立子问题一个 `taskName` | 调用只返回 accepted receipt（`runId`/`childSessionKey`）；用完成事件或 `sessions_yield` 接收结果，不轮询等待；子 Agent 只写自己的 packet，失败也要回传状态 |
| `artifact_io` | 当前会话已有的工作区文件工具 | 仅允许 run 目录内追加/新建；原始 source 不覆盖 |
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

研究默认是“外部只读、工作区受控写入”：允许读取公开网页和用户明确提供的材料，允许在 `research-run/` 中写入工件，但禁止发布、推送、发送消息或修改外部资源。不得读取、请求、修改或绕过权限、审批、沙箱、skill/tool 可见性、网络设置或凭据。运行校验脚本仅在当前会话已允许本地执行时进行；否则保留待验收状态，不尝试获得额外能力。

若 runtime 无法提供 workspace 文件写入，切换到“会话内工件 + 结束前导出 run bundle”；若无 `sessions_spawn`，切换到串行阶段并在 manifest 写入 `delegation: unavailable`。

## 恢复和失败处理

每次阶段完成后更新 `run_manifest.json` 的 status、attempt、artifact hash 和 retrieval event。OpenClaw 子 Agent 的后台完成事件可能晚于当前 turn；收到 `failed`、超时或失联状态时，保留 packet 并将 claim 标记为 `unknown`/`insufficient`，不得当作没有发现问题。`/stop` 或父会话取消会请求级联停止，但清理是异步的，不能把取消回执当成所有 child 已完成。继续运行前先执行：

```bash
python <skill-root>/scripts/run_gates.py <workspace>/research-run --preflight
```

恢复时只重试缺失或失败的 task，使用幂等 task id；不要删除或改写已有 JSONL 记录。
