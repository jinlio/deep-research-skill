# HermesAgent Capability Profile

本 profile 对应 Hermes Agent 官方 skills、tools 和 delegation 文档（核对日期：2026-09-02）。它只描述能力映射；研究事实协议仍以 `references/` 为准。Hermes 的版本和配置可能变化，执行前用 `hermes --help`、`hermes skills list`、`hermes tools` 确认实际能力。

官方参考：

- [Working with Skills](https://hermes-agent.nousresearch.com/docs/guides/work-with-skills)
- [Skills System](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills)
- [Tools & Toolsets](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools)
- [Subagent Delegation](https://hermes-agent.nousresearch.com/docs/user-guide/features/delegation)
- [Subagent lifecycle API](https://hermes-agent.nousresearch.com/docs/developer-guide/subagent-lifecycle-api)

## 安装和加载

Hermes 将用户 skill 目录作为 source of truth，支持把整个目录安装到 `~/.hermes/skills/`：

```bash
hermes skills install https://git.luckyguo.dpdns.org/chengge/deep-research-skill/raw/branch/main/SKILL.md --name deep-research
hermes skills list
```

若需要附属 references/scripts，推荐复制完整目录，或使用 Hermes 支持的 skill archive/URL 安装方式，确保 `SKILL.md` 相对路径下的文件一起存在：

```bash
mkdir -p ~/.hermes/skills/deep-research
git clone --depth 1 https://git.luckyguo.dpdns.org/chengge/deep-research-skill.git ~/.hermes/skills/deep-research
hermes skills list
```

新会话中使用 `/deep-research`；安装后的 skill 通过 `skill_view` 按需读取 references，避免把整套协议预先塞进上下文。

## 能力映射

| 通用能力 | HermesAgent 典型实现 | 约束和验收 |
|---|---|---|
| `load_skill` | `~/.hermes/skills/`、`hermes skills list`、`skill_view` | `SKILL.md`、references 和 scripts 均可读 |
| `search` | `web_search`、`web_extract`、browser toolset、MCP | 仅使用当前启用的 `web/search/browser` toolset |
| `read_source` | `web_extract`、browser、`read_file` | 保存原文摘录、页码/段落/时间戳和检索状态 |
| `delegate` | `delegate_task` 单任务或 `tasks=[...]` 批量委派 | 子 Agent 继承父 toolset；每个 goal/context 必须自包含 |
| `artifact_io` | `read_file`、`write_file`/`patch`、`terminal` | 工件只写入 run 目录，JSONL 追加并保留 hash |
| `checkpoint` | run bundle + Hermes 持久 delegation 结果 | 进程重启后仍以 bundle 为准；运行中的 child 若变为 unknown 必须披露 |
| `audit` | `terminal` 执行 `{baseDir}/scripts/run_gates.py` | 最终报告前运行完整门禁并保存输出 |

启用最小 toolset 后再开始正式搜索：

```bash
hermes chat --toolsets "web,file,delegation,skills" -q "/deep-research <研究问题>"
hermes tools
```

标准 `delegate_task` 的批量形状为：

```python
delegate_task(tasks=[
    {"goal": "Discover official sources for Q-001", "context": "Run: ...; output only sources.jsonl packet"},
    {"goal": "Find counter-evidence for Q-001", "context": "Use an independent source path; output challenges"},
])
```

Hermes 的普通 `delegate_task` 子 Agent 继承父级工具，不能靠调用参数扩大权限；需要更窄的工具隔离时，在父会话配置 toolset。插件作者可使用 lifecycle API 的 `allowed_toolsets`，但不要假设普通 skill 可以直接调用该 Python API。

## 只读和权限边界

建议把研究会话的终端 backend 设为 `docker` 或受控本地目录，禁止把 API key、用户私有材料和完整 prompt 写入日志。外部网络调用只读；工作区内允许写入 `research-run/` 工件和审计结果；发布、发送消息、改动仓库或远程资源必须另行得到用户授权。`terminal` toolset 不是研究协议的默认依赖，没有它就把脚本校验交给宿主 CI。

## 恢复和失败处理

Hermes 会保存 delegation completion，但子 Agent 进程在宿主崩溃后不保证继续执行。每个 child 结果都要落成 agent packet，并把 `PENDING`/`UNKNOWN` 反映到 manifest。恢复流程：读取最近 manifest → 找出缺失/失败 task → 只重新委派这些 task → 追加新 packet → 重新运行 gates。禁止按“没有返回内容”推断“没有证据”。

无 delegation 时按 Discover → Extract → Verify → Challenge 的串行顺序执行；无 web toolset 时只研究用户提供的链接/本地材料，并在最终报告披露覆盖限制。
