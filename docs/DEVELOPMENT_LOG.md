# DataInsightAI 开发日志

## 2026-09-06

### 今日完成

- 创建 DataInsightAI 项目
- 完成项目 PRD
- 配置 Python 3.14.3 开发环境
- 配置 VS Code
- 安装 Git
- 配置 Git 用户信息
- 初始化 Git 仓库
- 完成第一次 Git Commit
- 修正 README.md 项目结构
- 将项目设计文档整理到 docs 目录
### 今日遇到的问题

1. VS Code 终端最初进入了 WSL 环境
2. Git 安装后 PowerShell 无法识别 git 命令
3. README.md 最初被错误创建成文件夹
4. Git 第一次 Commit 时没有配置用户身份

### 问题解决

- 切换回 Windows PowerShell
- 重新配置 Git PATH
- 将 Word 设计文档移动到 docs 目录
- 创建正确的 README.md 文件
- 配置 Git user.name 和 user.email

### 今日收获

- 初步了解 Git 的基本工作流程
- 理解 git init、git add、git commit 的作用
- 熟悉 VS Code + PowerShell 的项目开发环境
- 初步建立项目版本管理意识

### 明日计划

- 搭建 FastAPI 后端基础结构
- 创建第一个 API
- 让 DataInsightAI 后端成功运行




## Day 2：FastAPI 后端基础环境搭建

### 今日完成内容

1. 创建后端应用目录 `backend/app/`
2. 创建 `__init__.py` 和 `main.py`
3. 创建 Python 虚拟环境 `.venv`
4. 激活 Python 虚拟环境
5. 安装 FastAPI 和 Uvicorn
6. 创建第一个 FastAPI 应用
7. 实现根路径接口：
   - `GET /`
   - 返回 `{"message": "Welcome to DataInsightAI"}`
8. 实现健康检查接口：
   - `GET /api/health`
   - 返回 `{"status": "ok", "project": "DataInsightAI"}`
9. 使用 Uvicorn 成功启动后端服务
10. 验证 FastAPI Swagger API 文档：
    - `GET /docs`
11. 生成并更新项目依赖文件 `requirements.txt`

### 今日验证结果

后端服务成功运行于：

`http://127.0.0.1:8000`

健康检查接口返回：

`{"status":"ok","project":"DataInsightAI"}`

Swagger API 文档：

`http://127.0.0.1:8000/docs`

### 今日状态

DataInsightAI 后端基础环境搭建完成，FastAPI 服务成功运行，基础 API 验证通过。

## Day 3：数据分析核心功能开发

### 今日完成

1. 完善 Pandas 数据分析服务 `data_analyzer.py`
2. 实现 CSV 数据基本信息分析：
   - 数据行数
   - 数据列数
   - 列名
   - 数据类型
   - 缺失值统计
   - 唯一值数量
3. 增加数值列统计功能：
   - 总和（sum）
   - 平均值（mean）
   - 最小值（min）
   - 最大值（max）
   - 标准差（std）
4. 增加数据预览功能，返回 CSV 前 5 行数据。
5. 处理 Pandas `NaN` 与 JSON 不兼容的问题，将缺失值转换为 `null`。
6. 完善 FastAPI CSV 文件上传与分析接口：
   - `POST /api/data/analyze`
7. 使用 Swagger UI 对接口进行测试，确认接口返回 HTTP 200，数据分析结果正常。

### 今日验证结果

测试文件：`data/test_sales.csv`

接口：

`POST /api/data/analyze`

测试结果：

- HTTP 状态码：200
- CSV 文件能够正常上传
- 数据分析结果能够正常返回
- 缺失值能够正确显示为 `null`
- 数据预览功能正常

### Day 3 总结

完成了 DataInsightAI 后端第一版数据分析核心能力，实现了从 CSV 文件上传、Pandas 数据处理到 FastAPI JSON 返回的完整流程，为后续前端页面开发和 AI 数据分析功能打下基础。
Day 4 ------ AI 洞察基础能力

日期：2026-09-09

一、今日目标

在已有 Pandas 数据分析能力的基础上，为 DataInsightAI
增加"数据洞察"层，使系统能够根据数据分析结果自动生成可读的数据结论、问题提示和处理建议，并为后续接入真实大语言模型做好架构准备。

二、今日完成内容

1. 创建 AI 洞察生成模块

在 backend/app/services/ 下创建：

insight_generator.py

将数据分析与洞察生成进行模块化分离，为后续扩展真实 AI 能力提供基础。

2. 实现规则型数据洞察

根据 data_analyzer.py 输出的分析结果，生成：

summary：数据规模概览

quality：数据质量评价

warnings：数据问题与异常提醒

recommendations：针对发现问题给出的处理建议

3. 接入 FastAPI

将洞察生成能力接入现有数据分析接口，使 CSV 上传后不仅能够返回 Pandas
分析结果，还能够返回自然语言形式的数据洞察。

4. 完成接口测试

使用此前的 test_outliers.csv 进行测试，确认系统能够识别 sales
字段中的异常值 9999，并生成相应的中文提示与处理建议。

5. 创建 AI 服务层

创建：

backend/app/services/ai_service.py

先使用规则/模拟方式完成 AI 服务层结构，为 Day 5
接入真实大语言模型保留统一的调用入口。

三、Day 4 成果

Day 4 完成后，DataInsightAI 的处理流程从：

CSV → Pandas 分析

扩展为：

CSV → Pandas 分析 → 数据洞察

系统已经具备基础的数据质量分析和自然语言洞察能力。

Day 5 ------ DeepSeek 大模型接入

日期：2026-09-09

一、今日目标

将 Day 4 的规则型 AI 洞察升级为真实大语言模型生成，使 DataInsightAI
能够调用 DeepSeek，根据实际数据分析结果动态生成数据洞察。

二、今日完成内容

1. 申请 DeepSeek API

完成 DeepSeek API Key 的申请，为真实大模型调用做好准备。

2. 配置环境变量

在：

backend/.env

中配置 DeepSeek API Key 和模型名称。

API Key 不写入 Python 源代码。

3. 加强 API Key 安全

检查并完善 .gitignore，确保：

.env

.venv/

__pycache__/

*.pyc

等敏感或无须提交的内容不会进入 Git 仓库。

4. 安装相关依赖

安装：

openai

python-dotenv

使用 Python 环境变量读取 DeepSeek API Key。

5. 改造 ai_service.py

将原来的规则型模拟 AI 服务升级为真实的大模型服务。

主要完成：

加载 .env

读取 DEEPSEEK_API_KEY

配置 DeepSeek API

使用 OpenAI SDK 兼容方式调用 DeepSeek

将 Pandas 分析结果转换为 JSON

构造系统提示词和用户提示词

要求模型使用中文生成数据分析洞察

6. 创建独立测试程序

创建：

backend/test_ai.py

使用一份模拟的结构化分析结果直接调用 generate_ai_insight()，用于排除
FastAPI 因素，单独验证 DeepSeek API。

7. 解决环境变量读取问题

第一次运行测试时出现：

Missing credentials

排查后发现 .env 文件虽然存在，但文件当时没有保存，文件大小为 0 字节。

保存 .env 后执行环境变量检查：

API Key loaded: True

随后 API 调用恢复正常。

8. DeepSeek 单独调用测试成功

运行：

python test_ai.py

成功获得 DeepSeek 生成的中文数据分析结果。

模型能够根据提供的数据分析结果识别：

数据规模较小

数据质量评分

sales 字段存在异常值

异常值可能影响统计结果

可以进一步核实和处理异常值

9. 完整 FastAPI 链路测试成功

重新启动 Uvicorn：

uvicorn app.main:app --reload

进入 Swagger：

/docs

测试：

POST /api/data/ai-insight

上传：

test_outliers.csv

最终接口返回：

HTTP 200 OK

并成功返回 DeepSeek 动态生成的 AI 洞察。

三、Day 5 成果

DataInsightAI 已经从固定规则生成文本升级为真正调用大语言模型：

CSV → Pandas → 结构化分析结果 → DeepSeek → AI 洞察 → FastAPI JSON

这意味着项目已经正式具备真实的大模型数据分析能力。

## Day 6 —— AI 洞察集成与代码重构

### 今日目标

1. 将 DeepSeek AI 洞察正式接入数据分析主流程
2. 对 CSV 文件读取与校验逻辑进行模块化重构
3. 完成两个数据分析接口的功能测试
4. 使用 Git 保存今日开发成果

### 今日完成内容

#### 1. AI 洞察接入主分析流程

将 DeepSeek AI 洞察功能正式接入：

`POST /api/data/analyze`

实现完整的数据分析流程：

CSV 文件
→ CSV 数据读取
→ Pandas 数据分析
→ 规则型洞察
→ DeepSeek AI 洞察
→ 返回完整分析结果

接口现在可以同时返回：

- `analysis`：数据分析结果
- `insights`：规则型数据洞察
- `ai_insight`：DeepSeek 生成的 AI 洞察

#### 2. 抽离 CSV 文件处理逻辑

新建：

`backend/app/services/csv_loader.py`

将原本位于 `main.py` 中的 CSV 文件处理逻辑进行抽离。

`csv_loader.py` 主要负责：

- 检查文件名
- 检查 CSV 文件类型
- 检查文件是否为空
- 读取 CSV 文件
- UTF-8 编码检查
- CSV 格式错误处理

通过模块化处理，使 `main.py` 的职责更加清晰。

#### 3. 优化 main.py

修改 `main.py`，通过：

`read_csv_file()`

调用 CSV 文件读取服务。

目前 `main.py` 主要负责：

- 定义 FastAPI 接口
- 调用数据分析服务
- 调用规则型洞察服务
- 调用 AI 洞察服务
- 返回 API 结果

进一步降低了不同功能之间的耦合。

#### 4. 完成功能测试

使用：

`test_outliers.csv`

分别测试：

- `POST /api/data/analyze`
- `POST /api/data/ai-insight`

两个接口均返回：

`HTTP 200 OK`

并成功生成 AI 洞察。

测试过程中，DeepSeek 正确识别出了 `sales` 字段中的异常值 `9999`，说明完整的 AI 数据分析流程运行正常。

#### 5. Git 版本控制

完成 Day 6-1 和 Day 6-2 的 Git 提交。

Day 6-2 提交信息：

`refactor: extract CSV loading logic`

并确认工作区干净。

### 今日项目成果

DataInsightAI 当前已经形成较完整的后端分析链路：

CSV
→ CSV Loader
→ Data Analyzer
→ Rule-based Insight
→ DeepSeek AI Insight
→ FastAPI API

同时完成了基础的服务模块拆分，项目代码结构进一步规范。

### 今日总结

今天主要完成了 DataInsightAI 的 AI 能力整合和代码结构优化。

相比之前，项目已经不再只是简单的 CSV 分析接口，而是形成了从数据读取、数据分析、规则洞察到 AI 洞察的完整流程。

通过今天的重构，也进一步理解了模块化设计和服务层拆分的基本思想。

### 明日计划

进入 Day 7，开始为 DataInsightAI 接入数据库，实现分析结果的持久化保存，并逐步为后续的历史分析记录功能做准备。

# DataInsightAI Day 7 日报

**日期：2026-09-11**

## 今日目标

完成 MySQL 数据持久化，并实现历史数据集与历史分析结果查询功能。

## 今日完成

### 1. 完成 MySQL 环境搭建

- 修复并重新安装 MySQL Server 8.0.41
- 启动 MySQL80 服务
- 使用 MySQL Workbench 成功连接数据库
- 创建 `datainsightai` 数据库

### 2. 完成 Python 数据库连接

- 安装并配置 SQLAlchemy、PyMySQL
- 在 `.env` 中配置数据库连接信息
- 创建 `database.py`
- 成功实现 Python → SQLAlchemy → MySQL 数据库连接
- 使用 `SELECT 1` 验证数据库连接成功

### 3. 建立数据集数据模型

- 创建 `Dataset` 模型
- 创建 `datasets` 数据表
- 保存数据集的：
  - ID
  - 文件名
  - 行数
  - 列数
  - 上传时间
- 实现 CSV 上传后自动保存数据集信息

### 4. 增加历史数据集查询功能

新增 API：

```text
GET /api/data/datasets
GET /api/data/datasets/{dataset_id}


# DataInsightAI Day 8 日报

## 今日完成

1. 完善并确认 DatasetAnalysis 数据模型
2. 建立 Dataset 与 DatasetAnalysis 的数据库关联
3. 更新数据库初始化逻辑，成功创建 dataset_analysis 表
4. 将数据分析结果保存到 MySQL
5. 将规则型洞察保存到 MySQL
6. 将 DeepSeek AI 洞察保存到 MySQL
7. 完成历史分析结果查询接口：
   GET /api/data/datasets/{dataset_id}/analysis
8. 使用 Swagger 对完整数据链路进行测试并验证成功

## 今日成果

DataInsightAI 已实现完整的数据分析持久化流程：

CSV 上传
→ 数据分析
→ 规则型洞察
→ AI 洞察
→ MySQL 持久化
→ 历史分析结果查询

分析结果不再只是临时返回，而是能够保存到数据库并通过 dataset_id 重新查询。

## 今日学习

- SQLAlchemy 外键关联
- 数据分析结果持久化
- 数据集与分析结果的关联设计
- FastAPI 历史数据查询接口
- API 完整链路测试

## Day 8 状态

✅ Day 8 完成