from io import StringIO

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile

from app.services.data_analyzer import analyze_dataframe

from app.services.insight_generator import generate_insights

from app.services.ai_service import generate_ai_insight


app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome to DataInsightAI"}


@app.get("/api/health")
def health_check():
    return {"status": "ok", "project": "DataInsightAI"}


@app.post("/api/data/analyze")
async def analyze_data(file: UploadFile = File(...)):
    # 1. 检查文件名
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="未提供文件",
        )

    # 2. 检查文件类型
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="只支持 CSV 文件",
        )

    try:
        # 3. 读取文件
        content = await file.read()

        # 4. 检查文件是否为空
        if not content:
            raise HTTPException(
                status_code=400,
                detail="上传的 CSV 文件为空",
            )

        # 5. 使用 Pandas 读取 CSV
        df = pd.read_csv(
            StringIO(content.decode("utf-8"))
        )

        # 6. 执行数据分析
        result = analyze_dataframe(df)

        # 7. 生成规则型洞察
        insights = generate_insights(result)

        # 8. 生成 AI 洞察
        ai_insight = generate_ai_insight(result)

        # 9. 返回完整分析结果
        return {
            "filename": file.filename,
            "analysis": result,
            "insights": insights,
            "ai_insight": ai_insight,
        }

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="CSV 文件编码不是 UTF-8",
        )

    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=400,
            detail="CSV 文件没有有效数据",
        )

    except pd.errors.ParserError:
        raise HTTPException(
            status_code=400,
            detail="CSV 文件格式错误，无法解析",
        )

@app.post("/api/data/ai-insight")
async def ai_insight(file: UploadFile = File(...)):
    # 1. 检查文件名
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="未提供文件",
        )

    # 2. 检查文件类型
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="只支持 CSV 文件",
        )

    try:
        # 3. 读取文件
        content = await file.read()

        # 4. 检查文件是否为空
        if not content:
            raise HTTPException(
                status_code=400,
                detail="上传的 CSV 文件为空",
            )

        # 5. 读取 CSV
        df = pd.read_csv(
            StringIO(content.decode("utf-8"))
        )

        # 6. 执行数据分析
        analysis = analyze_dataframe(df)

        # 7. 生成 AI 洞察
        insight = generate_ai_insight(analysis)

        # 8. 返回结果
        return {
            "filename": file.filename,
            "ai_insight": insight,
        }

    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="CSV 文件编码不是 UTF-8",
        )

    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=400,
            detail="CSV 文件没有有效数据",
        )

    except pd.errors.ParserError:
        raise HTTPException(
            status_code=400,
            detail="CSV 文件格式错误，无法解析",
        )