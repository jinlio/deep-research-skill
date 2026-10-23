# Deep Research Skill

[English](README.md) · [GitHub](https://github.com/jinlio/deep-research-skill) · MIT

> 不只是搜索：把模糊问题变成经过追问、核验和审查的决策材料。每条结论都能回到带位置的原文证据，冲突、未知和检索失败保持可见，而不是被流畅文字掩盖。

AI 研究工具的引用造假已被定量记录：2026 年的多项分析显示各工具生成的引用中有 **39.6%–55% 完全捏造**（[INRA](https://www.inra.ai/blog/ai-hallucinations)），即便 OpenAI Deep Research，也有约 **22% 的引用 URL 并不支持对应论断**（[FACT 框架，arXiv](https://arxiv.org/html/2604.03173v1)）。失败模式从来不是"报告看起来空洞"，而是"报告很流畅，但你不敢信"。

Deep Research Skill 是面向编程 Agent（Claude Code、Codex CLI、OpenCode 及通用 Agent）的**纯工作流**研究协议。它不内置搜索引擎、模型或 API key，而是把宿主已有的工具组织成一条可检查的流程：

1. **先澄清，再搜索** —— 可配置的 N 轮追问固化为用户确认的 `research_spec.yaml`，减少"搜得很全但答非所问"的返工。
2. **结论与证据绑定** —— 每条 claim 引用带位置信息的原文摘录（`claim → evidence → source`），不用搜索摘要或模型记忆冒充事实。
3. **冲突与未知是一等公民** —— 矛盾、检索失败、`insufficient` 进入独立工件，而不是被综合掉的噪音。
4. **确定性门禁验收** —— 零依赖脚本检查引用覆盖、来源独立性、澄清确认、隐私和路径安全；不通过就不能交付。
5. **可恢复、可交接** —— append-only run bundle 在中断后可恢复；团队成员或另一个 Agent 可以接着同一份账本继续。

## 安装

**一行安装（Claude Code、Codex CLI 及一切兼容 [agentskills.io](https://agentskills.io) 标准的宿主）：**

```bash
npx skills add jinlio/deep-research-skill
```

**Claude Code 插件市场：**

```
/plugin marketplace add jinlio/deep-research-skill
/plugin install deep-research@deep-research-skill
```

**手动安装（任意宿主）：** 把本仓库复制进 skill 目录（如 `~/.claude/skills/deep-research/`）。根 `SKILL.md` 自足可用；`core/references/`、`scripts/`、`profiles/` 提供完整协议。

**按 runtime 裁剪的精简包：**

```bash
python scripts/build_adapters.py --output dist
# 安装 dist/<runtime>/deep-research/，可选 openclaw | hermesagent | codex | opencode | claude-code | generic
```

## 快速开始

```bash
# 1. 创建研究运行
python scripts/init_run.py research-run --question "研究问题" --goal "支持的决策" --depth standard

# 2. ……完成澄清、登记来源、提取证据、核验 claim……

# 3. 交付前运行门禁
python scripts/run_gates.py research-run --require-final --fail-on-pii
```

宿主 Agent 负责搜索、阅读和写作；脚本只做确定性校验。所有产物落在一个可审计的目录里：

```
research-run/
  research_spec.yaml      # 确认后的问题、范围、证据标准
  clarification_log.jsonl # 每轮追问与回答
  sources.jsonl           # 来源元数据、获取状态、独立性分组
  evidence.jsonl          # 带页码/章节定位的原文摘录
  claims.jsonl            # 每条 claim 的状态、置信度、证据引用
  conflicts.jsonl         # 冲突、未知、检索失败
  run_manifest.json       # 运行时、尝试记录、降级原因
  final_report.md         # 从账本派生——账本才是事实基础
```

## 深度模式

| depth | 澄清轮次 | 适用 |
|---|---|---|
| `quick` | 0 轮（假设显式写入规格并展示） | 事实盘点、时间敏感查询 |
| `standard` | 1 轮 + 最终确认 | 大多数调研 |
| `deep` | 2–3 轮 + 最终确认 | 高影响决策、竞品分析、尽调 |

任何模式下都可以说"按当前理解开始"提前结束澄清；未决项会作为显式假设写入规格，不会静默猜测。

## 引用核验：抓住造假引文的那一层

结构性门禁能发现"缺引用"；`scripts/verify_evidence.py` 抓的是**错的引用**。它重新抓取每个被引用的来源页面，把每条证据摘录逐条回贴定位（有序分段 + 滑窗模糊匹配，标点/全半角归一化，CJK 友好），结果连同内容 hash 写入 `verification.jsonl`：

| 状态 | 含义 |
|---|---|
| `verified` / `verified_fuzzy` | 摘录在页面上定位成功（精确 / 窗口相似度 ≥0.85） |
| `mismatch` | 页面上找不到该摘录——引文造假或页面已变更 |
| `unavailable` | 来源不可达（瞬时网络、404、500） |
| `unverifiable` | 无可匹配对象（PDF、无 URL）——绝不当作通过 |

严格模式下它是门禁：`run_gates.py <run> --require-final --require-verified` 会在高影响 claim 没有回贴成功的证据、或任何摘录 mismatch 时直接失败。网络抓取只走 http/https，并拒绝解析到环回/私有/保留地址的主机。

**看实际效果：** [examples/deep-dive/](examples/deep-dive/README.md) 是一个完整真实运行（SQLite vs DuckDB）——三个官方文档的 7 条引文全部回贴 verified，争议边界诚实标注为 `insufficient`，并附[单文件 HTML 报告](examples/deep-dive/run/final_report.md)：悬浮引用即可看到原文摘录和核验徽标。

## 和同类方案的区别

大多数 deep research skill 在优化"搜得更多"：并行 Agent、长报告、漂亮排版。这能提高覆盖，但文档化的核心失败——引用经不起核对——在那些技巧里原样存活。本项目优化的是**可核验性**：

| | 常见 research skill | Deep Research Skill |
|---|---|---|
| 证据 | 参考文献里的 URL | 每条 claim 对应带位置的原文摘录 |
| 冲突 | 尽力综合成单一结论 | 独立 `conflicts.jsonl`，禁止静默择一 |
| 证据不足 | 流畅文字补齐 | 显式 `unknown` / `insufficient` 状态 |
| 质量控制 | 提示词层面的建议 | 确定性、零依赖的门禁脚本 |
| 可移植 | 绑定单一宿主 | 同一协议经 capability profile 跑在 6 个 runtime |
| 中断恢复 | 从头再来 | append-only bundle，从 checkpoint 继续 |
| 权限 | 各异 | 默认只读；不碰权限、凭据、网络配置 |

代价也是诚实的：这个工作流会先问几个问题，并在正文之外产出账本。如果你只想要一篇快而不设防的摘要，用普通搜索就好；如果报告要支撑决策，这些摩擦就是产品本身。

## Runtime 支持

| Runtime | 状态 | 说明 |
|---|---|---|
| Claude Code | ✅ 维护中 | 串行优先；委派经 capability profile 映射 |
| Codex CLI | ✅ 维护中 | 已通过 `codex exec --sandbox read-only` smoke test |
| OpenCode | ✅ 维护中 | 真实端到端运行已验证（降级串行模式） |
| generic | ✅ 维护中 | 其他宿主的协议兜底 |
| OpenClaw | 🔧 维护模式 | profile 保持更新；不再扩展新功能 |
| HermesAgent | 🔧 维护模式 | profile 保持更新；不再扩展新功能 |

各 runtime 的真实测试边界、smoke test 命令和 OpenCode 运行摘要见 [runtime_validation.md](runtime_validation.md)。

## 文档

- [English README](README.md)
- [实施计划](implementation_plan.md) —— 架构与工程取舍
- [调研结论](research_findings.md) —— 催生本设计的市场扫描
- [Runtime 验证](runtime_validation.md) —— 每个 runtime 实际测过什么
- [Benchmark](benchmarks/README.md) —— 金标用例与评估协议
- [变更日志](CHANGELOG.md) · [贡献指南](CONTRIBUTING.md) · [安全](SECURITY.md)

## 设计原则

- 最终报告是派生物，`sources`、`evidence`、`claims`、`conflicts` 才是事实基础。没有证据时必须输出 `unknown` 或 `insufficient`，不能用流畅文字掩盖缺口。
- 不绑定搜索服务、模型或 provider。运行时能力在 profile 中声明；能力缺失时透明降级并写入 manifest。
- 默认只读。Skill 不请求或修改权限、审批、沙箱、工具/网络配置或凭据。

## 许可

MIT
