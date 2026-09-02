# Capability JSON

`probe_runtime.py` 接受一个 capability JSON 文件。平台适配器应记录“实际观察到的能力”，而不是根据平台名称猜测。仓库里的 `*.example.json` 只是协议 fixture，不代表本机已经安装并黑盒验证了对应 runtime：

```json
{
  "runtime": "openclaw",
  "version": "observed-version",
  "observed_at": "2026-09-02T00:00:00Z",
  "capabilities": {
    "load_skill": {"available": true, "details": "workspace skills/"},
    "search": {"available": true, "mode": "host-provided", "read_only": true},
    "read_source": {"available": true},
    "delegate": {"available": true, "parallel": true},
    "artifact_io": {"available": true, "append_only": true},
    "checkpoint": {"available": true, "durable": true},
    "audit": {"available": true}
  },
  "permissions": {"external_write_default": false}
}
```

`available: false` 的能力必须进入输出的 `degradations`；`load_skill`、`artifact_io` 或 `external_write_default: true` 会使探测失败。探测器不调用网络，也不修改 runtime 配置。
