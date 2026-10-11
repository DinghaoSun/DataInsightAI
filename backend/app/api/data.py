import logging

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services import dataset_service
from app.services.csv_loader import read_csv_file


router = APIRouter(prefix="/api/data")
logger = logging.getLogger("app.main")


@router.get("/datasets")
def get_datasets():
    datasets = dataset_service.list_datasets()
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


@router.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: int):
    dataset = dataset_service.get_dataset(dataset_id)
    if dataset is None:
        raise HTTPException(status_code=404, detail="数据集不存在")
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


@router.get("/datasets/{dataset_id}/analysis")
def get_dataset_analysis(dataset_id: int):
    analysis_record = dataset_service.get_latest_analysis(dataset_id)
    if analysis_record is None:
        raise HTTPException(status_code=404, detail="该数据集暂无分析结果")
    return {
        "id": analysis_record.id,
        "dataset_id": analysis_record.dataset_id,
        "analysis": analysis_record.analysis,
        "insights": analysis_record.insights,
        "ai_insight": analysis_record.ai_insight,
        "created_at": analysis_record.created_at,
    }


@router.post("/analyze")
async def analyze_data(file: UploadFile = File(...)):
    try:
        df = await read_csv_file(file)
        dataset_id = dataset_service.create_pending_dataset(file.filename, df)
        try:
            result, insights, ai_insight = dataset_service.analyze_dataset(dataset_id, df)
        except dataset_service.DatasetAnalysisError:
            raise HTTPException(
                status_code=500,
                detail="数据分析失败，请稍后重新上传文件",
            )
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


@router.post("/ai-insight")
async def ai_insight(file: UploadFile = File(...)):
    try:
        df = await read_csv_file(file)
        insight = dataset_service.generate_csv_ai_insight(df)
        return {"filename": file.filename, "ai_insight": insight}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI 洞察生成过程中发生错误：{str(e)}",
        )


@router.get("/analysis/count")
def get_analysis_count():
    return {"count": dataset_service.count_analyses()}


@router.get("/quality")
def get_data_quality():
    return {"quality_score": dataset_service.average_quality_score()}
