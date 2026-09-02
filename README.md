# Deep Research Skill

多 Agent 通用深度调研 skill：以研究规格、证据账本、独立审查和质量门禁为核心，复用宿主 Agent 已有的搜索、浏览、文件和 MCP 工具。

## 当前状态

`v0.1.1` 发布版本。核心协议、串行/多 Agent 工作流、OpenClaw/HermesAgent/Codex/OpenCode/Claude Code 适配指南、确定性质量门禁和 benchmark 骨架已就绪。各 runtime 的真实测试边界见 [`runtime_validation.md`](runtime_validation.md)。

总体调研结论见 [`research_findings.md`](research_findings.md)，完整路线见 [`implementation_plan.md`](implementation_plan.md)，版本变更见 [`CHANGELOG.md`](CHANGELOG.md)。

## 设计目标

- 先通过可配置的 N 轮追问确认研究需求，再开始正式检索。
- 不绑定搜索服务或 Agent runtime；OpenClaw、HermesAgent、Codex、Claude Code 等通过 capability profile 适配。
- 每条重要结论都能回溯到带位置的原文证据。
- 显式报告冲突、未知、证据不足、检索失败和停止原因。
- 研究过程可恢复、可审计，默认只读并保护敏感信息。

## 目录

```text
SKILL.md                  # 核心工作流入口
references/               # 协议、证据、门禁和报告规则
  agent-contracts.md      # 各研究角色的输入/输出契约
profiles/                 # 各 Agent runtime 的能力映射
scripts/                  # 确定性检查与工件校验
benchmarks/               # golden set 和评估用例
tests/                    # 协议与门禁测试
examples/                 # 最小可运行示例
.github/workflows/        # GitHub CI
```

## 原则

最终报告是派生物，`sources`、`evidence`、`claims` 和 `conflicts` 才是事实基础。没有证据时必须输出 `unknown` 或 `insufficient`，不能用流畅文字掩盖缺口。

## 快速开始

创建一个空的研究运行：

```bash
python scripts/init_run.py research-run --question "研究问题" --goal "支持的决策"
python scripts/run_gates.py research-run --preflight
```

完成 N 轮澄清、来源登记和证据核验后，运行最终门禁：

```bash
python scripts/run_gates.py research-run --require-final --fail-on-pii
```

宿主 Agent 负责调用已有搜索工具和填写 JSONL 工件；本项目的脚本只负责确定性校验，不替代搜索或模型判断。

## 安装与运行时

### OpenClaw

将仓库放入 `<workspace>/skills/deep-research`，或运行 `openclaw skills install` 安装本地目录；新会话中使用 `/deep-research`。具体的 `sessions_spawn`、workspace、权限和恢复映射见 [`profiles/openclaw.md`](profiles/openclaw.md)。

### Codex

Codex CLI 可用 `codex exec --sandbox read-only` 做无副作用 smoke test；搜索能力按当前宿主配置映射，不假设固定 CLI 参数。具体映射见 `profiles/codex.md`。

### OpenCode 与 Claude Code

两者通过各自的项目 skill/instruction 目录加载同一 `SKILL.md`。由于不同发行版的 CLI 和 delegation API 不一致，先导出实际 capability JSON，再运行 `scripts/probe_runtime.py`；具体安全降级规则见 `profiles/opencode.md` 和 `profiles/claude-code.md`。

### HermesAgent

将 skill 安装到 `~/.hermes/skills/`，然后在新会话中使用 `/deep-research`；启用 `web`、`file`、`delegation` toolset 后，可按子问题并行委派。具体映射见 [`profiles/hermesagent.md`](profiles/hermesagent.md)。

### 能力探测与发布验收

运行时可先导出 capability JSON，再执行：

```bash
python scripts/probe_runtime.py profiles/capabilities/openclaw.example.json
python scripts/probe_runtime.py profiles/capabilities/hermesagent.example.json
python scripts/release_check.py
```

探测结果会明确完整模式、串行降级模式、缺失能力和安全错误；不会自动安装搜索服务或修改远程资源。
