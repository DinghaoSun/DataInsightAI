from fastapi import FastAPI, File, HTTPException, UploadFile

from app.services.data_analyzer import analyze_dataframe
from app.services.insight_generator import generate_insights
from app.services.ai_service import generate_ai_insight
from app.services.csv_loader import read_csv_file


app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome to DataInsightAI"}


@app.get("/api/health")
def health_check():
    return {"status": "ok", "project": "DataInsightAI"}


@app.post("/api/data/analyze")
async def analyze_data(file: UploadFile = File(...)):
    try:
        # 1. 读取并校验 CSV 文件
        df = await read_csv_file(file)

        # 2. 执行数据分析
        result = analyze_dataframe(df)

        # 3. 生成规则型洞察
        insights = generate_insights(result)

        # 4. 生成 AI 洞察
        ai_insight = generate_ai_insight(result)

        # 5. 返回完整分析结果
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