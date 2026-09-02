# Benchmarks

# Benchmarks

golden set 覆盖普通事实、时间敏感、冲突来源和私有材料四类问题，并标注关键 claims、必要来源、反例、应拒答部分和隐私陷阱。

## 文件协议

每个 `cases/*.json` 至少包含 `case_id`、`category`、`prompt`、`required_claim_ids`、`must_abstain_claim_ids` 和 `expects_conflict`。运行结果为 JSONL，每行包含 `case_id`、`claims`（含 `claim_id` 和 `status`）、`conflicts`，私有材料案例还应包含 `privacy_violation`。

## 运行

```bash
python scripts/evaluate_benchmark.py benchmarks/cases benchmarks/fixtures/reference_results.jsonl
```

评分不替代人工的 citation correctness 审查；它只对 claim 覆盖、unknown/insufficient 拒答、冲突召回和隐私标记做确定性回归检查。
