# SQLite vs DuckDB for Embedded Analytics

深度模式：`standard`（1 轮澄清 + 最终确认） · 运行时间：2026-10-24 · 核验：7/7 条证据已回贴原文（`verification.jsonl`）

## 结论

- [C-001] **两个项目都把自己定位为进程内本地引擎，而非 client/server 数据库**（高影响，两个独立官方来源支持，置信度高）。
- [C-002] SQLite 官方文档明确将其定位为本地存储与应用文件格式，"SQLite does not compete with client/server databases. SQLite competes with fopen()."（置信度高）。
- [C-003] DuckDB 面向分析型负载、零外部依赖、完全内嵌于宿主进程（置信度高）。
- [C-004] **仅凭官方文档无法划定两者在小规模分析负载上的边界**——状态为 `insufficient`：双方文档描述的适用范围重叠（SQLite 称 10 万 hits/day 以下"works fine"，DuckDB 称分析型用例是其目标），但都没有给出对比基准数据（置信度低，见冲突 CF-001）。

## 证据与冲突

每条结论都绑定带位置信息的原文摘录（见 `evidence.jsonl`）；来源为三个官方文档页（`sources.jsonl`，独立性分组 sqlite-org / duckdb-org）。C-004 的边界张力记录在 `conflicts.jsonl`（CF-001），处置方式是"undecided"，而不是择一断言。

## 交付建议

- 默认嵌入式存储选型应先跑**工作负载基准**再定边界；文档共识只支持"两者都是进程内引擎"这一层结论。
- 引用核验：`python scripts/verify_evidence.py <run_dir>` 会重新抓取来源并逐条回贴本报告引用的原文摘录；本次运行 7 条全部 `verified`。

## 限制

- 未覆盖：第三方基准（如 CLICK-bench 类）、实际数据更新模式对 WAL/检查点行为的影响。
- 引文抓取于 2026-10-24；页面内容可能随时间变化，核验记录含 `content_sha256` 与时间戳。
