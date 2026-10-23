# 质量门禁

- 研究规格有目标、范围、时间点、停止条件和用户确认。
- 澄清日志记录理解回显、问题轮次、用户回答和最终确认；方向侦察不得进入正式工件。
- 高影响 claim 默认至少有两条证据，且来自不同 `independence_group`；可用 claim 字段 `minimum_evidence` 显式提高门槛。
- 每条引用包含 URL/路径、标题、时间、原文片段和位置。
- 数字包含单位、币种、时间点和可复算过程。
- 冲突、未知、失效来源和检索失败没有被静默隐藏。
- 报告中的事实 claim 都能回溯到 evidence。
- 运行记录包含 Agent、模型、工具、重试、错误和成本。
- 敏感输入通过脱敏/权限检查，默认无远程写入。

## 增强门禁（可选）

- `run_gates.py --verify-network`：抓取每个来源页面，逐条回贴定位 evidence 的原文摘录，结果写入 `verification.jsonl`（`verified` / `verified_fuzzy` / `mismatch` / `unavailable` / `unverifiable`）。
- `run_gates.py --require-verified`：高影响 claim 必须至少有一条 `verified` 证据；任何 `mismatch`（引文未出现在来源页面上）直接失败。网络模式只允许 http/https，并拒绝解析到环回、私有或保留地址的主机。
- 核验是增强而非搜索的替代：`unverifiable`（如 PDF、动态页面）必须如实标注，不得当作通过。
