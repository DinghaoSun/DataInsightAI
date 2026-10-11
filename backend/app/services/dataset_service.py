"""Dataset queries, analysis orchestration and short-lived transactions."""

import logging

import pandas as pd

from app.database import SessionLocal
from app.models.dataset import Dataset
from app.models.dataset_analysis import DatasetAnalysis
from app.services.data_analyzer import analyze_dataframe
from app.services.insight_generator import generate_insights
from app.services.ai_service import generate_ai_insight


# Keep the existing log category and messages.
logger = logging.getLogger("app.main")


class DatasetAnalysisError(RuntimeError):
    """Analysis failed and the original failed-state handling has completed."""


def list_datasets() -> list[Dataset]:
    db = SessionLocal()
    try:
        return db.query(Dataset).order_by(Dataset.uploaded_at.desc()).all()
    finally:
        db.close()


def get_dataset(dataset_id: int) -> Dataset | None:
    db = SessionLocal()
    try:
        return db.query(Dataset).filter(Dataset.id == dataset_id).first()
    finally:
        db.close()


def get_latest_analysis(dataset_id: int) -> DatasetAnalysis | None:
    db = SessionLocal()
    try:
        return (
            db.query(DatasetAnalysis)
            .filter(DatasetAnalysis.dataset_id == dataset_id)
            .order_by(DatasetAnalysis.created_at.desc())
            .first()
        )
    finally:
        db.close()


def count_analyses() -> int:
    db = SessionLocal()
    try:
        return db.query(DatasetAnalysis).count()
    finally:
        db.close()


def average_quality_score() -> float | int:
    db = SessionLocal()
    try:
        analysis_records = (
            db.query(DatasetAnalysis)
            .order_by(DatasetAnalysis.created_at.desc())
            .all()
        )
        if not analysis_records:
            return 0
        scores = []
        for record in analysis_records:
            quality_score = record.analysis.get("quality_score")
            if quality_score is not None:
                scores.append(float(quality_score))
        if not scores:
            return 0
        average_score = sum(scores) / len(scores)
        return round(average_score, 1)
    finally:
        db.close()


def mark_dataset_failed(dataset_id: int, error_message: str) -> None:
    db = SessionLocal()

    try:
        dataset = (
            db.query(Dataset)
            .filter(Dataset.id == dataset_id)
            .first()
        )

        if dataset is None:
            logger.error(
                "无法标记失败状态：Dataset %s 不存在",
                dataset_id,
            )
            return

        dataset.status = "failed"
        dataset.error_message = error_message
        db.commit()

    except Exception:
        db.rollback()
        logger.exception(
            "更新 Dataset %s 失败状态时发生错误",
            dataset_id,
        )

    finally:
        db.close()


def create_pending_dataset(filename: str, df: pd.DataFrame) -> int:
    # 创建 pending 后立即释放会话；分析和 AI 调用不在此事务内。
    db = SessionLocal()

    try:
        dataset = Dataset(
            filename=filename,
            row_count=len(df),
            column_count=len(df.columns),
            status="pending",
        )

        db.add(dataset)
        db.commit()
        db.refresh(dataset)
        dataset_id = dataset.id

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()

    return dataset_id


def analyze_dataset(dataset_id: int, df: pd.DataFrame) -> tuple[dict, dict, str]:
    try:
        # 3. 数据分析和外部 AI 调用期间不持有数据库连接
        result = analyze_dataframe(df)
        insights = generate_insights(result)
        ai_insight = generate_ai_insight(result)

        # 4. 分析结果和 completed 状态在同一短事务中提交
        db = SessionLocal()

        try:
            analysis_record = DatasetAnalysis(
                dataset_id=dataset_id,
                analysis=result,
                insights=insights,
                ai_insight=ai_insight,
            )

            dataset_to_update = (
                db.query(Dataset)
                .filter(Dataset.id == dataset_id)
                .first()
            )

            if dataset_to_update is None:
                raise RuntimeError("数据集记录不存在")

            db.add(analysis_record)
            dataset_to_update.status = "completed"
            dataset_to_update.error_message = None
            db.commit()

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

    except Exception:
        logger.exception(
            "Dataset %s 分析失败",
            dataset_id,
        )
        mark_dataset_failed(
            dataset_id,
            "数据分析失败，请稍后重新上传文件",
        )
        raise DatasetAnalysisError("数据分析失败，请稍后重新上传文件")

    return result, insights, ai_insight


def generate_csv_ai_insight(df: pd.DataFrame) -> str:
    analysis = analyze_dataframe(df)
    return generate_ai_insight(analysis)
