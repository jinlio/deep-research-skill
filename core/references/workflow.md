# 标准研究工作流

1. Intake：按深度模式执行 `clarification_rounds` 的递进式追问，固化 `research_spec.yaml`。
2. Plan：拆分子问题、来源路径、反方任务、预算和停止条件。
3. Discover：调用宿主已有搜索/浏览工具登记候选来源；搜索失败必须记录。
4. Extract：从原文提取带位置的 evidence，不使用搜索摘要替代原文。
5. Verify：逐 claim 核验支持、反驳、时效、适用范围和置信度。
6. Challenge：独立寻找反例、遗漏、定义偷换和过度推断。
7. Synthesize：只综合已通过门禁的 evidence；区分 fact、inference、opinion、unknown。
8. Audit/Deliver：运行确定性检查，生成报告和完整 run bundle。

## 深度模式与澄清轮次

`research_spec.yaml` 的 `depth` 决定默认澄清预算；显式设置 `clarification_rounds: N` 时以 N 为准：

| depth | 默认澄清轮次 | 上限（auto 时） | 问题轮是否必需 |
|---|---|---|---|
| `quick` | 0 轮 | 1 | 否（假设必须写入规格并展示给用户） |
| `standard` | 1 轮 | 2 | 是 |
| `deep` | 2–3 轮 | 5 | 是 |

任何模式下用户都可以说"按当前理解开始"提前结束澄清；达到上限仍有未决项时，必须把假设显式写入 `research_spec.yaml` 并让用户确认，不得静默猜测。方向侦察最多少量查询，必须覆盖至少两个可能解释，且不得进入最终引用。

## 证据核验（可选，网络模式）

登记来源后可运行 `python scripts/verify_evidence.py <run_dir>`，把每条 evidence 的原文摘录与来源页面做回贴匹配，生成 `verification.jsonl`；`run_gates.py --require-verified` 会要求高影响 claim 至少有一条 `verified` 证据。核验是增强门禁，不是搜索的替代：`unverifiable` 必须如实标注，不得当作通过。

