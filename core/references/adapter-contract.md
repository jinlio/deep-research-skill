# Runtime Capability Contract

平台适配只负责将宿主能力映射到以下抽象操作，不能改变研究规则：

| 操作 | 输入 | 最低输出 |
|---|---|---|
| `load_skill` | skill 根目录 | 已加载入口和 references |
| `discover_sources` | 查询、来源限制 | 候选 URL、标题、摘要、检索状态 |
| `fetch_source` | URL/路径 | 原始响应、访问状态、抓取时间 |
| `read_source` | URL/路径 | 原文、位置、访问状态 |
| `delegate` | 角色、任务、工件路径 | Agent packet 或失败状态 |
| `artifact_io` | 相对路径、追加内容 | 写入结果和 hash |
| `checkpoint` | run manifest | 可恢复的状态标识 |
| `audit` | run 目录 | 可机器解析的通过/失败结果 |

能力探测顺序：加载 skill → 读取/写入临时工件 → 分别调用一次只读来源发现与抓取 → 验证子 Agent（若有）→ 验证恢复 → 验证权限。任何失败都记录为 capability 缺失并启用降级模式。旧版仅提供 `search` 时可映射为发现与抓取，但应标记为兼容推断，不能算作已测试。
