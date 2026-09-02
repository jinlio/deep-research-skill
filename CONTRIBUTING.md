# Contributing

## 开发检查

项目只使用 Python 标准库。提交前运行：

```bash
python scripts/release_check.py
```

新增研究规则时，请同时更新相应的 `references/`、至少一个 fixture 和测试。平台差异应放在 `profiles/`，不要把平台 API 写入核心 `SKILL.md`。

## 工件和安全

不要提交真实用户材料、API key、token、私有 URL 或运行输出。研究工件必须保持 `claim -> evidence -> source` 可追溯；冲突和 unknown 不得被删除来让门禁通过。

