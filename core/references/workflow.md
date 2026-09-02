# 标准研究工作流

1. Intake：执行 `clarification_rounds: auto|N` 的递进式追问，固化 `research_spec.yaml`。
2. Plan：拆分子问题、来源路径、反方任务、预算和停止条件。
3. Discover：调用宿主已有搜索/浏览工具登记候选来源；搜索失败必须记录。
4. Extract：从原文提取带位置的 evidence，不使用搜索摘要替代原文。
5. Verify：逐 claim 核验支持、反驳、时效、适用范围和置信度。
6. Challenge：独立寻找反例、遗漏、定义偷换和过度推断。
7. Synthesize：只综合已通过门禁的 evidence；区分 fact、inference、opinion、unknown。
8. Audit/Deliver：运行确定性检查，生成报告和完整 run bundle。

需求澄清默认 2 轮、最多 5 轮；用户可提前确认。方向侦察最多少量查询，必须覆盖至少两个可能解释，且不得进入最终引用。

