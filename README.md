# Deep Research Skill

[GitHub](https://github.com/jinlio/deep-research-skill) · [SkillHub](https://skills.palebluedot.live) · OpenClaw adapter via ClawHub

> 让 Agent 先把问题问清楚，再用证据给出经得起追问的答案。

Deep Research Skill 是一个跨 Agent 的深度调研工作流。它不绑定某个模型、搜索服务或平台，而是把需求澄清、证据管理、独立审查和质量门禁固化成可复用协议，运行在 OpenClaw、HermesAgent、Codex、OpenCode、Claude Code 以及 generic Agent 上。

## 两个核心能力

### 1. 先澄清，再搜索：避免一开始就答错问题

大多数调研失败不是“搜不到”，而是研究目标没有被定义清楚。Skill 会在正式检索前进行可配置的 N 轮追问，确认：

- 研究要支持什么决策，最终读者是谁
- 范围、时间窗口、地域和术语边界是什么
- 需要事实盘点、方案比较，还是风险判断
- 什么证据标准才算足够，哪些结论必须保守表达

早期方向侦察与正式证据严格隔离，用户确认后的 `research_spec.yaml` 才能启动正式研究。这样能显著减少“回答很完整，但答的不是我想问的”这一类返工。

### 2. 证据优先：每个结论都能回到原文

Skill 不把搜索摘要或 Agent 的记忆当作事实。每条重要结论都进入 `claim -> evidence -> source` 证据账本，并经过独立核验和反方挑战：

- 记录原文片段、页码/段落或结构化字段，而不是只保存链接
- 对冲突、未知、检索失败和证据不足显式标记，不用流畅文字掩盖缺口
- 只有通过引用覆盖、来源一致性、隐私和 manifest 门禁的工件，才能生成最终报告
- 多 Agent 并行时共享同一工件协议，避免子 Agent 只交一段无法复核的 prose

最终交付的不只是 `final_report.md`，还包括可恢复、可审计的完整 run bundle。

## 它解决什么痛点

| 常见问题 | 结果 | Deep Research Skill 的做法 |
|---|---|---|
| 需求模糊就开始搜索 | 方向跑偏，反复返工 | N 轮澄清 + 用户确认后再检索 |
| 只相信搜索摘要或模型记忆 | 引用无法核验，事实容易幻觉 | claim-evidence-source 账本 |
| 多个 Agent 各自输出长文本 | 重复劳动，无法合并和追责 | 角色契约、结构化 packet、共享 run bundle |
| 不同 Agent 的工具名和权限不同 | 换平台就要重写 skill | capability profile + 自动降级 |
| 长任务中断或上下文丢失 | 进度无法恢复 | append-only 工件、manifest、checkpoint 规则 |
| 为了“看起来完整”而隐藏缺口 | 读者误把未知当结论 | 冲突/unknown/insufficient 状态和最终门禁 |

它解决的不是“再做一个搜索器”，而是把搜索、阅读、核验和写作组织成一条可检查的生产流程。

## 当前状态

`v0.2.2` 发布版本。核心协议、串行/多 Agent 工作流、OpenClaw/HermesAgent/Codex/OpenCode/Claude Code 适配指南、确定性质量门禁和 benchmark 骨架已就绪。OpenClaw/HermesAgent profile 已按 2026-09-02 上游文档补齐技能发现、toolset/权限边界、异步委派和恢复语义。各 runtime 的真实测试边界见 [`runtime_validation.md`](runtime_validation.md)。

总体调研结论见 [`research_findings.md`](research_findings.md)，完整路线见 [`implementation_plan.md`](implementation_plan.md)，版本变更见 [`CHANGELOG.md`](CHANGELOG.md)。

当前仓库已用 15 个单元测试、runtime adapter matrix、四类 benchmark 和完整 run gates 验证。Codex CLI 与 OpenCode Desktop 的真实 smoke test 已通过；Claude Code 的环境限制及 OpenCode 的降级边界见 [`runtime_validation.md`](runtime_validation.md)。我们明确区分协议验证、runtime 启动验证和真实模型黑盒验证，不把 fixture 冒充成黑盒通过。

## 设计原则

- 先通过可配置的 N 轮追问确认研究需求，再开始正式检索。
- 不绑定搜索服务或 Agent runtime；OpenClaw、HermesAgent、Codex、Claude Code 等通过 capability profile 适配。
- 每条重要结论都能回溯到带位置的原文证据。
- 显式报告冲突、未知、证据不足、检索失败和停止原因。
- 研究过程可恢复、可审计，默认只读并保护敏感信息。

## 公开文档

仓库中的文档按读者分层：README 介绍价值和使用方式，`runtime_validation.md` 记录可复核的兼容性结果，`research_findings.md` 和 `implementation_plan.md` 记录调研依据与工程取舍。公开文档只保留版本、能力、结果和限制，不包含账号、凭据、本机路径、provider 额度、代理地址或用户材料。

## 目录

```text
SKILL.md                  # 源码兼容入口
core/SKILL.md             # 唯一核心工作流入口
core/references/          # 协议、证据、门禁和报告规则
  agent-contracts.md      # 各研究角色的输入/输出契约
adapters/<runtime>/       # 各 Agent 的薄入口（不复制核心逻辑）
profiles/                 # 各 Agent runtime 的能力映射
scripts/                  # 确定性检查与工件校验
dist/                     # build_adapters.py 生成的可安装包（不提交）
benchmarks/               # golden set 和评估用例
tests/                    # 协议与门禁测试
examples/                 # 最小可运行示例
.github/workflows/        # GitHub CI
```

## 原则

最终报告是派生物，`sources`、`evidence`、`claims` 和 `conflicts` 才是事实基础。没有证据时必须输出 `unknown` 或 `insufficient`，不能用流畅文字掩盖缺口。

## 快速开始

### 1. 生成对应 Agent 的安装包

```bash
python scripts/build_adapters.py --output dist
```

选择 `dist/<runtime>/deep-research/`，复制到对应 Agent 的 skill 目录。每个包都是自包含的，不需要再从源码仓库寻找 `references/` 或 `scripts/`。

### 2. 创建一次研究运行

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

先运行 `python scripts/build_adapters.py --output dist`，再将 `dist/openclaw/deep-research` 放入 `<workspace>/skills/`，或用 `openclaw skills install` 安装该目录；新会话中使用 `/deep-research`。具体的 `sessions_spawn`、workspace、权限和恢复映射见 [`profiles/openclaw.md`](profiles/openclaw.md)。

发布到 ClawHub 后可直接使用 `clawhub install deep-research`；SkillHub 通过 GitHub 索引本仓库，收录完成后可使用 `npx skillhub install jinlio/deep-research-skill`。

### Codex

Codex CLI 可用 `codex exec --sandbox read-only` 做无副作用 smoke test；搜索能力按当前宿主配置映射，不假设固定 CLI 参数。具体映射见 `profiles/codex.md`。

### OpenCode 与 Claude Code

两者通过各自的项目 skill/instruction 目录加载同一 `SKILL.md`。由于不同发行版的 CLI 和 delegation API 不一致，先导出实际 capability JSON，再运行 `scripts/probe_runtime.py`；具体安全降级规则见 `profiles/opencode.md` 和 `profiles/claude-code.md`。

### HermesAgent

将 `dist/hermesagent/deep-research` 安装到 `~/.hermes/skills/`，然后在新会话中使用 `/deep-research`；启用 `web`、`file`、`delegation` toolset 后，可按子问题并行委派。具体映射见 [`profiles/hermesagent.md`](profiles/hermesagent.md)。

### 构建和验证适配包

```bash
python scripts/build_adapters.py --output dist
python scripts/test_runtime_matrix.py
python scripts/release_check.py
```

`dist/<runtime>/deep-research/` 是可复制到对应 Agent skill 目录的完整包；`dist/` 为构建产物，不提交到 Git。

### 能力探测与发布验收

运行时可先导出 capability JSON，再执行：

```bash
python scripts/probe_runtime.py profiles/capabilities/openclaw.example.json
python scripts/probe_runtime.py profiles/capabilities/hermesagent.example.json
python scripts/release_check.py
```

探测结果会明确完整模式、串行降级模式、缺失能力和安全错误；不会自动安装搜索服务或修改远程资源。
