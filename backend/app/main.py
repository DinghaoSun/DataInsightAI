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
                detail="数据集不存在"
            )

        return {
            "id": dataset.id,
            "filename": dataset.filename,
            "row_count": dataset.row_count,
            "column_count": dataset.column_count,
            "uploaded_at": dataset.uploaded_at,
        }

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


@app.post("/api/data/analyze")
async def analyze_data(file: UploadFile = File(...)):
    try:
        # 1. 读取并校验 CSV 文件
        df = await read_csv_file(file)

        # 2. 执行数据分析
        result = analyze_dataframe(df)

        # 3. 保存数据集信息到 MySQL
        db = SessionLocal()

        try:
            dataset = Dataset(
                filename=file.filename,
                row_count=len(df),
                column_count=len(df.columns),
            )

            db.add(dataset)
            db.commit()
            db.refresh(dataset)

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

        # 4. 生成规则型洞察
        insights = generate_insights(result)

        # 5. 生成 AI 洞察
        ai_insight = generate_ai_insight(result)

        # 6. 保存分析结果到 MySQL
        db = SessionLocal()

        try:
            analysis_record = DatasetAnalysis(
                dataset_id=dataset.id,
                analysis=result,
                insights=insights,
                ai_insight=ai_insight,
            )

            db.add(analysis_record)
            db.commit()
            db.refresh(analysis_record)

        except Exception:
            db.rollback()
            raise

        finally:
            db.close()

        # 7. 返回完整分析结果
        return {
            "filename": file.filename,
            "analysis": result,
            "insights": insights,
            "ai_insight": ai_insight,
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"数据分析过程中发生错误：{str(e)}",
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