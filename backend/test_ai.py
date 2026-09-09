from app.services.ai_service import generate_ai_insight


test_analysis = {
    "rows": 10,
    "columns": 3,
    "column_names": [
        "name",
        "sales",
        "age"
    ],
    "quality_score": 98,
    "missing_rate": {
        "name": 0,
        "sales": 0,
        "age": 0
    },
    "duplicate_rows": 0,
    "outliers": {
        "sales": {
            "count": 1,
            "values": [9999.0]
        }
    }
}


result = generate_ai_insight(test_analysis)

print("\n========== DeepSeek AI 洞察 ==========\n")
print(result)
print("\n======================================\n")