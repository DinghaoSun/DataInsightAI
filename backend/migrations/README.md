# 数据库迁移

在 `backend` 目录执行：

```powershell
.venv\Scripts\python.exe migrations\20261004_add_dataset_status.py
```

脚本会为现有 `datasets` 表增加 `status`、`error_message` 和 `updated_at`。已有分析记录的数据集会标记为 `completed`；没有分析记录的历史数据集会标记为 `failed`，失败原因为“历史数据缺少分析结果”。脚本不会删除现有数据，也不会修改 `dataset_analysis` 表。
