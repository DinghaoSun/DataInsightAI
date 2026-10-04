r"""一次性迁移：为 datasets 表增加分析状态字段。

在 backend 目录执行：
    .venv\Scripts\python.exe migrations\20261004_add_dataset_status.py
"""

from pathlib import Path
import sys

from sqlalchemy import inspect, text


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.database import engine  # noqa: E402


def column_names() -> set[str]:
    return {
        column["name"]
        for column in inspect(engine).get_columns("datasets")
    }


def run_migration() -> None:
    existing_columns = column_names()
    status_added = "status" not in existing_columns

    with engine.begin() as connection:
        if status_added:
            connection.execute(
                text(
                    "ALTER TABLE datasets "
                    "ADD COLUMN status VARCHAR(20) NULL"
                )
            )

        if "error_message" not in existing_columns:
            connection.execute(
                text(
                    "ALTER TABLE datasets "
                    "ADD COLUMN error_message TEXT NULL"
                )
            )

        if "updated_at" not in existing_columns:
            connection.execute(
                text(
                    "ALTER TABLE datasets "
                    "ADD COLUMN updated_at DATETIME NULL"
                )
            )
            connection.execute(
                text(
                    "UPDATE datasets "
                    "SET updated_at = uploaded_at "
                    "WHERE updated_at IS NULL"
                )
            )
            connection.execute(
                text(
                    "ALTER TABLE datasets "
                    "MODIFY COLUMN updated_at DATETIME NOT NULL"
                )
            )

        if status_added:
            connection.execute(
                text(
                    "UPDATE datasets AS d "
                    "SET d.status = CASE "
                    "WHEN EXISTS ("
                    "SELECT 1 FROM dataset_analysis AS da "
                    "WHERE da.dataset_id = d.id"
                    ") THEN 'completed' ELSE 'failed' END, "
                    "d.error_message = CASE "
                    "WHEN EXISTS ("
                    "SELECT 1 FROM dataset_analysis AS da "
                    "WHERE da.dataset_id = d.id"
                    ") THEN NULL ELSE '历史数据缺少分析结果' END"
                )
            )
            connection.execute(
                text(
                    "ALTER TABLE datasets "
                    "MODIFY COLUMN status VARCHAR(20) "
                    "NOT NULL DEFAULT 'pending'"
                )
            )

    print("Dataset 状态字段迁移完成。")


if __name__ == "__main__":
    run_migration()
