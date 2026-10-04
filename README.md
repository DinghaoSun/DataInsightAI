# DataInsightAI

## 项目简介

DataInsightAI 是一个面向 CSV 数据的 AI 数据分析项目。用户可以上传数据文件，查看基础统计、数据质量、规则型洞察和 AI 洞察。

## 核心功能

- CSV 文件上传与解析
- 缺失值、重复值、异常值和数值字段统计
- 数据质量评分与规则型洞察
- DeepSeek AI 数据洞察
- 数据集与分析结果持久化
- 数据总览、数据集列表和数据集详情展示

## 技术栈

- 前端：Vue 3、Vite、Vue Router、Axios、ECharts
- 后端：FastAPI、Pandas、SQLAlchemy
- 数据库：MySQL
- AI：DeepSeek API

## 项目结构

- `frontend/`：Vue 前端应用
- `backend/`：FastAPI 后端应用
- `data/`：本地测试数据
- `docs/`：产品文档和开发日志

## 本地运行

分别安装前端和后端依赖，配置环境变量及 MySQL 数据库后，启动 FastAPI 后端和 Vite 前端。

## 环境变量

后端需要配置 MySQL 连接信息、DeepSeek API Key 和模型名称。具体变量以 `backend/app/database.py` 和 `backend/app/services/ai_service.py` 中读取的配置为准。

## 当前状态

项目当前已完成 CSV 上传、数据分析、AI 洞察、MySQL 持久化以及主要前端页面的基础闭环，仍处于开发完善阶段。
