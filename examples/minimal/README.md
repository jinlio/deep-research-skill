# Minimal Fixture

`run/` 是一个完整的通过样例，故意包含一个被反驳并记录冲突的 claim。

验证：

```bash
python scripts/run_gates.py examples/minimal/run --require-final --fail-on-pii
python -m unittest discover -s tests -v
```

