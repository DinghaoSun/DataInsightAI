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

# Day 9 开发日志

## 今日目标

完成 DataInsightAI 前端基础搭建，并实现 Vue Dashboard 与后端 FastAPI 接口的数据联动。

## 今日完成内容

### 1. 搭建 Vue 前端项目

- 使用 Vite 创建 frontend 前端项目
- 选择 Vue 框架
- 使用 JavaScript 作为开发语言
- 成功启动 Vite 开发服务器
- 前端运行地址：http://localhost:5173

### 2. 引入 Axios

- 安装 Axios
- 创建前端 API 服务层
- 为 Vue 前端调用 FastAPI 后端接口做好基础准备

### 3. Dashboard 接入真实数据

将原本写死的 Dashboard 数据逐步替换为后端真实数据。

目前 Dashboard 已实现：

- 数据集数量动态获取
- 数据记录数量动态获取
- 分析次数动态获取
- 数据质量动态获取
- 最近数据集列表动态获取

### 4. 新增数据质量接口

后端新增：

`GET /api/data/quality`

该接口从 `DatasetAnalysis` 分析记录中读取真实的数据质量评分，并计算平均质量分。

当前接口返回：

```json
{
  "quality_score": 89.0
}

# DataInsightAI Day 10 开发日报

## 一、今日完成

### 1. 完成前端路由系统
- 引入并配置 Vue Router。
- 完成 Dashboard、数据集列表、数据集详情三个页面的路由配置。
- 实现页面之间的正常跳转。

### 2. 完成数据集列表页
- 新增 `Datasets.vue`。
- 接入后端 `/api/data/datasets` 接口。
- 展示数据集文件名、数据量、字段数、上传时间和分析状态。
- 实现点击数据集进入对应详情页。
- 增加数据加载和异常状态处理。

### 3. 完成数据集详情页
- 新增 `DatasetDetail.vue`。
- 接入 `/api/data/datasets/{dataset_id}` 接口。
- 展示数据集基本信息，包括数据量、字段数、上传时间和分析状态。
- 接入 `/api/data/datasets/{dataset_id}/analysis` 接口。
- 实现历史分析结果的前端展示。

### 4. 完成 AI 数据洞察展示
- 将数据库中保存的规则型分析结果展示到数据集详情页。
- 将 DeepSeek AI 生成的分析结果展示到 AI 数据洞察区域。
- 对 AI 分析内容进行了页面样式优化，使其更加符合数据分析平台的视觉效果。

### 5. 优化前端全局样式
- 清理 Vite 默认的全局 CSS。
- 解决 `#app` 宽度限制、页面整体居中以及文本布局异常等问题。
- 建立 DataInsightAI 自己的基础全局样式。

### 6. 完成 Git 提交
- 完成 Day 10 相关代码的 Git 提交。
- Commit：
  `feat: complete dataset list and detail pages`
- Commit ID：
  `1e12a61`

## 二、今日项目流程

目前 DataInsightAI 已实现：

CSV 数据上传
→ Pandas 数据分析
→ 规则型数据洞察
→ DeepSeek AI 洞察
→ MySQL 数据持久化
→ Dashboard 数据展示
→ 数据集列表
→ 数据集详情
→ 历史分析结果展示

## 三、今日收获

- 熟悉了 Vue Router 的基本使用和页面路由组织方式。
- 进一步理解了 Vue 前端如何通过 Axios 调用 FastAPI 后端接口。
- 完成了前端页面与 MySQL 持久化数据之间的完整联动。
- 对前后端分离项目的整体结构有了更加清晰的认识。
- 开始将 DataInsightAI 从后端功能型项目向完整的数据分析 Web 应用进行产品化。

## 四、明日计划

- 继续完善数据集详情页。
- 优化数据分析结果的可视化展示。
- 进一步提升 AI 洞察模块的产品化效果。
- 开始考虑数据分析图表、字段统计等更加直观的数据展示方式。


# DataInsightAI Day 11 日报

## 一、今日目标

完成 DataInsightAI 前端页面统一与数据集详情页优化，进一步完善数据可视化和 AI 洞察展示效果。

---

## 二、今日完成内容

### 1. 统一前端 Sidebar / Layout

- 完成前端整体 Layout 结构调整。
- 将 Sidebar 独立为公共组件。
- 使用 `AppLayout.vue` 统一管理页面布局。
- 通过 `router-view` 实现不同页面的内容切换。
- 优化页面整体结构，使 Dashboard、数据集页面和详情页保持统一的视觉布局。

### 2. 修复页面导航

- 完善 Vue Router 路由配置。
- 完成数据总览、数据集列表、数据集详情之间的页面跳转。
- 修复进入数据集页面后无法返回数据总览的问题。
- 优化 Sidebar 当前页面状态显示。
- 完成主要页面之间的正常导航。

### 3. 优化数据集详情页

- 优化数据集详情页的信息卡片展示。
- 增加数据集基本信息、数据质量等内容。
- 优化缺失值、字段信息等数据的展示方式。
- 完善详情页整体视觉效果，提高页面信息的可读性。

### 4. 接入第一个 ECharts 数据图表

- 在数据集详情页中接入 ECharts。
- 基于数据分析结果生成缺失值统计图表。
- 将后端返回的 `missing_values` 数据转换为图表数据。
- 实现数据分析结果的可视化展示。
- 初步完成 DataInsightAI 的数据可视化能力。

### 5. AI 洞察 Markdown 产品化

- 优化 AI 洞察结果的前端展示方式。
- 对 AI 返回的 Markdown 文本进行前端解析和格式处理。
- 对标题、编号列表、项目符号和普通文本进行分类展示。
- 将 AI 洞察从普通文本升级为更接近 AI 分析报告的产品化展示形式。
- 优化 AI 洞察区域的视觉层次和阅读体验。

### 6. 优化「分析摘要」

- 修复数据集详情页中「分析摘要」显示“暂无分析摘要”的问题。
- 根据当前数据集的真实分析结果动态生成分析摘要。
- 摘要中加入：
  - 数据记录数量
  - 字段数量
  - 数据质量评分
  - 缺失字段数量
  - 数值字段统计信息
- 增加数据集概览标签，使摘要信息更加直观。

### 7. 整理前端项目目录

- 检查前端项目目录结构。
- 删除之前遗留的多余 `frontend/frontend` 文件夹。
- 保留当前实际使用的 `frontend/src`、`package.json`、`node_modules` 等项目文件。
- 清理后重新启动并验证前端功能正常。

### 8. 完成测试与 Git Commit

- 完成数据总览页面测试。
- 完成数据集列表页面测试。
- 完成数据集详情页面测试。
- 完成详情页返回数据集页面测试。
- 完成 Sidebar 页面导航测试。
- 完成 ECharts 图表展示测试。
- 完成 AI 智能洞察展示测试。
- 完成分析摘要展示测试。
- 确认前端项目整理后运行正常。
- 完成本地 Git Commit。

Commit 信息：

`feat: optimize dataset detail page and AI insights`

---

## 三、今日技术收获

### 前端

- Vue 3 组件化开发
- Vue Router 路由管理
- 公共 Layout 设计
- Sidebar 公共组件复用
- Vue `computed` 数据计算
- Vue `ref` 状态管理
- Axios 前后端数据请求
- ECharts 数据可视化
- Markdown 文本前端产品化展示

### 项目工程

- 前端目录结构整理
- Git 工作流
- `git add`
- `git commit`
- 项目功能测试与回归测试

---

## 四、今日项目进展

DataInsightAI 已逐渐从基础的后端数据分析接口，发展为具备完整前端交互的数据分析应用。

当前已经实现：

CSV 数据上传
→ Pandas 数据分析
→ 数据质量分析
→ 规则型数据洞察
→ DeepSeek AI 智能洞察
→ MySQL 数据持久化
→ Vue 前端展示
→ 数据集管理
→ 数据集详情
→ ECharts 数据可视化
→ AI 分析报告展示

项目整体功能完整度和可展示性进一步提升。

---

## 五、Git 状态

今日已完成本地 Git Commit。

Commit：

`feat: optimize dataset detail page and AI insights`

GitHub 远程仓库连接暂未处理，不影响今日项目开发与本地版本管理。

---

## 六、今日总结

Day 11 主要围绕 DataInsightAI 前端体验和产品化展示进行完善。

今天完成了统一 Layout、页面导航修复、详情页信息卡片优化、ECharts 图表接入、AI 洞察产品化以及分析摘要优化，同时清理了项目中遗留的多余前端目录。

经过测试，目前前端主要页面和核心功能均可以正常运行。

DataInsightAI 的整体形态已经越来越接近一个完整的数据分析产品，而不仅仅是简单的后端接口项目。

---

## Day 11 完成情况

- [x] 统一 Sidebar / Layout
- [x] 修复所有页面导航
- [x] 优化详情页信息卡片
- [x] 开始第一个数据图表
- [x] AI 洞察 Markdown 产品化
- [x] 优化分析摘要
- [x] 整理前端项目目录
- [x] 测试
- [x] Git Commit

**Day 11：完成！**


## Day 12 - 2026-09-20

### 今日完成

#### 1. 完善数据集详情页
- 进一步优化数据集详情页整体信息结构
- 完善数据集基本信息、核心指标、数据质量和分析摘要展示
- 增加「字段概览」模块
- 展示字段名称、数据类型、缺失值等信息
- 优化详情页整体布局，使页面更加接近正式数据分析产品

#### 2. 增加第二个数据可视化图表
- 基于后端真实 `numeric_summary` 分析结果增加 ECharts 图表
- 新增「数值字段均值对比」图表
- 对不同数值字段的平均值进行可视化展示
- 与原有「字段缺失值统计」图表形成互补

#### 3. 优化数据分析结果展示
- 将 `numeric_summary` 等原始分析结果进行前端产品化展示
- 将数值字段的平均值、最大值、最小值、总和、标准差等信息以卡片形式展示
- 减少原始 JSON 数据堆积，提高分析结果的可读性

#### 4. 优化数据集详情页交互与 UI
- 优化页面各模块之间的间距和层级
- 统一卡片、标题、标签等视觉样式
- 检查数据集详情页加载、跳转及刷新情况
- 保持整体简洁、现代化的数据分析产品风格

#### 5. 完成前端功能测试
- 测试 Dashboard 页面
- 测试数据集列表页面
- 测试数据集详情页面
- 测试字段缺失值统计图
- 测试数值字段均值对比图
- 测试字段概览
- 测试数值统计
- 测试数据洞察
- 测试 AI 智能洞察
- 测试页面跳转与浏览器刷新

测试结果：功能正常，无明显问题。

#### 6. 完成 Git 提交与 GitHub 推送
- 完成 Git Commit
- Commit 信息：
  `feat: complete Day 12 dataset detail analysis UI`
- 成功推送至 GitHub `master` 分支

### 技术收获

- 进一步熟悉 Vue 单文件组件开发
- 掌握 ECharts 在 Vue 页面中的数据可视化应用
- 加深对后端分析结果与前端可视化数据绑定的理解
- 进一步理解数据分析产品的信息层级与 UI 设计
- 熟悉 Git 本地仓库与 GitHub 远程仓库的关联及 Push 流程

### 今日成果

DataInsightAI 数据集详情页进一步完善，实现：

**数据质量 → 字段分析 → 数值统计 → 可视化 → 数据洞察 → AI 智能洞察**

的完整数据分析结果展示流程。

### Day 12 状态

**✅ 已完成**

# Day 13 —— 数据上传闭环

## 今日完成

### 1. 完成 CSV 数据上传功能

* 在数据集页面增加「上传数据」入口
* 增加上传数据弹窗
* 支持选择 CSV 文件
* 限制文件大小不超过 20MB
* 增加文件格式校验
* 增加上传过程中的 Loading 状态

### 2. 完成前后端上传联动

* 前端使用 FormData 上传 CSV 文件
* 调用后端 `/api/data/analyze` 接口
* 完成 CSV 文件上传、数据分析、规则洞察、AI 洞察和数据库保存

### 3. 优化上传体验

* 将 Axios 请求超时时间由 10 秒调整为 60 秒
* 解决 AI 分析耗时较长导致前端请求超时的问题
* 上传成功后自动刷新数据集列表
* 自动获取最新数据集并跳转到对应详情页

### 4. 完成完整产品闭环

用户操作流程：

CSV 文件
→ 上传
→ 后端分析
→ Pandas 数据分析
→ 规则洞察
→ DeepSeek AI 洞察
→ MySQL 保存
→ 数据集列表刷新
→ 自动进入详情页
→ 查看分析结果

### 5. 完成边界测试

* 正常 CSV 上传测试：通过
* 非 CSV 文件限制测试：通过
* 取消上传测试：通过
* 上传完成自动跳转详情页：通过

## 今日成果

Data


# DataInsightAI Day 14 开发日报

**日期：2026-09-22**

## 今日目标

1. 修复上传文件大小显示异常问题
2. 完整测试 CSV 上传组件
3. 验证上传流程及异常状态
4. 完成 Day 14 收尾

---

## 今日完成内容

### 1. 修复文件大小显示问题

解决上传弹窗中已选择文件大小始终显示 `0.00 MB` 的问题。

调整文件大小显示逻辑，通过 `selectedFile.size` 获取浏览器 File 对象的真实文件大小，并使用 `formatFileSize()` 进行格式化。

现在可以根据文件实际大小正常显示：

- B
- KB
- MB

文件名和文件大小能够正常展示。

---

### 2. 完成上传组件测试

对数据集上传功能进行了完整测试：

- CSV 文件选择正常
- 文件名显示正常
- 文件大小显示正常
- 上传 Loading 状态正常
- 上传成功状态正常
- 上传完成后数据集能够正常处理
- 数据集详情页面能够正常进入
- 页面刷新后功能正常

同时确认非 CSV 文件受到文件类型限制。

---

### 3. 20MB 文件测试说明

原计划使用约 20MB 的大型 CSV 文件进行测试。

由于该文件在本地直接打开时会造成明显卡顿，因此没有继续使用浏览器/编辑器直接打开该文件。

本次重点验证上传组件本身的文件读取、大小显示和上传流程，核心功能已经测试通过。

---

## 今日结果

Day 14 主要完成了数据集上传模块的遗留问题修复与稳定性验证。

目前上传组件运行正常，之前的 `0.00 MB` 文件大小显示问题已经解决。

---

## Git 提交

```text
fix: 修复上传文件大小显示问题并完善上传测试