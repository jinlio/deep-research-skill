---
name: deep-research
description: Evidence-first deep research: clarify goals, verify every claim against original sources, expose conflicts, deliver auditable reports. 深度调研：先澄清，再核验证据，可审计。
version: 0.3.0
license: MIT
homepage: https://github.com/jinlio/deep-research-skill
---

# Deep Research

一个运行时无关的证据优先研究工作流。本文件自足：即使附属 references 缺失，也应按下面的硬规则和执行顺序完成研究。安装整个仓库目录时，`core/references/`、`scripts/`、`profiles/` 会一并可用。

This file is self-sufficient. When the repository is installed as a skill directory (for example via `npx skills add jinlio/deep-research-skill`), `core/references/`, `scripts/`, and `profiles/` are available next to it.

## 硬规则（不可省略）

1. 正式搜索前完成需求澄清和用户确认；方向侦察只能标记为 `orientation_only`。
2. 搜索摘要不是证据；事实 claim 必须绑定可定位的原文片段或结构化数据。高影响 claim 默认需要至少两条来自不同 `independence_group` 的 evidence。
3. 冲突、未知、检索失败和低置信度必须显式记录，不得静默择一。
4. 只使用宿主 Agent 已有工具；不得假设或安装特定搜索服务。
5. 最终报告只能消费通过核验和反方审查的工件；没有证据时输出 `unknown` / `insufficient`。
6. 默认只读；不得更改权限、审批、沙箱、工具配置、网络配置或凭据。任何远程写入或发布都需要用户明确授权。

## 执行顺序

1. 读取 `core/references/workflow.md`（缺失时按本文件执行）、当前 runtime profile（`profiles/<runtime>.md`）和 `core/references/adapter-contract.md`。
2. 如需方向侦察，用宿主已有搜索/浏览工具做少量查询并记录为 `orientation_only`；不要把工具存在误认为 capability 已测试。
3. 按深度模式完成澄清（见下表），得到用户确认的 `research_spec.yaml`。
4. 按 Plan → Discover → Extract → Verify → Challenge → Synthesize → Audit 执行；每阶段只消费上一阶段通过门禁的工件。
5. 交付前运行 `python scripts/run_gates.py <run_dir> --require-final --fail-on-pii`（脚本缺失时按 `core/references/quality-gates.md` 逐条自查并在报告中说明）。通过后才交付 `final_report.md` 和完整 run bundle。

## 深度模式

| depth | 澄清轮次 | 适用 |
|---|---|---|
| `quick` | 0 轮（假设显式写入 research_spec 并展示） | 简单事实盘点、时间敏感查询 |
| `standard` | 1 轮 + 最终确认 | 大多数调研 |
| `deep` | 2–3 轮 + 最终确认 | 高影响决策、竞品/尽调 |

任何模式下用户都可以说"按当前理解开始"提前结束澄清；未决项必须作为显式假设写入 `research_spec.yaml`，不得静默猜测。

## 降级

没有子 Agent、结构化输出或持久 checkpoint 时，按 profile 的降级路径串行执行；降级原因必须写入 `run_manifest.json`，不得假装完整模式。

## 交付物

`final_report.md`（面向决策者）+ run bundle：`research_spec.yaml`、`clarification_log.jsonl`、`sources.jsonl`、`evidence.jsonl`、`claims.jsonl`、`conflicts.jsonl`、`run_manifest.json`。最终报告是派生物，账本才是事实基础。

## 源码仓库与安装包

本仓库根目录可直接作为 skill 安装（`npx skills add jinlio/deep-research-skill`）。如需生成按 runtime 裁剪的精简安装包，运行 `python scripts/build_adapters.py --output dist` 并安装 `dist/<runtime>/deep-research/`。
