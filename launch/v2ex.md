# V2EX / 掘金 帖子草稿

## 标题

```
做了个证据优先的深度调研 skill：每条引用都会被脚本重新回贴到原文页面核验
```

## 正文（V2EX /share 节点或掘金）

> AI 调研报告最大的问题不是内容少，是引用经不起核对：2026 年的几份分析显示各工具 39.6%–55% 的引用是捏造的，OpenAI Deep Research 也有约 22% 的引用 URL 不支持对应论断（数据出处见 README）。
>
> 所以我做了这个 Claude Code / Codex / OpenCode 通用的深度调研 skill，核心思路是把"核验"从提示词层面的请求变成确定性脚本：
>
> **工作流**：先 N 轮追问冻结 research spec（quick 模式 0 轮，假设显式记录）→ 检索登记来源 → 逐条摘录带位置的原文证据 → 每 claim 绑定证据 → 冲突/未知/检索失败单独建账 → 门禁通过才出报告。
>
> **核验引擎** `verify_evidence.py`：重新抓取每个来源页面，把证据摘录逐条回贴匹配（处理中英文标点/空白/省略号，CJK 友好）。找不到的判 `mismatch`，抓不到的判 `unavailable`，PDF 如实标 `unverifiable`——严格模式下高影响 claim 没有回贴成功的证据会直接拦住交付。纯标准库实现，抓取前校验 host，拒绝环回/私有/保留地址。
>
> **仓库里有个完整真实示例**（SQLite vs DuckDB 嵌入式分析选型）：7 条引用全部回贴 verified，其中一条边界结论诚实地标为"证据不足"，而不是硬给答案。还有个单文件 HTML 报告，鼠标悬浮引用能看到原文摘录和核验徽标。
>
> 安装：`npx skills add jinlio/deep-research-skill`，或 Claude Code 里 `/plugin marketplace add jinlio/deep-research-skill`。
>
> GitHub: https://github.com/jinlio/deep-research-skill （双语 README）
>
> 代价也说清楚：比裸搜索慢（要建账本）、默认只读不碰权限配置、公开 benchmark 还没跑完所以不贴通过率数字。中文来源（公众号/知乎/巨潮公告等）的引文定位方法论单独写在 core/references/source-playbook.zh.md。
>
> 欢迎拍砖，尤其是：澄清轮次对 CLI 场景是不是太重？要不要做一个"核验我手上已有的 ChatGPT/Gemini 报告"的独立模式？

## 发布注意

- V2EX 分享创造节点；掘金可选「人工智能」标签。
- 帖子里引用的外部数据（INRA / FACT）必须带原文链接，避免被打"编数据"。
- 有人质疑示例真实性时，给出 `verification.jsonl` 里的 content_sha256 和时间戳即可自证。
