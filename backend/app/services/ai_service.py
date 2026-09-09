import os
import json

from dotenv import load_dotenv
from openai import OpenAI


# 加载 .env 文件
load_dotenv()

# 创建 DeepSeek 客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")


def generate_ai_insight(analysis: dict) -> str:
    """
    使用 DeepSeek 根据数据分析结果生成 AI 洞察。
    """

    analysis_text = json.dumps(
        analysis,
        ensure_ascii=False,
        indent=2
    )

    system_prompt = """
你是一名专业的数据分析助手。

你的任务是根据系统提供的数据分析结果，
为用户生成简洁、清晰、具有实际价值的数据洞察。

请重点关注：
1. 数据规模
2. 数据质量
3. 缺失值
4. 重复数据
5. 异常值
6. 数值字段的整体情况
7. 可以采取的数据处理建议

要求：
- 使用中文回答
- 不要编造数据
- 只能根据提供的分析结果进行判断
- 用大学生也容易理解的语言
- 先给出整体结论，再指出主要问题，最后给出建议
"""

    user_prompt = f"""
下面是 DataInsightAI 对 CSV 数据进行分析后得到的结果：

{analysis_text}

请根据这些结果生成一份数据分析洞察。
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        stream=False
    )

    return response.choices[0].message.content