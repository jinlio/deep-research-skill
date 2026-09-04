# Capability JSON

`probe_runtime.py` 接受一个 capability JSON 文件。平台适配器应记录“实际观察到的能力”，而不是根据平台名称猜测。仓库里的 `*.example.json` 只是协议 fixture，不代表本机已经安装并黑盒验证了对应 runtime：

```json
{
  "runtime": "openclaw",
  "version": "observed-version",
  "observed_at": "2026-09-02T00:00:00Z",
  "capabilities": {
    "load_skill": {"available": true, "details": "workspace skills/"},
    "discover_sources": {"available": true, "tested": true, "mode": "host-provided", "evidence": ["search-smoke"]},
    "fetch_source": {"available": true, "tested": true, "mode": "host-provided", "evidence": ["fetch-smoke"]},
    "read_source": {"available": true},
    "delegate": {"available": true, "parallel": true},
    "artifact_io": {"available": true, "append_only": true},
    "checkpoint": {"available": true, "durable": true},
    "audit": {"available": true}
  },
  "permissions": {"external_write_default": false}
}
```

每项能力建议使用对象声明：`available` 表示宿主声称可用，`tested` 表示本次 runtime smoke test 已验证，`mode` 描述实现方式，`evidence` 列出验证工件（如 `run_manifest.json`）。旧版布尔值仍兼容，但会被视为 `tested: false`。

能力拆分为 `discover_sources`（搜索/发现候选来源）、`fetch_source`（抓取来源内容）和 `read_source`（解析/读取内容）。旧版 `search` 字段仍可作为两者的兼容别名。`available: false` 的能力必须进入输出的 `degradations`；`load_skill`、`artifact_io` 或 `external_write_default: true` 会使探测失败。探测器不调用网络，也不修改 runtime 配置。
