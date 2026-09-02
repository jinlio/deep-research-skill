# Deep Research Skill

多 Agent 通用深度调研 skill：以研究规格、证据账本、独立审查和质量门禁为核心，复用宿主 Agent 已有的搜索、浏览、文件和 MCP 工具。

## 当前状态

项目处于协议设计与参考实现阶段。总体调研结论见 [`research_findings.md`](research_findings.md)，实施路线见 [`implementation_plan.md`](implementation_plan.md)。

## 设计目标

- 先通过可配置的 N 轮追问确认研究需求，再开始正式检索。
- 不绑定搜索服务或 Agent runtime；OpenClaw、HermesAgent、Codex、Claude Code 等通过 capability profile 适配。
- 每条重要结论都能回溯到带位置的原文证据。
- 显式报告冲突、未知、证据不足、检索失败和停止原因。
- 研究过程可恢复、可审计，默认只读并保护敏感信息。

## 目录

```text
SKILL.md                  # 核心工作流入口
references/               # 协议、证据、门禁和报告规则
profiles/                 # 各 Agent runtime 的能力映射
scripts/                  # 确定性检查与工件校验
benchmarks/               # golden set 和评估用例
tests/                    # 协议与门禁测试
examples/                 # 最小可运行示例
```

## 原则

最终报告是派生物，`sources`、`evidence`、`claims` 和 `conflicts` 才是事实基础。没有证据时必须输出 `unknown` 或 `insufficient`，不能用流畅文字掩盖缺口。

