# 多 Agent 通用深度调研 Skill 实施计划

目标：构建一套以方法论和工作流为核心、可运行于 OpenClaw、HermesAgent、Codex、Claude Code 等 Agent runtime 的深度调研 skill。

原则：**协议统一，运行时适配；先澄清需求，证据优先，结论后置；可恢复，可审计，可拒答。**

## 一、产品边界

### 解决的问题

- 将模糊问题转成可验收的研究规格。
- 用多个独立研究路径提高覆盖率，而不是简单增加 Agent 数量。
- 为每个重要结论保存可定位的原文证据。
- 显式处理冲突、时效、未知和证据不足。
- 在限流、超时、上下文压缩或 Agent 退出后恢复。
- 用统一工件协议适配不同 Agent 平台。
- 在正式研究前使用 Agent 已有的搜索/浏览工具做有限方向侦察，并进行 N 轮递进式追问，精确研究目标。

### 不解决的问题

- 不自带搜索引擎、爬虫、数据库或大模型。
- 不承诺所有问题都能得到确定结论。
- 不把报告字数、来源数量或 Agent 数量当作研究质量。
- 不在第一版内覆盖复杂的 Word/PDF 排版、自动发布和远程写入。

## 二、总体架构

采用三层结构：

```text
方法论层（固定）
  研究规格、角色、证据规则、冲突规则、停止条件、质量门禁

协议层（固定）
  research_spec / source / evidence / claim / review / run_manifest

运行时适配层（可替换）
  搜索、浏览、文件、PDF、数据库、子 Agent、checkpoint、权限和模型调用
```

核心 skill 不直接调用平台专属 API。它只要求 runtime 提供能力；若能力不存在，按照降级规则继续：

| 能力 | 完整模式 | 降级模式 |
|---|---|---|
| 子 Agent | 并行 discoverer/verifier/challenger | 单 Agent 分阶段执行，强制清空阶段上下文 |
| 结构化输出 | JSON schema 验证 | Markdown 模板 + 脚本校验 |
| 持久文件 | append-only 工件和 checkpoint | 会话内工件，结束前导出 run bundle |
| 浏览/搜索 | 多来源并行检索 | 用户提供来源 + 单一搜索工具 |
| 独立 reviewer | 不同模型/不同会话 | 新上下文中的同模型 reviewer，并标记独立性较低 |
| 权限控制 | runtime 原生只读/沙箱 | skill 层明确禁止写入和外部发布 |

## 三、标准工作流

### 阶段 0：Intake 与 N 轮需求澄清

输入：用户问题、目标、已有材料、截止时间、隐私要求。支持参数 `clarification_rounds: auto|N`，默认 `auto`（通常 2 轮，最多 5 轮）。

产物：`clarification_log.jsonl`、`research_spec.v<N>.yaml`，最终确认后固化为 `research_spec.yaml`。

#### 澄清循环

每轮只问仍会改变研究方案的高价值问题，避免一次发送长问卷：

1. **Round 0：理解回显**。将用户原问题改写成“当前理解 + 已知假设 + 不确定项”，不开始正式研究。
2. **方向侦察（可选）**。当术语、对象或问题边界明显含糊时，调用 runtime 已有的搜索/浏览工具，最多做少量查询，用来发现歧义、候选定义、时间范围和可能的决策分支。侦察结果标记为 `orientation_only`，不得进入证据账本或最终引用。
3. **Round 1：目标与边界**。追问要支持的决策、研究对象、时间点、地域、用户人群、排除项和成功标准。
4. **Round 2：证据与交付**。追问来源偏好、证据强度、是否接受二手来源、需要的报告深度、语言、格式、隐私和预算。
5. **Round 3+：只补关键缺口**。根据已确认规格和方向侦察结果，逐项处理仍会导致不同研究路径的歧义；不重复问用户已经回答的问题。
6. **最终确认**。展示一页式 research spec、默认假设、预期子问题和停止条件，由用户确认或修改。

用户在任一轮表示“按当前理解开始”即可提前结束；达到 N 轮上限仍有未决项时，必须把假设显式写入规格，并让用户确认，不得静默猜测。

#### 追问选择规则

- 优先问会改变来源、研究对象、时间范围、结论标准的问题。
- 一轮最多 3-5 个问题；可提供默认值，但不能把默认值伪装成用户答案。
- 问题必须是可回答的选择或短答，不让用户填写技术配置。
- 对同一歧义最多追问两次；仍无法确定则拆成多个解释分支并分别评估。
- 方向侦察必须覆盖至少两个可能解释，不能用单一搜索结果诱导用户确认某个假设。

必须明确：

- 研究问题和要支持的决策。
- 时间点、地域、对象定义和排除范围。
- 输出形式和读者。
- 来源优先级、禁止来源和用户指定来源。
- 深度模式：`quick`、`standard`、`deep`。
- 预算、截止时间和最大 Agent/工具调用数。
- 完成条件和必须回答的反证问题。

Gate：问题可被拆成至少一个可验证子问题；范围、时间点、决策目标和停止条件不能为空；用户已确认最终规格，或明确接受记录在案的默认假设。未通过时不得进入正式搜索。

### 阶段 1：Plan

由 planner 把问题拆成子问题树和独立证据路径。每个子问题声明：

- 要验证的 claim 类型。
- 主要来源路径，例如官方、学术、监管、数据、历史、反方。
- 负责 Agent 和允许使用的工具。
- 预期证据、失败处理和完成条件。

计划至少包含一条反方路径；高风险问题至少包含两条互相独立的来源路径。

Planner 必须读取运行时 capability profile，优先复用当前 Agent 已经可用的搜索、浏览、文件、PDF、数据库和 MCP 工具。核心 skill 不安装或假设新的搜索服务；若没有搜索工具，切换到用户材料/指定链接模式，并在报告中说明覆盖限制。

Gate：所有原始问题映射到子问题；没有“泛搜一下”这种不可验收任务；每个关键 claim 有预定验证路径。

### 阶段 2：Discover（使用 Agent 现有搜索工具）

discoverer 通过 runtime 已有的搜索/浏览工具发现和登记候选来源，不写最终结论。每个来源登记：

- URL/文件路径、标题、作者或机构。
- 发布日期、抓取时间、语言和来源类型。
- 与哪个子问题相关。
- 是否一手来源、潜在偏见、访问状态。
- 内容 hash 或版本标识（可获得时）。

执行去重：规范化 URL、域名/机构去重、转载链识别、同一新闻稿的镜像合并。

搜索策略按 research spec 生成，而不是让每个 Agent 自由泛搜：

- 每个子问题至少生成定义、直接证据、反方/风险、时间变化四类查询。
- 对高影响 claim 使用不同来源类型或不同搜索入口复查。
- 搜索摘要只用于筛选；正式 evidence 必须来自打开后的原文、PDF 或结构化数据。
- 工具调用失败、限流、登录或地区限制写入 `retrieval_events`，不能当作“没有结果”。

Gate：来源已登记；检索失败、登录限制、robots、解析错误等不能被静默丢弃。

### 阶段 3：Extract

extractor 从原文中提取证据片段，不允许只交搜索摘要。每条 evidence 包含：

- `evidence_id`、`source_id`。
- 原文摘录和位置（页码、章节、段落或时间戳）。
- 证据支持/反驳的命题。
- 适用范围、限制条件和时效。
- 提取 Agent、模型和时间。

Agent packet 只允许提交证据、观察、未知和后续问题；不得提交没有证据绑定的确定性结论。

Gate：关键数字、日期、因果和比较命题必须有原文片段；来源不可访问时只能标记为待核验。

### 阶段 4：Verify

verifier 按 claim 核验，而不是按来源写摘要。为每个 claim 记录：

- `status`: `supported`、`partially_supported`、`contradicted`、`insufficient`、`unknown`。
- 支持和反驳 evidence 列表。
- 来源质量、独立性、时效和适用范围。
- 置信度及其理由。
- 从证据到结论之间是否存在推断跳跃。

数值由脚本/计算器核验；单位、币种、时间点必须显式记录。

Gate：高影响 claim 至少一个权威来源；关键 claim 默认需要第二个独立来源；所有冲突进入 `conflicts.jsonl`，禁止静默择一。

### 阶段 5：Challenge

challenger 使用与主研究尽可能不同的检索路径，专门寻找：

- 反例、反方观点和失败案例。
- 被忽略的地域、时间段或人群。
- 定义偷换、因果过度推断、选择性引用。
- 低质量来源被重复引用造成的假共识。
- “没有证据”被误写成“证据表明不存在”。

reviewer 应直接读取来源登记和 evidence ledger，而不是只看 writer 的草稿。

Gate：每个高影响结论都有反方检查结果；未完成的挑战必须在报告中披露。

### 阶段 6：Synthesize

synthesizer 只能消费通过 Verify 和 Challenge 的工件。报告中的句子必须分类：

- `fact`：直接有证据支持。
- `inference`：基于多个事实的推断，必须写明推断性质。
- `opinion/recommendation`：价值判断或行动建议。
- `unknown`：证据不足，明确拒绝确定性表述。

报告固定包含：执行摘要、范围与方法、结论表、证据表、冲突与反方、置信度、缺口、停止原因、来源清单、运行成本。

### 阶段 7：Audit 与交付

audit agent 运行机器检查和人工式审查：

- claim 是否都有 evidence 引用。
- 引用是否真的支持对应句子。
- URL/文件是否可访问，失效来源是否标记。
- 冲突是否完整披露。
- 报告是否出现未登记数字、日期或来源。
- 是否泄漏 secret、PII 或用户私有材料。
- 是否发生未授权写操作。

只有通过 Gate 才能生成 `final_report.md`。无论是否通过，都保留 run bundle，不能只返回一篇最终文章。

方向侦察结果、每轮追问、用户回答、规格版本和最终确认必须随 run bundle 保存，以便审计“研究结论是否回答了用户真正确认的问题”。

## 四、角色和协作规则

第一版固定五类角色，角色是方法论提示，不绑定具体平台名称：

| 角色 | 责任 | 禁止事项 |
|---|---|---|
| Orchestrator | 管理阶段、预算、状态和 Gate | 不自行补写缺失证据 |
| Discoverer | 发现和登记来源 | 不把搜索摘要当证据，不写最终结论 |
| Extractor/Verifier | 提取原文、建立 claim-evidence 关系、核验数字 | 不修改原始来源，不静默解决冲突 |
| Challenger | 反方、遗漏、偏见和边界审查 | 不以多数票否决证据 |
| Synthesizer/Auditor | 生成报告和运行质量检查 | 不引用 ledger 外的事实，不隐藏 unknown |

并行规则：不同子问题可并行；同一 claim 的冲突核验必须在 evidence 登记后进行；最终综合必须串行，以避免未经验证的中间结论扩散。

## 五、统一工件协议

建议目录：

```text
research-run/
  research_spec.yaml
  clarification_log.jsonl
  orientation_notes.md
  plan.yaml
  sources.jsonl
  evidence.jsonl
  claims.jsonl
  conflicts.jsonl
  agent_packets/
  review.md
  audit.json
  run_manifest.json
  final_report.md
```

最小字段：

```yaml
# claims.jsonl 中的一条记录
claim_id: C-001
text: "可验证的命题"
type: fact
status: supported
evidence_ids: [E-003, E-008]
counter_evidence_ids: [E-011]
confidence: medium
scope: "适用范围"
as_of: "2026-09-02"
reason: "两个独立来源支持，但存在时间限制"
```

工件规则：原始来源不可覆盖；JSONL 采用追加式写入；派生报告可重建；每次运行记录模型、Agent、工具版本、调用时间、重试、错误和成本。

## 六、OpenClaw / HermesAgent 适配计划

不在核心 skill 中猜测平台 API。每个平台先填写一份 capability profile：

1. 如何加载 skill 和附属 references。
2. 如何创建并行/串行子 Agent。
3. 如何限制 Agent 的工具和写权限。
4. 如何读写工作目录和传递工件。
5. 如何执行 JSON/Markdown 结构化输出检查。
6. 如何保存和恢复 checkpoint。
7. 如何获取模型、工具调用、token 和错误信息。
8. 如何在能力缺失时切换降级模式。

### OpenClaw

- 提供 `profiles/openclaw.md`，只描述调用入口、子 Agent 委派格式、workspace 工件位置和权限映射。
- 通过 OpenClaw 原生 skill/agent 机制加载核心 `SKILL.md`，不复制第二套研究逻辑。
- 若原生调度器支持并行，按 plan 的独立路径并行；若不支持，按阶段顺序执行并保留同一工件协议。
- 用 OpenClaw 的工具权限和沙箱能力承载只读默认策略；缺失时由 audit 检查工作区 diff。

### HermesAgent

- 提供 `profiles/hermesagent.md`，将五类角色映射到 Hermes 的 skill、tool 和 sub-agent 概念。
- 不依赖 Hermes 的专属 memory 格式；研究状态始终以 `research-run/` 工件为准。
- 若 Hermes 支持持久会话，保存 `run_manifest` 和 checkpoint；若不支持，下一次运行从工件恢复。
- 模型身份、工具调用和失败信息若无法自动获取，必须在 manifest 中标记 `unobserved`，不能伪造运行记录。

### 通用适配验收

每个平台都必须通过同一组黑盒测试：

- 能否完整加载研究规格和角色约束。
- 能否产出符合 schema 的 source/evidence/claim。
- 是否会在证据不足时输出 `insufficient/unknown`。
- 是否能发现一组预置的冲突来源。
- 中断后能否从最近 checkpoint 继续而不重复计费/覆盖工件。
- 是否能阻止默认远程写入。
- 最终报告能否反向定位到 evidence。

平台 profile 只做映射和降级，不得降低核心质量门禁。

## 七、分阶段实施路线

### M0：协议冻结（第 1 周）

交付：核心 `SKILL.md` 草案、N 轮澄清协议、五类角色定义、工件 schema、状态机、错误分类、报告模板。

验收：不依赖任何平台即可通过人工 walkthrough；所有阶段有输入、输出和 Gate；未知和冲突有明确表示；用户需求在未完成确认前不会进入正式搜索。

### M1：参考实现与门禁（第 2-3 周）

交付：Markdown/JSON 工件模板，引用完整性、claim 覆盖、来源去重、冲突登记、PII/secret 扫描和 run manifest 校验脚本。

验收：故意注入无引用结论、失效 URL、冲突来源、错误单位和敏感字段时，门禁能够失败并指出位置。

### M2：单 Agent 基线（第 3-4 周）

交付：不依赖子 Agent 的串行工作流，支持用户提供链接、本地 Markdown/PDF 和 runtime 已有的一种网页搜索工具；支持 `clarification_rounds` 参数。

验收：两个 demo 问题完整跑通；中断恢复不丢失已登记证据；输出包括 final report 和 run bundle。

### M3：多 Agent 协作（第 5-6 周）

交付：discoverer、verifier、challenger 的并行/串行调度模板，独立性声明和证据加权规则。

验收：重复来源不会被计为独立证据；反方来源会进入 conflict/review；综合 Agent 无法读取未经 Gate 的草稿结论。

### M4：OpenClaw 与 HermesAgent 适配（第 7-8 周）

交付：两个 capability profile、安装说明、降级模式、黑盒兼容测试和平台差异说明。

验收：同一 `research_spec` 在两个平台产生结构等价的工件；至少一个平台无子 Agent 时仍能完成串行模式。

### M5：Benchmark 与发布（第 9-10 周）

交付：golden set、自动评分脚本、成本/延迟报告、失败案例库、版本化发布包。

验收指标：claim coverage、unsupported claim rate、citation correctness、conflict recall、abstention quality、恢复成功率、成本和 PII 泄漏率达到预设阈值。

## 八、首版 Benchmark 设计

至少准备四类案例：

1. 普通事实问题：测试基本覆盖和引用。
2. 时间敏感问题：测试发布日期、截至日期和过期来源处理。
3. 冲突问题：提供互相矛盾的一手/二手来源，测试是否显式报告冲突。
4. 私有材料问题：测试本地文件、脱敏、只读权限和来源边界。

每个案例保存人工标注：关键 claims、必要来源、可接受答案范围、反例、应当拒答的部分和隐私陷阱。

另加三项需求澄清指标：

- **规格完整率**：正式搜索前，研究对象、目标、范围、截止时间和交付标准是否齐全。
- **澄清效率**：达到用户确认所需轮数、问题数和用户回答负担。
- **误导率**：方向侦察是否把用户过早锚定到某一解释；多解释案例中应保留至少两个候选解释直到用户确认。

## 九、风险和控制措施

| 风险 | 控制 |
|---|---|
| Agent 把流程当成建议而跳步 | 将关键检查脚本化；阶段 Gate 失败即停止综合 |
| 多 Agent 共享同一盲点 | 来源路径隔离、不同工具/模型、独立 challenger |
| 上下文过大 | Agent packet 小型化；只传递 ledger 摘要和必要原文 |
| 工具限流/重复收费 | URL 缓存、幂等 key、指数退避、预算门禁 |
| 结果过度确定 | 强制 `unknown/insufficient` 状态和 abstention benchmark |
| 平台 API 变化 | 核心协议与 profile 分离；平台适配只依赖 capability contract |
| 私有信息外泄 | 默认只读、发送前扫描、来源分级和审计日志 |
| 报告很长但无用 | 先验收 claim coverage 和 citation correctness，再渲染 prose |

## 十、首版完成定义

首版只有同时满足以下条件才发布：

- 核心 `SKILL.md` 不包含平台专属调用逻辑。
- OpenClaw、HermesAgent 至少各有一个可执行 capability profile。
- 单 Agent 降级模式和多 Agent 完整模式使用同一工件协议。
- 每个最终事实 claim 都能反向定位到 evidence。
- 冲突、未知、检索失败和低置信度会进入最终报告。
- 研究可以从 checkpoint 恢复，且不覆盖原始来源。
- 自动门禁能阻止无证据结论、失效引用和敏感信息泄漏。
- benchmark 报告同时给出质量、成本、延迟和恢复结果。
- 支持 `clarification_rounds: auto|N`；每轮问答、方向侦察和最终规格确认均可审计。
- 正式搜索只使用 runtime 已有工具；没有搜索能力时能够透明降级并披露覆盖限制。

## 十一、推荐的实际启动顺序

先冻结协议和门禁，再做单 Agent 基线；单 Agent 的工件和质量检查稳定后，加入并行角色；最后才做 OpenClaw、HermesAgent 的 profile 和安装适配。这样平台变化只影响适配文件，不会反复重写研究方法和质量标准。

## 十二、v0.1.0 发布验收状态

本版本完成了可在没有特定 Agent runtime 的环境中复核的部分：

- 协议、N 轮澄清、方向侦察隔离、证据账本、冲突和恢复规则已固化。
- 串行降级与多 Agent 协作使用同一工件协议；OpenClaw、HermesAgent 和 generic profile 已提供安装/调用/权限/恢复映射。
- `probe_runtime.py` 根据平台实际导出的 capability JSON 选择 `complete`、`serial-degraded` 或 `blocked`，不会从平台名称推断能力。
- `validate_skill.py`、研究 run gates、四类 benchmark 和 `release_check.py` 可离线重复执行，CI 使用同一入口。
- Gitea 与 GitHub 镜像的 tag/release 采用“先推 Gitea tag，再同步 GitHub，再创建 GitHub release”的顺序。

本机未安装 `openclaw` 或 `hermes` 命令，因此平台黑盒安装、真实子 Agent 调用和 runtime 权限探测留作发布后的兼容性矩阵工作；仓库内的 capability JSON 明确标为协议 fixture，不冒充黑盒测试结果。
