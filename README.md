# DataInsightAI（DIAI）

## 项目简介

DataInsightAI 是面向 CSV 数据的个人全栈 AI 数据分析项目。上传文件后，可以查看基础统计、数据质量、规则型洞察与 DeepSeek AI 洞察，并通过 Vue 页面浏览持久化结果。

V1.0 以本地运行和演示为目标，核心闭环已在开发环境验证；不代表已经完成生产部署、并发与安全验收。

## 核心功能

- UTF-8 CSV 上传、格式检查、20MiB 大小限制及有效数据校验。
- 行列数、缺失值、重复行、异常值、每列非空唯一值数量和数值统计。
- 数据质量评分、规则型洞察及 DeepSeek AI 洞察。
- MySQL 保存数据集与分析结果，展示 pending / completed / failed 状态及错误信息。
- 数据总览、近七天上传趋势、数据集列表与详情、ECharts 可视化及 AI 文本展示。
- 总览质量面板展示平均分，不是质量分类分布。总览、数据集菜单可用；分析、洞察、设置暂未开放。

## 技术栈

- 前端：Vue 3、Vite、Vue Router、Axios、ECharts。
- 后端：FastAPI、Pandas、SQLAlchemy、Uvicorn。
- 数据库：MySQL、PyMySQL。
- AI：DeepSeek API，通过 OpenAI SDK 调用。

## 系统架构与处理流程

`app/main.py` 创建应用、配置 CORS、定义根接口和健康检查、注册路由。`app/api/data.py` 接收 HTTP 参数、组装响应及映射错误；`app/services/` 负责 CSV 校验、统计、规则洞察、AI、查询和事务编排；`app/models/` 定义数据库模型。

```text
Vue 上传 CSV → FastAPI 校验 → 创建 pending Dataset 并提交/关闭会话
  → Pandas 统计与规则洞察 → DeepSeek（不持有数据库会话）
  → 同一事务保存 DatasetAnalysis 并标记 completed → Vue 读取展示
```

校验失败返回 400 或 413，不创建 Dataset、不调用 AI。分析或 AI 失败返回 500，使用独立会话尝试写 failed 状态与安全错误信息。上传是同步请求，不是后台任务。统计及数据预览会发送给 DeepSeek，请勿上传未经许可的敏感数据；真实调用可能产生费用。

## 主要目录

```text
DataInsightAI/
├─ README.md
├─ requirements.txt                 根目录简化依赖，非完整后端清单
├─ backend/
│  ├─ requirements.txt              实际后端依赖
│  ├─ .env.example                  安全配置示例
│  ├─ init_db.py                    建表入口
│  ├─ app/
│  │  ├─ main.py
│  │  ├─ database.py
│  │  ├─ api/data.py                HTTP 路由
│  │  ├─ models/                    Dataset / DatasetAnalysis
│  │  └─ services/                  CSV、统计、洞察、AI、数据集编排
│  ├─ migrations/                  历史迁移及说明
│  ├─ tests/                       隔离基线测试
│  └─ test_*.py                    旧真实服务测试，有副作用
├─ frontend/
│  ├─ package.json / package-lock.json
│  ├─ vite.config.js
│  ├─ src/                         views、components、router、services、assets 等
│  ├─ tests/                       Node 内置测试
│  └─ public/
├─ data/                           小型示例 CSV
└─ docs/                           PRD、设计文档、开发日志
```

## 环境要求

当前开发环境：Python **3.14.3**、Node.js **24.16.0**、npm **11.13.0**、MySQL **8.0.41**。这些是已使用版本，**不代表最低兼容版本**；其他版本尚未完成兼容验收。当前 Vite 要求 Node `^20.19.0 || >=22.12.0`。

以下步骤适用于 Windows PowerShell，需要先安装运行时并启动 MySQL 服务。安装命令供新 checkout 使用，干净环境完整安装尚待独立验证。

## 后端安装与环境变量

从项目根目录执行；不要覆盖已有虚拟环境：

```powershell
cd backend
py -3.14 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

这里使用的是 **backend/requirements.txt**，不要误用根目录简化清单。依赖版本以该文件为准。

复制示例并编辑（已有 `.env` 时不覆盖）：

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
notepad .env
```

替换密码和 API Key 占位值。代码调用 `load_dotenv()`，已设置的进程环境变量默认优先于文件。请从 backend 目录启动。真实 `.env` 已被 Git 忽略，不能强制提交或公开密钥。

| 变量 | 代码默认值 | 说明 |
| --- | --- | --- |
| `DB_HOST` | `localhost` | MySQL 主机 |
| `DB_PORT` | `3306` | MySQL 端口 |
| `DB_USER` | `root` | 当前本地默认值，可使用自行授权的数据库用户 |
| `DB_PASSWORD` | 无 | 自行配置数据库密码 |
| `DB_NAME` | `datainsightai` | 必须与实际数据库一致 |
| `DEEPSEEK_API_KEY` | 无 | 用户自行取得并配置真实密钥 |
| `DEEPSEEK_MODEL` | `deepseek-v4-flash` | 当前代码默认模型，确认账号可用性 |

DeepSeek 地址固定为 `https://api.deepseek.com`。数据库使用 `mysql+pymysql` 与 `utf8mb4`；目前连接 URL 直接拼接，密码含 URL 特殊字符时可能导致解析问题，属于待处理限制。不要打印包含密码的连接串。

## MySQL 数据库准备

### 新数据库

先确认目标数据库不存在，不要覆盖业务库。进入 MySQL 客户端，交互输入密码：

```powershell
mysql -u root -p
```

仅在确认名称未被使用时执行 SQL；如已存在，采用“已有数据库”流程，不删除或重建：

```sql
CREATE DATABASE datainsightai CHARACTER SET utf8mb4;
EXIT;
```

配置 `.env` 后，在 backend 目录执行：

```powershell
.\.venv\Scripts\python.exe init_db.py
```

`init_db.py` 导入模型并调用 `Base.metadata.create_all()`，为目标库创建缺失的表；**不创建数据库、不自动升级已有表结构**。主要表为 `datasets` 和 `dataset_analysis`，分析结果与规则洞察存为 JSON。

### 已有数据库与历史迁移

先备份、确认目标库与权限，再检查表结构是否符合当前模型，尤其是 `datasets.status`、`error_message`、`updated_at`。结构匹配时无需重复迁移。

`migrations/20261004_add_dataset_status.py` 会增加缺失状态字段并回填历史状态；无分析记录的历史数据集可能被标记为 failed。该脚本执行 ALTER/UPDATE，**不是每次启动的必跑步骤**。先阅读 [迁移说明](backend/migrations/README.md) 与脚本，确认确实需要、有备份且范围可接受后再手动执行。不要未经检查运行全部迁移；`init_db.py` 不能代替历史迁移。

## 后端启动

完成依赖、配置与数据库准备后，在 backend 目录执行：

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

等价于激活虚拟环境后的 `uvicorn app.main:app --reload`。默认地址 `http://127.0.0.1:8000`，接口文档 `http://127.0.0.1:8000/docs`。

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/health
```

健康接口返回 `status: ok`，但不检查数据库或 AI 连通性。`--reload` 仅用于开发，不是生产启动方案。

## 前端安装与启动

另开 PowerShell，从项目根目录执行：

```powershell
cd frontend
npm ci
npm run dev -- --port 5173 --strictPort
```

已有 package-lock.json，优先使用 `npm ci` 复现锁定依赖；一般开发安装也可使用 `npm install`。浏览器访问 **http://localhost:5173**。

前端 API 地址硬编码为 `http://127.0.0.1:8000`，后端 CORS 仅允许 `http://localhost:5173`，不要随意换用 IP 或其他端口。生产域名与代理配置尚未完成。

```powershell
npm run build
```

产物位于 frontend/dist。构建成功不代表已部署；默认 `npm run preview` 端口也不在当前 CORS 允许范围内。

## 测试命令与已验证范围

在 backend 目录、新 Python 进程中执行：

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -p 'test_*_baseline.py' -v
```

当前 **32 项隔离基线测试通过**，覆盖 CSV 校验及 20MiB 边界、正常分析、唯一值数量、9 个接口、CORS、JSON 持久化、任务状态与事务提交/回滚/会话关闭。API 测试使用内存 SQLite、替换数据库/AI 导入并拦截网络，不连接真实 MySQL 或 DeepSeek；SQLite 不证明 MySQL 完整兼容。

在 frontend 目录执行：

```powershell
node --test tests/*.test.js
npm run build
```

当前 **6 项前端测试通过**，覆盖唯一值展示及质量面板状态，读取实际 computed 逻辑但不替代浏览器验收。构建已成功，仍有详情页资源包大于 500kB 的警告。

此前真实验证了 MySQL 8.0.41 连接、小型 CSV 的 DeepSeek 调用、结果保存及 Vue 详情展示；另在独立 mock AI 进程中验证真实库 failed 状态和异常文件拒绝。导航与质量面板使用模拟接口完成浏览器验证。这些是已有开发环境验证记录，并非本次文档更新中新运行的测试，不覆盖生产、并发或全部历史数据。

**不要盲目运行旧测试或全项目自动收集**：backend 根目录 `test_dataset_status.py` 会写入及清理配置数据库数据，`test_ai.py` 会真实调用 AI，`test_db.py` 导入即连接数据库。参见 [隔离测试说明](backend/tests/README.md)。其中部分 Day 17/18 历史说明尚待更新：当前仅表头/全缺失值 CSV 已拒绝，后端总数为 32 项。

## 已知限制与后续规划

- 当前为本地演示版本：认证、权限、生产密钥管理、部署、备份恢复及负载验收尚待完善，不应直接对外开放。
- 同步 AI 请求可能超时；进程中断或 failed 标记写入失败时可能遗留 pending。
- CSV 大小检查在全量读取后执行；有效数据按 Pandas 缺失值语义判断，不是完整业务字段校验。
- `unique_values` 是每列非空不同值数量，不是值列表；历史 JSON 未全面核验或迁移。
- 质量 API 无评分区间分布或有效评分样本数；无有效评分返回 0，无法与真实零分区分。
- 全空数值列在均值图中可能显示 0，而统计卡片显示 `--`；AI Markdown 为简化展示，分隔线等语法支持有限。
- 详情资源包较大；移动端、性能、其他运行时兼容、干净安装及生产启动仍待验证。
- 前端 API 地址与 CORS 固定，不能直接作为远程部署配置。

下一步优先同步文档与干净环境复现，再进行 V1.0 发布验收；数据展示边界、部署配置和性能优化分别作为独立任务。产品设计与开发过程见 docs/。
