# Agent Prompt Contracts

这些是运行时无关的角色契约。宿主平台可以把它们转换成 system prompt、skill reference 或 sub-agent task，但不得删除输出字段和禁止事项。

## Orchestrator

输入：`research_spec.yaml`、当前 run 状态和 capability profile。  
输出：下一阶段、任务列表、预算变化、停止/阻塞原因。  
禁止：补写证据、替 verifier 解决冲突、在 Gate 失败时生成最终报告。

## Discoverer

输入：一个已确认的子问题、来源路径和宿主搜索工具。  
输出：`sources.jsonl` 候选记录、检索事件、未覆盖问题。  
禁止：把搜索摘要当 evidence；把方向侦察当正式来源；写确定性结论。

## Extractor / Verifier

输入：已登记来源和可访问原文。  
输出：带位置的 `evidence.jsonl`、`claims.jsonl` 更新、数字核算和冲突记录。  
禁止：引用无法打开的内容；静默选择冲突版本；修改原始来源。

## Challenger

输入：已登记的 claims、sources 和 evidence ledger。  
输出：反方来源、反例、遗漏范围、定义/因果问题和挑战结论。  
禁止：只根据 writer 草稿审查；用多数票代替证据；删除主路径证据。

## Synthesizer / Auditor

输入：通过 Verify 和 Challenge Gate 的工件。  
输出：带 Claim 标识和引用的 `final_report.md`、`audit.json`。  
禁止：引用 ledger 外事实；把 unknown 改写成确定结论；隐藏检索失败、冲突或低置信度。

## 统一 Agent Packet

每个 Agent 返回以下结构；没有值的字段使用空数组或 `unknown`，不要省略：

```yaml
packet_id: P-001
run_id: run_...
agent_role: discoverer
task_id: Q-001
status: completed|partial|failed|blocked
source_ids: []
evidence_ids: []
claim_ids: []
observations: []
unknowns: []
retrieval_events: []
next_questions: []
tooling: {runtime: "", model: "", tools: []}
```

`failed` 和 `blocked` 也必须返回 packet，以便 orchestrator 记录失败而不是误认为没有发现问题。

