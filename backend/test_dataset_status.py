from unittest.mock import patch

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models.dataset import Dataset
from app.models.dataset_analysis import DatasetAnalysis


SUCCESS_FILENAME = "day15_status_success.csv"
FAILURE_FILENAME = "day15_status_failure.csv"
PENDING_FILENAME = "day15_status_pending.csv"
CSV_CONTENT = b"name,sales\nA,100\nB,200\nC,300\nD,400\n"


def cleanup_test_records() -> None:
    db = SessionLocal()

    try:
        datasets = (
            db.query(Dataset)
            .filter(
                Dataset.filename.in_(
                    [
                        SUCCESS_FILENAME,
                        FAILURE_FILENAME,
                        PENDING_FILENAME,
                    ]
                )
            )
            .all()
        )
        dataset_ids = [dataset.id for dataset in datasets]

        if dataset_ids:
            (
                db.query(DatasetAnalysis)
                .filter(DatasetAnalysis.dataset_id.in_(dataset_ids))
                .delete(synchronize_session=False)
            )
            (
                db.query(Dataset)
                .filter(Dataset.id.in_(dataset_ids))
                .delete(synchronize_session=False)
            )
            db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def run_status_flow_test() -> None:
    client = TestClient(app)
    cleanup_test_records()

    try:
        db = SessionLocal()

        try:
            pending_dataset = Dataset(
                filename=PENDING_FILENAME,
                row_count=4,
                column_count=2,
                status="pending",
            )
            db.add(pending_dataset)
            db.commit()
            db.refresh(pending_dataset)
            pending_id = pending_dataset.id

        finally:
            db.close()

        pending_detail = client.get(
            f"/api/data/datasets/{pending_id}"
        )
        assert pending_detail.status_code == 200
        assert pending_detail.json()["status"] == "pending"

        with patch(
            "app.main.generate_ai_insight",
            return_value="测试 AI 洞察",
        ):
            success_response = client.post(
                "/api/data/analyze",
                files={
                    "file": (
                        SUCCESS_FILENAME,
                        CSV_CONTENT,
                        "text/csv",
                    )
                },
            )

        assert success_response.status_code == 200
        success_body = success_response.json()
        success_id = success_body["dataset_id"]
        assert success_body["status"] == "completed"

        success_detail = client.get(
            f"/api/data/datasets/{success_id}"
        )
        assert success_detail.status_code == 200
        assert success_detail.json()["status"] == "completed"
        assert success_detail.json()["error_message"] is None

        success_analysis = client.get(
            f"/api/data/datasets/{success_id}/analysis"
        )
        assert success_analysis.status_code == 200

        with patch(
            "app.main.generate_ai_insight",
            side_effect=RuntimeError("模拟 DeepSeek 服务失败"),
        ):
            failure_response = client.post(
                "/api/data/analyze",
                files={
                    "file": (
                        FAILURE_FILENAME,
                        CSV_CONTENT,
                        "text/csv",
                    )
                },
            )

        assert failure_response.status_code == 500

        db = SessionLocal()

        try:
            failed_dataset = (
                db.query(Dataset)
                .filter(Dataset.filename == FAILURE_FILENAME)
                .one()
            )
            assert failed_dataset.status == "failed"
            assert failed_dataset.error_message
            failed_analysis_count = (
                db.query(DatasetAnalysis)
                .filter(DatasetAnalysis.dataset_id == failed_dataset.id)
                .count()
            )
            assert failed_analysis_count == 0
            failure_id = failed_dataset.id

        finally:
            db.close()

        list_response = client.get("/api/data/datasets")
        assert list_response.status_code == 200
        list_item = next(
            item
            for item in list_response.json()
            if item["id"] == failure_id
        )
        assert {
            "status",
            "error_message",
            "updated_at",
        }.issubset(list_item)

        failure_detail = client.get(
            f"/api/data/datasets/{failure_id}"
        )
        assert failure_detail.status_code == 200
        assert failure_detail.json()["status"] == "failed"

        print("completed 流程验证通过")
        print("failed 流程验证通过")
        print("pending 状态字段验证通过")
        print("列表与详情状态字段验证通过")

    finally:
        cleanup_test_records()


if __name__ == "__main__":
    run_status_flow_test()
