# HermesAgent Capability Profile

此文件只描述 HermesAgent 到通用研究协议的映射，不依赖其专属 memory 格式。

适配时确认：skill/tool 加载、sub-agent 委派、工件读写、搜索工具、权限边界、状态恢复、模型/调用日志和结构化输出。

若平台无法观测某项运行信息，写入 `run_manifest.json` 的 `unobserved`，不得猜测或伪造。

