import logging

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.database import SessionLocal
from app.models.dataset import Dataset
from app.models.dataset_analysis import DatasetAnalysis
from app.services.data_analyzer import analyze_dataframe
from app.services.insight_generator import generate_insights
from app.services.ai_service import generate_ai_insight
from app.services.csv_loader import read_csv_file


app = FastAPI()
logger = logging.getLogger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to DataInsightAI"}


@app.get("/api/health")
def health_check():
    return {"status": "ok", "project": "DataInsightAI"}


@app.get("/api/data/datasets")
def get_datasets():
    db = SessionLocal()

    try:
        datasets = (
            db.query(Dataset)
            .order_by(Dataset.uploaded_at.desc())
            .all()
        )

        return [
            {
                "id": dataset.id,
                "filename": dataset.filename,
                "row_count": dataset.row_count,
                "column_count": dataset.column_count,
                "uploaded_at": dataset.uploaded_at,
                "status": dataset.status,
                "error_message": dataset.error_message,
                "updated_at": dataset.updated_at,
            }
            for dataset in datasets
        ]

    finally:
        db.close()

@app.get("/api/data/datasets/{dataset_id}")
def get_dataset(dataset_id: int):
    db = SessionLocal()

    try:
        dataset = (
            db.query(Dataset)
            .filter(Dataset.id == dataset_id)
            .first()
        )

        if dataset is None:
            raise HTTPException(
                status_code=404,
                detail="数据集不存在",
            )

        return {
            "id": dataset.id,
            "filename": dataset.filename,
            "row_count": dataset.row_count,
            "column_count": dataset.column_count,
            "uploaded_at": dataset.uploaded_at,
            "status": dataset.status,
            "error_message": dataset.error_message,
            "updated_at": dataset.updated_at,
        }

    finally:
        db.close()

@app.get("/api/data/datasets/{dataset_id}/analysis")
def get_dataset_analysis(dataset_id: int):
    db = SessionLocal()

    try:
        analysis_record = (
            db.query(DatasetAnalysis)
            .filter(DatasetAnalysis.dataset_id == dataset_id)
            .order_by(DatasetAnalysis.created_at.desc())
            .first()
        )

        if analysis_record is None:
            raise HTTPException(
                status_code=404,
                detail="该数据集暂无分析结果",
            )

        return {
            "id": analysis_record.id,
            "dataset_id": analysis_record.dataset_id,
            "analysis": analysis_record.analysis,
            "insights": analysis_record.insights,
            "ai_insight": analysis_record.ai_insight,
            "created_at": analysis_record.created_at,
        }

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


@app.post("/api/data/analyze")
async def analyze_data(file: UploadFile = File(...)):
    dataset_id = None

    try:
        # 1. 读取并校验 CSV 文件
        df = await read_csv_file(file)

        # 2. 创建 pending Dataset，并立即释放数据库连接
        db = SessionLocal()

        try:
            dataset = Dataset(
                filename=file.filename,
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
            raise HTTPException(
                status_code=500,
                detail="数据分析失败，请稍后重新上传文件",
            )

        # 5. 保持原有返回字段，并追加任务标识和状态
        return {
            "filename": file.filename,
            "analysis": result,
            "insights": insights,
            "ai_insight": ai_insight,
            "dataset_id": dataset_id,
            "status": "completed",
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("创建 Dataset 分析任务失败")
        raise HTTPException(
            status_code=500,
            detail="数据分析任务创建失败，请稍后重试",
        )


@app.post("/api/data/ai-insight")
async def ai_insight(file: UploadFile = File(...)):
    try:
        # 1. 读取并校验 CSV 文件
        df = await read_csv_file(file)

        # 2. 执行数据分析
        analysis = analyze_dataframe(df)

        # 3. 生成 AI 洞察
        insight = generate_ai_insight(analysis)

        # 4. 返回 AI 洞察结果
        return {
            "filename": file.filename,
            "ai_insight": insight,
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI 洞察生成过程中发生错误：{str(e)}",
        )

@app.get("/api/data/analysis/count")
def get_analysis_count():
    db = SessionLocal()

    try:
        count = db.query(DatasetAnalysis).count()

        return {
            "count": count
        }

    finally:
        db.close()

@app.get("/api/data/quality")
def get_data_quality():
    db = SessionLocal()

    try:
        analysis_records = (
            db.query(DatasetAnalysis)
            .order_by(DatasetAnalysis.created_at.desc())
            .all()
        )

        if not analysis_records:
            return {
                "quality_score": 0
            }

        scores = []

        for record in analysis_records:
            quality_score = record.analysis.get("quality_score")

            if quality_score is not None:
                scores.append(float(quality_score))

        if not scores:
            return {
                "quality_score": 0
            }

        average_score = sum(scores) / len(scores)

        return {
            "quality_score": round(average_score, 1)
        }

    finally:
        db.close()
