# 多 Agent 通用深度调研 Skill：现状、痛点与需求

调研日期：2026-09-02（中国标准时间）  
范围：本机已安装/可见的 Codex skills、GitHub 开源项目、ClawHub skill registry。  
目标：找出一个跨领域、跨 Agent runtime 的通用深度调研 skill 应该解决的真实问题，而不是重复做一个搜索器。

## 1. 结论先行

当前生态已经有很多“能搜索并生成报告”的系统，但缺少一个轻量、可移植、与具体框架解耦的**研究协议层**。主要缺口是：

1. **研究问题没有被形式化**：很多系统从一句自然语言直接生成搜索词，缺少范围、时间点、定义、决策对象和停止条件。
2. **多 Agent 并不等于独立验证**：常见做法是并行分工后由一个 writer 拼接；Agent 之间共享相同搜索偏差，容易产生重复证据和“多数投票式幻觉”。
3. **证据不可追溯到 claim**：报告有链接不代表每个关键结论都有精确出处、原文片段、发布日期和适用范围。
4. **冲突与未知没有一等地位**：系统倾向于合成单一结论，较少明确记录相互矛盾的来源、证据不足、未检查的方向和“无法判断”。
5. **质量门禁和验收标准不统一**：大多数项目把检索数量/字数当作深度代理，缺少覆盖率、来源质量、独立性、时效性、引用正确率等可测指标。
6. **运行过程不够可恢复、可审计、可控成本**：长任务会遇到超时、限流、上下文膨胀、工具故障和中途退出；很多系统只能重跑，或只能恢复粗粒度状态。
7. **现有方案要么是重型应用，要么是垂直 skill**：缺少能在 Codex、Claude Code、OpenClaw、CLI 等环境用同一套输入/输出协议运行的通用层。

因此，本项目的差异化不应是“再做一个 research agent”，而应是：**用可验证的研究计划、证据账本、独立审查和可恢复工件，约束任意 Agent 完成高可信调研。**

## 2. 代表性方案横向扫描

| 项目/skill | 主要能力 | 已解决的问题 | 暴露的边界/痛点 |
|---|---|---|---|
| [GPT Researcher](https://github.com/assafelovic/gpt-researcher) | planner 生成问题，crawler 并行抓取，publisher 汇总；支持网页、本地文档、MCP、多 Agent | 并行检索、长报告、多来源、导出格式 | 主要以“抓更多站点、取共识”降低错误，不能替代逐 claim 核验；检索器、爬虫、模型和密钥依赖多；公开 issue 显示搜索复用旧元数据、空白字段绕过默认检索器、MCP transport 误判等可靠性问题；报告深度与来源独立性缺少统一验收标准 |
| [Open Deep Research](https://github.com/dzhng/deep-research) | breadth/depth 参数、递归生成后续方向、并发 SERP 处理，目标是小于 500 LoC | 简单、易读的递归研究骨架 | 只输出 Markdown 报告，研究状态/证据模型很薄；依赖 Firecrawl/OpenAI，免费额度会限流；公开 issue 包括“是否有足够 benchmark”“需要 MCP interoperability”“需要从中断处继续”“能否研究数据库/Excel”等，说明可评估性、互操作性、恢复能力和数据源覆盖仍是缺口 |
| [DeerFlow 2.0](https://github.com/bytedance/deer-flow) | super-agent harness，sub-agents、memory、sandbox、MCP、skills、artifact 和项目级能力 | 长任务编排、工具/私有数据集成、沙箱与持久状态、人机协作 | 这是完整平台而非可嵌入的研究协议；部署和配置复杂。公开 issue 数量很高，包含并发子 Agent 沙箱重试、Windows runtime、MCP cache、项目/记忆一致性等问题；平台能力不自动保证证据质量 |
| [LLM Wiki](https://github.com/nvk/llm-wiki) | immutable raw sources、增量编译、来源链、confidence、thesis for/against、lint/audit、并行 research | 目前最接近“持久证据库+研究协议”的开源实现 | 主要面向 wiki/个人知识库，协议和目录体系较重；其 issue 已直接指出：缺少 secret/PII redaction、footnote/link 未验证、`verified` 可能被自动设置、孤立发现缺 owner 等。这些正是通用研究 skill 需要内置的安全与 provenance 门禁 |
| [ARIS / Auto-claude-code-research-in-sleep](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep) | Markdown skills、跨模型 reviewer、review→fix→re-review、自省记忆、checkpoint、成本/流式重试 | 跨模型审查、长任务恢复、把 reviewer 原文持久化 | 偏 ML 论文/代码研究；配置和 README 很复杂，跨平台/模型/代理组合多；公开 issue 包括配置困难、Windows/LaTeX、结果屏蔽、子 skill 被跳过等。审查的是研究产物，不一定验证每条外部事实 |
| [Agent Laboratory / AgentRxiv](https://github.com/SamuelSchmidgall/AgentLaboratory) | 文献综述→实验→写作，专业 Agent 协作，checkpoint；AgentRxiv 允许研究互相积累 | 科研工作流分阶段、实验可执行、跨项目累积 | 需要 Python/数据集/模型/计算环境，适合科研而非通用事实调研；公开 issue 有 missing sections、timeout、依赖和 benchmark 不足，说明“能运行完整流程”和“稳定交付完整结果”之间有明显差距 |
| [AI Berkshire](https://github.com/xbtlin/ai-berkshire) | 4 个视角并行投研、反向思考、估值计算、多源交叉验证、结构化输出 | 领域化角色分工、反方分析、数值核算 | 强绑定投资领域和大师框架；评分/组合建议容易给人精确感，但不一定对应可复核证据；不能直接泛化到医疗、政策、技术尽调等领域 |
| ClawHub `academic-paper-writer` | IMRaD 写作、Zotero/PubMed 补充引用、迭代改稿 | 论文写作阶段的引用与结构约束 | 这是写作 skill，不是开放域研究编排；描述显示其针对特定用户、肾脏病学和本地 workspace，不能作为通用多 Agent 研究层 |
| ClawHub `discovery-engine` | 统计发现、hold-out 验证、FDR 校正、文献新颖性检查 | 对表格数据的统计验证和发现 | 强依赖外部 API/key，公共分析会发布数据/结果；只解决“数据模式发现”，不解决开放网页调研、来源冲突和跨 Agent 综合 |
| ClawHub `agent-constraints` | 把规则分到 hook、常驻指令、Skill、会话层；强调确定性门禁 | Agent 治理、规则分层、验证证据 | 不是调研 skill，但它揭示了一个关键事实：仅靠 SKILL.md 的建议性文字会失守，必须把可确定检查放到脚本/hook/CI；其自身也强调规则成本、跨会话恢复和实测验证 |

ClawHub 的 `api/v1/skills?q=...` 检索结果显示，当前公开目录以垂直 API、内容生产和单任务 skill 为主；在“research / literature / multi-agent”相关结果中，没有发现一个广泛采用的、跨领域多 Agent 深度调研协议。ClawHub 更适合作为工具和数据源能力的发现层，而不是研究质量标准的来源。

## 3. 本机现有 skills 的启示

本机可见的 `paper-spine` 是最成熟的流程型参考。它采用：配置 intake、阶段化 playbook、每阶段 gate、resume-first、citation bank、integrity audit、最终 artifact audit，并明确禁止编造数据/引用。这些做法值得迁移到通用调研 skill。

但它也有明显边界：流程面向论文写作和 LaTeX/Word 交付，阶段数量多、产物重，且需要用户在“动机确认”等节点介入。通用调研 skill 应保留“阶段 gate + 可恢复工件 + 引用完整性”，去掉论文投稿特有的负担。

`llm-wiki` 和 ARIS 进一步说明：研究结果要想长期复用，必须保存原始来源、来源哈希/时间、研究计划、每轮状态、审查原文和缺口，而不能只保存最终 prose。

## 4. 需要解决的核心痛点（按优先级）

### P0：事实和引用可信度

- 一条结论可能由多个 Agent 重复转述，却没有新增独立证据。
- URL 失效、页面更新、搜索摘要与正文不一致时，报告仍可能照常完成。
- 关键数字、日期、因果关系、比较结论没有逐项绑定证据片段。
- 来源之间冲突时，writer 往往偷偷选择一个版本。
- 模型会把“未检索到”写成“并不存在”，把低质量二手文章写成事实。

**应对方向**：建立 claim-evidence ledger。每个 claim 必须有来源 URL、标题、作者/机构、发布日期、抓取时间、原文摘录、来源类型、适用范围、支持/反驳关系和 confidence；没有证据的内容只能进入 `hypothesis` 或 `unknown`，不能进入事实结论。

### P0：多 Agent 的独立性与协作质量

- 简单按“Agent A/B/C 各搜一遍”会产生相关性很高的重复结果。
- 角色分工不等于认知多样性；同一模型、同一检索器、同一 prompt 会共享盲点。
- 最终汇总常变成“多数投票”，而不是按证据强度合成。
- reviewer 看到的是 writer 过滤后的材料，无法发现遗漏或选择性取证。

**应对方向**：研究计划中声明独立路径（官方/学术/反方/数据/历史/用户指定来源）；对关键 claim 做 blind evidence review；综合按证据质量、独立性和可复核性加权，不按 Agent 数量投票；允许不同模型或不同工具担任反方审查者。

### P0：研究边界、停止条件和反偏见

- breadth/depth 参数容易被误认为“深度”，但不表示问题覆盖完整。
- 没有显式的时间点、地域、定义和排除范围，导致答非所问。
- 研究会围绕最初叙事越挖越深，确认偏见越来越强。
- 研究何时完成通常靠模型主观判断，成本不可预测。

**应对方向**：先生成并确认 research spec：目标问题、子问题树、决策标准、时间/地域范围、来源优先级、反证问题、停止规则、预算上限。每轮根据“未覆盖 claim、冲突、信息增益/成本”选择下一步；连续低信息增益时自动收敛并报告剩余缺口。

### P1：可恢复、可审计、可复用

- 长任务遇到限流、超时或上下文压缩后，常只能重跑。
- 只存最终报告，无法回答“这句话是谁查的、何时查的、用的什么版本”。
- 不同 Agent runtime 没有统一的中间产物协议，迁移成本高。

**应对方向**：采用 append-only run manifest 和小型 JSON/Markdown 工件：`research_spec`、`source_registry`、`claim_ledger`、`agent_packets`、`conflict_log`、`review_report`、`final_report`。每一步幂等、可重试、可从最近 checkpoint 继续，并保存模型/工具版本与内容 hash。

### P1：成本、延迟与工具失败

- 并发抓取会触发 QPS/额度限制；重试可能重复收费。
- 让强模型做所有工作成本高，弱模型又可能导致检索和结构化输出失败。
- 网页动态渲染、robots、登录、地区限制和 PDF 解析会让“搜索成功”不等于“正文可用”。

**应对方向**：按任务风险分层模型；先廉价发现、后高质量核验；缓存 URL 内容和摘要；预算感知调度；指数退避和幂等 key；为每个来源记录 `retrieval_status`；在最终报告中披露检索失败和未覆盖范围。

### P1：隐私、安全和副作用

- 用户私有文档、API key、PII 可能被传给外部 Agent/检索器。
- 具有写权限的“研究 Agent”可能修改文件、远程资源或发布结果。
- ClawHub skill 的能力和数据处理边界不总是显式可见。

**应对方向**：默认只读；来源分级（公开/私有/敏感）；发送前做 secret/PII 扫描和脱敏；工具声明权限和数据流；远程写操作需显式批准；报告记录使用过的外部服务和数据保留策略。

### P2：交付格式和用户可理解性

- 很多报告“看起来很完整”，但读者无法快速区分事实、推断、意见和建议。
- 只给链接列表，不能让用户复核关键段落。
- 没有按决策者需要输出“结论、依据、反证、风险、下一步”。

**应对方向**：固定报告骨架：执行摘要、研究范围、结论表、claim-evidence 表、冲突/反方、置信度、缺口、方法与成本、来源清单。支持 Markdown/JSON，其他格式作为渲染层而不是事实源。

## 5. 建议的通用 Skill 设计

### 5.1 核心协议，而不是特定框架

输入最小字段：

```yaml
question: "要研究的问题"
goal: "要支持的决策或产出"
scope: {time: "截至日期", geography: "范围", domain: "领域"}
constraints: {budget: "token/金额", deadline: "时长", privacy: "public|private"}
sources: {preferred: [], forbidden: [], user_materials: []}
depth: "quick|standard|deep"
```

Agent 只需要遵循协议；具体的搜索、浏览、PDF、数据库和 MCP 工具由 runtime 注入。这样可以在 Codex、Claude Code、OpenClaw 等环境复用同一套方法。

### 5.2 推荐流水线

1. **Intake**：澄清问题，生成可验收的 research spec。
2. **Plan**：拆分子问题，指定来源路径、独立 Agent、反方任务和停止条件。
3. **Discover**：宽搜候选来源，去重，登记来源元数据；发现阶段不下最终结论。
4. **Extract**：从原文提取带位置的证据片段，写入 source registry 和 evidence packets。
5. **Verify**：逐 claim 核验、交叉来源、检测冲突、标注时效和置信度。
6. **Challenge**：独立 reviewer 寻找遗漏、反例、反方来源和过度推断。
7. **Synthesize**：按 claim 和证据强度综合，明确区分 fact/inference/opinion/unknown。
8. **Gate**：运行可机器检查的质量门禁；失败则回到对应阶段，不直接修饰最终 prose。
9. **Deliver**：输出报告、机器可读 ledger、来源包、研究日志和未解决问题。

### 5.3 最小质量门禁

- 每个高影响 claim 有至少一个可访问的一手/权威来源，关键 claim 有第二个独立来源。
- 每个引用包含 URL、标题、发布日期/抓取时间和原文片段。
- 关键数字有单位、时间点和计算过程；计算由脚本完成，不由模型心算。
- 冲突来源被显式列出；没有“静默择一”。
- 报告中的事实 claim 可反向定位到 ledger；ledger 中的来源可打开或标记失效。
- 明确列出未覆盖子问题、检索失败、低置信度和停止原因。
- 运行 manifest 记录 Agent、模型、工具版本、重试和成本。
- 敏感输入通过脱敏/权限检查；默认不执行远程写操作。

### 5.4 评估指标（不要只看字数）

建立小型 golden set，每个问题带人工标注的关键 claim、权威来源和常见陷阱，评估：

- claim coverage / unsupported claim rate
- citation correctness（引用是否真正支持该句）
- source quality、source diversity、source independence
- contradiction recall、abstention quality（该说“不知道”时是否拒答）
- freshness / temporal correctness
- plan coverage、stop-condition precision
- recovery success rate、tool failure handling
- token/金钱成本、端到端延迟、重复检索率
- PII/secret 泄漏率和未授权副作用数

公开 issue 中“是否有足够 benchmark”的反复出现，说明这一层是生态共同短板；本 skill 应把评估协议和示例数据作为一等交付物。

## 6. MVP 建议

第一版不要尝试覆盖所有工具或自动化所有领域，先做一个可迁移的协议和参考实现：

- 一个短 `SKILL.md`，只定义触发条件、阶段、工件和硬规则。
- `references/`：研究 spec 模板、claim ledger schema、来源评分、冲突处理、报告模板、恢复协议。
- `scripts/`：URL/引用完整性检查、claim-证据覆盖检查、重复来源检测、PII/secret 扫描、run manifest 校验。
- 默认 3 类 Agent：discoverer、verifier、challenger；writer 只消费已通过门禁的 evidence packets。
- 先支持网页 + 本地 Markdown/PDF + 用户指定链接，工具适配通过 MCP/CLI 插件完成。
- 输出 Markdown + JSON；不把 PDF/Word 作为第一版事实源。
- 提供两个 demo：一个开放域事实问题，一个存在冲突/时效性的决策问题。

最重要的验收标准是：当来源不足或互相矛盾时，系统能稳定地输出“证据不足/存在冲突/需要人工决定”，而不是生成一篇读起来流畅但不可复核的文章。

## 7. 来源与可复核链接

- [GPT Researcher README](https://github.com/assafelovic/gpt-researcher)
- [GPT Researcher issues](https://github.com/assafelovic/gpt-researcher/issues)
- [Open Deep Research README](https://github.com/dzhng/deep-research)
- [Open Deep Research issues](https://github.com/dzhng/deep-research/issues)
- [DeerFlow 2.0 README](https://github.com/bytedance/deer-flow)
- [DeerFlow issues](https://github.com/bytedance/deer-flow/issues)
- [LLM Wiki README](https://github.com/nvk/llm-wiki)
- [LLM Wiki protocol / AGENTS.md](https://github.com/nvk/llm-wiki/blob/main/AGENTS.md)
- [LLM Wiki issues](https://github.com/nvk/llm-wiki/issues)
- [ARIS README](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep)
- [ARIS issues](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/issues)
- [Agent Laboratory README](https://github.com/SamuelSchmidgall/AgentLaboratory)
- [Agent Laboratory issues](https://github.com/SamuelSchmidgall/AgentLaboratory/issues)
- [AI Berkshire README](https://github.com/xbtlin/ai-berkshire)
- [ClawHub](https://clawhub.ai/) 与 [ClawHub skills API](https://clawhub.ai/api/v1/skills)

注：GitHub stars、issue 数量和 ClawHub 下载量是动态指标，只用于判断生态活跃度，不作为技术质量证明。README 是项目自述；本报告用公开 issue 和本机实际 skill 文档补充其边界，结论仍应通过后续 benchmark 验证。
