# Day 17：重构前安全测试基线

第三阶段适配：应用仍从 `app.main` 导入；SessionLocal、AI、统计的 mock
查找位置迁至 `app.services.dataset_service`，日志在服务和 API 两层隔离。
旧状态测试的 AI patch 同步迁至服务层，但仍不得在业务库运行。
保留原 25 项测试断言，另加 3 项：completed 与分析记录同次提交、
AI 调用前事务已关闭、查询结果脱离会话；failed 标记提交失败的 rollback
与日志；failed 标记会话创建失败时保留原任务创建失败错误映射。
路由清单通过应用 `/openapi.json`
解析实际注册路径，兼容 FastAPI 的 included-router 容器；仍精确断言 9 个
方法/URL。

## 唯一推荐运行入口

在 `backend` 目录、新的 Python 进程中运行：

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -p 'test_*_baseline.py' -v
```

只收集本目录，不导入 backend 根目录的旧测试。不要使用全项目 pytest
收集来替代此命令。`-B` 避免新增 Python 字节码缓存。无需安装 pytest。

## 隔离方式与边界

- `test_services_baseline.py`：真实 CSV 加载、统计和规则洞察，内存独立数据。
- `test_api_baseline.py`：导入应用前，在 `sys.modules` 替换 `app.database`
  和 `app.services.ai_service`。不执行生产数据库配置，不读取 `.env`，
  不创建 DeepSeek 客户端。若应用已被导入，则拒绝运行。
- 使用真实模型和 SQLAlchemy，每项测试创建全新的 `sqlite://` 内存库；
  外键开启，StaticPool 支持 TestClient 工作线程。
- 清理只关闭测试会话并 dispose 内存 engine，没有按文件名删除数据，
  没有磁盘数据库，没有迁移，也没有 MySQL 连接。
- AI 默认拒绝调用，单项测试显式 mock。外部 socket connect 和
  create_connection 被禁止；仅允许 Windows 标准库 socketpair 内部连接，
  供 asyncio 自唤醒使用。HTTP 请求通过 TestClient 的进程内 ASGI transport。
- 模块替换仅适用于独立测试进程，不支持和其他应用测试混用或并行线程运行。
- SQLite 不能证明 MySQL JSON、DDL、连接池、并发或历史业务数据兼容性。
  不代表真实 AI、完整浏览器流程或生产环境启动已经验证。

## 现有测试风险（未运行）

| 文件 | 副作用 | 本阶段处理 |
| --- | --- | --- |
| `../test_dataset_status.py` | 真实库插入、更新；按固定三个文件名删除关联分析和数据集，运行前后均清理 | 未确认专用测试库，跳过 |
| `../test_db.py` | 导入即连接配置数据库执行 SELECT 1；失败被捕获并打印，退出码不可靠 | 无需真实服务，跳过 |
| `../test_ai.py` | 导入即真实 DeepSeek 调用，可能产生费用并发送示例分析 | 严格跳过 |

## 依赖核对

第四阶段已在后端 requirements 补齐必要运行依赖 `SQLAlchemy==2.0.52`
和 `PyMySQL==1.2.0`，沿用文件已有的精确版本声明方式，并将 UTF-16LE
转为 UTF-8 以便文本工具读取。不安装或升级当前虚拟环境，不修改其他约束。
根目录 requirements 保持不变，也不是完整后端依赖清单。
干净环境在 backend 目录执行：

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

以上命令仅供没有现有 .venv 的新 checkout/干净目录使用；本阶段未执行。
现有后端的 FastAPI、Pandas、OpenAI、dotenv、multipart、uvicorn 依赖
已列入 backend requirements。当前 TestClient 在已安装的 httpx2 环境中可用。

## 9 个显式接口契约

FastAPI 默认文档路由不计入下面 9 个业务/基础路由。

数据集字段 D：`id, filename, row_count, column_count, uploaded_at, status,
error_message, updated_at`。

分析记录字段 A：`id, dataset_id, analysis, insights, ai_insight, created_at`。

| 方法、路径 | 输入 | 成功响应 | 错误与关键语义 |
| --- | --- | --- | --- |
| GET `/` | 无 | 200，`{"message":"Welcome to DataInsightAI"}` | 不访问数据库/AI |
| GET `/api/health` | 无 | 200，`{"status":"ok","project":"DataInsightAI"}` | 不是数据库/AI 连通性检查 |
| GET `/api/data/datasets` | 无 | 200，D 对象数组 | uploaded_at 倒序；空库 `[]`；不是分页对象 |
| GET `/api/data/datasets/{dataset_id}` | 整数路径参数 | 200，D | 不存在 404 `数据集不存在`；非整数 422 |
| GET `/api/data/datasets/{dataset_id}/analysis` | 整数路径参数 | 200，A | created_at 倒序取第一条；无记录 404 `该数据集暂无分析结果`；非整数 422 |
| POST `/api/data/analyze` | multipart 必填 `file` | 200，`filename, analysis, insights, ai_insight, dataset_id, status` | 同一请求完成，status 为 completed；不是后台任务 202 |
| POST `/api/data/ai-insight` | multipart 必填 `file` | 200，`filename, ai_insight` | 不创建数据集/分析记录 |
| GET `/api/data/analysis/count` | 无 | 200，`{"count":整数}` | 统计分析记录数，不是 completed 数据集数 |
| GET `/api/data/quality` | 无 | 200，`{"quality_score":数值}` | 所有分析记录有效分数平均值，round(..., 1)；无有效分数为 0；不是仅最新分析 |

所有 HTTPException 返回 `{"detail":...}`。两项上传接口缺少 `file` 返回 422。
默认未处理异常返回 500，不能假设所有 500 都是 JSON detail。
时间字段保持 FastAPI 当前序列化为字符串的行为，无额外时区转换。

### CSV 校验基线

- 文件名缺失：400 `未提供文件`（服务级覆盖；HTTP 缺少 file 是 422）。
- 扩展名不为 .csv：400 `只支持 CSV 文件`；大小写不敏感，不校验 MIME。
- 大于 `20 * 1024 * 1024` 字节：413 `上传的 CSV 文件不能超过 20MB`。
- 恰好 20MiB 允许继续解析；大小检测发生在全量 read 之后。
- 空字节：400 `上传的 CSV 文件为空`。
- 非 UTF-8：400 `CSV 文件编码不是 UTF-8`。
- Pandas EmptyDataError：400 `CSV 文件没有有效数据`。
- Pandas ParserError：400 `CSV 文件格式错误，无法解析`。
- 仅表头目前允许，分析返回零行，不在重构时擅自拒绝。
- 实际 20MiB 边界在服务级测试；HTTP 413 用临时缩小常量减少 multipart 临时资源。

### 分析结构与任务状态

`analysis` 字段：`rows, columns, column_names, data_types, missing_values,
missing_rate, duplicate_rows, outliers, quality_score, unique_values,
numeric_summary, preview`。

numeric_summary 每列字段：`sum, mean, min, max, std`。
outliers 数值样本少于 4 个时只有 `count, values`，否则还包含
`lower_bound, upper_bound`。preview 最多 5 行，缺失项为 null。

`insights` 字段：`summary, quality, warnings, recommendations`。
AI 文本全部 mock，不固定真实 AI 文案。

状态流程：校验成功 → pending 短事务提交/会话关闭 → 统计/规则/AI →
分析结果和 completed 同一短事务提交。

- CSV 校验失败不创建任务，不调用 AI。
- pending 在 AI mock 回调时可被独立会话读取；旧会话已关闭。
- 分析/AI 失败：500 `数据分析失败，请稍后重新上传文件`；独立事务写 failed
  和同样 error_message，不产生分析记录。
- 创建任务失败：500 `数据分析任务创建失败，请稍后重试`。
- 最终提交失败：rollback，之后独立写 failed，不残留分析记录。
- failed 标记自身提交失败：rollback 并记录日志，仍返回分析失败 500；
  pending 可能保留。此测试记录已有行为，不表示该行为理想。
- AI-only 异常：500 `AI 洞察生成过程中发生错误：{异常文本}`。
- 各请求内生产会话的 close 调用也有断言。

### 已有问题与未覆盖项

不修复、不擅自改变 API 的已知问题：safe_float 不处理 infinity；
零列 DataFrame 的 duplicate_rows 未赋值；非法历史 quality_score 导致 500；
前端 unique_counts 与后端 unique_values 错配；进程中断可能遗留 pending。
其中非法质量分数的现有 500 已纳入行为测试，其他缺陷未纳入修复验收。

未执行：旧三项测试、真实 MySQL 集成、数据库迁移、真实 DeepSeek、
生产 .env/连接初始化、浏览器联调、干净环境依赖重装、并发/性能测试、
refresh 失败后遗留 pending 场景。
