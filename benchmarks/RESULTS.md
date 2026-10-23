# Benchmark Results

> **状态：协议与评估器就绪，等待首次公开跑分。** 本仓库的原则是不把 fixture 冒充黑盒结果（见 `runtime_validation.md` 的区分），所以本文件在真实运行完成前不填任何数字。

## 指标定义

| 指标 | 含义 | 数据来源 |
|---|---|---|
| claim coverage | 必答 claim 被回答的比例 | `evaluate_benchmark.py` |
| abstention quality | 应拒答 claim 输出 unknown/insufficient 的比例 | 同上 |
| **fabrication trap pass** | 预埋的"可信假事实"没有被写成 supported 的比例 | 同上（`must_not_support_claim_ids`） |
| conflict recall | 预置冲突被显式报告的比例 | 同上 |
| privacy | 无隐私违规 | 同上 |
| **citation verification rate** | 证据原文摘录在来源页面上回贴成功的比例（verified + verified_fuzzy）/ 总数 | `verify_evidence.py` 的 `verification.jsonl` |
| token cost / wall time | 每次 run 的成本与时长 | `run_manifest.json` |

## 首次公开评测协议（待执行）

1. 选 10–20 个可公开复核的问题，覆盖五类 case（普通事实 / 时间敏感 / 冲突 / 私有材料 / **造假引文陷阱**）。
2. 每个问题在同一 runtime（Claude Code）跑两次：本 skill 工作流 vs 裸 WebSearch 流程；记录 run bundle。
3. 对两组结果运行 `evaluate_benchmark.py` + `verify_evidence.py`，汇总上表指标。
4. 结果（含失败案例）提交到本文件，并附可复现命令与 run bundle 归档链接。
5. 已知的诚实成本：人工复核 citation correctness（引用是否真的支持该句）仍需抽样标注，评估器只做确定性部分。

## 基线引用（外部，2026）

这些是本 skill 动机的公开基准数据，用于对比时引用：

- INRA（2026-10）：各 AI 研究工具生成引用中 39.6%–55% 完全捏造。<https://www.inra.ai/blog/ai-hallucinations>
- FACT 框架（arXiv 2026-04）：OpenAI Deep Research 引用准确率约 78%。 <https://arxiv.org/html/2604.03173v1>
- VerusCite V1：记录到一份 12 条引用全部捏造的 Deep Research 报告。<https://www.crimrxiv.com/pub/s63si1hl>

本 skill 的目标不是宣布这些数字的普适性，而是提供一个可以**逐 claim 复核**的流程，让任何一份报告的引用正确率可以被独立测量。
