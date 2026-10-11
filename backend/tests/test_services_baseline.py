"""Offline characterization tests: no application/database/AI imports."""

import json
from io import BytesIO
import unittest

import pandas as pd
from fastapi import HTTPException, UploadFile

from app.services.csv_loader import MAX_FILE_SIZE, read_csv_file
from app.services.data_analyzer import analyze_dataframe, safe_float
from app.services.insight_generator import generate_insights


class CSVBaselineTests(unittest.IsolatedAsyncioTestCase):
    async def read(self, content, filename="sample.csv"):
        upload = UploadFile(file=BytesIO(content), filename=filename)
        try:
            return await read_csv_file(upload)
        finally:
            await upload.close()

    async def test_validation_errors(self):
        cases = [
            (b"a\n1\n", None, 400, "未提供文件"),
            (b"a\n1\n", "a.txt", 400, "只支持 CSV 文件"),
            (b"", "a.csv", 400, "上传的 CSV 文件为空"),
            (b"\xff", "a.csv", 400, "CSV 文件编码不是 UTF-8"),
            (b"\n\n", "a.csv", 400, "CSV 文件没有有效数据"),
            (b'a,b\n"unterminated', "a.csv", 400, "CSV 文件格式错误，无法解析"),
        ]
        for content, filename, status, detail in cases:
            with self.subTest(filename=filename, detail=detail):
                with self.assertRaises(HTTPException) as caught:
                    await self.read(content, filename)
                self.assertEqual((caught.exception.status_code, caught.exception.detail),
                                 (status, detail))

    async def test_case_insensitive_extension_and_utf8(self):
        frame = await self.read("名字,销售额\n甲,100\n".encode(), "DATA.CSV")
        self.assertEqual(frame.iloc[0].tolist(), ["甲", 100])

    async def test_real_size_boundary(self):
        self.assertEqual(MAX_FILE_SIZE, 20 * 1024 * 1024)
        # A valid one-column CSV exactly at the byte limit; no disk fixture.
        content = b"value\n" + b"x" * (MAX_FILE_SIZE - 7) + b"\n"
        self.assertEqual(len(content), MAX_FILE_SIZE)
        self.assertEqual((await self.read(content)).shape, (1, 1))
        with self.assertRaises(HTTPException) as caught:
            await self.read(content + b"x")
        self.assertEqual(caught.exception.status_code, 413)
        self.assertEqual(caught.exception.detail, "上传的 CSV 文件不能超过 20MB")

    async def test_header_only_current_behavior(self):
        frame = await self.read(b"name,sales\n")
        self.assertEqual(frame.shape, (0, 2))
        self.assertEqual(analyze_dataframe(frame)["quality_score"], 100)


class AnalysisBaselineTests(unittest.TestCase):
    def test_statistics_and_result_fields(self):
        result = analyze_dataframe(pd.DataFrame({"name": ["A", "B", "C", "D"],
                                                 "sales": [100, 200, 300, 400]}))
        self.assertEqual(set(result), {
            "rows", "columns", "column_names", "data_types", "missing_values",
            "missing_rate", "duplicate_rows", "outliers", "quality_score",
            "unique_values", "numeric_summary", "preview",
        })
        self.assertEqual((result["rows"], result["columns"]), (4, 2))
        self.assertEqual(result["column_names"], ["name", "sales"])
        self.assertEqual(result["unique_values"], {"name": 4, "sales": 4})
        summary = result["numeric_summary"]["sales"]
        self.assertEqual(set(summary), {"sum", "mean", "min", "max", "std"})
        self.assertEqual([summary[key] for key in ["sum", "mean", "min", "max"]],
                         [1000, 250, 100, 400])
        self.assertAlmostEqual(summary["std"], 129.09944487358055)
        self.assertEqual(result["quality_score"], 100)
        self.assertEqual(result["outliers"]["sales"],
                         {"count": 0, "values": [], "lower_bound": -50.0, "upper_bound": 550.0})
        json.dumps(result, allow_nan=False)

    def test_missing_duplicate_outlier_and_preview(self):
        result = analyze_dataframe(pd.DataFrame({
            "name": ["A", "A", None, "B", "C", "D"],
            "sales": [1, 1, 2, 3, 4, 100],
        }))
        self.assertEqual(result["missing_values"]["name"], 1)
        self.assertEqual(result["missing_rate"]["name"], 16.67)
        self.assertEqual(result["duplicate_rows"], 1)
        self.assertEqual(result["outliers"]["sales"]["values"], [100.0])
        self.assertEqual(result["quality_score"], 86)
        self.assertEqual(len(result["preview"]), 5)
        self.assertIsNone(result["preview"][2]["name"])
        insight = generate_insights(result)
        self.assertEqual(set(insight), {"summary", "quality", "warnings", "recommendations"})
        self.assertEqual(len(insight["warnings"]), 3)
        self.assertEqual(len(insight["recommendations"]), 3)
        json.dumps(result, allow_nan=False)

    def test_small_numeric_sample_and_nan(self):
        result = analyze_dataframe(pd.DataFrame({"value": [1.0, None]}))
        self.assertEqual(result["outliers"]["value"], {"count": 0, "values": []})
        self.assertIsNone(result["numeric_summary"]["value"]["std"])
        self.assertIsNone(safe_float(float("nan")))
        self.assertEqual(result["quality_score"], 80)
        json.dumps(result, allow_nan=False)

    def test_quality_score_floor(self):
        result = analyze_dataframe(pd.DataFrame({"value": [1] * 60}))
        self.assertEqual(result["quality_score"], 0)

    def test_unique_counts_exclude_nulls_and_count_distinct_values(self):
        result = analyze_dataframe(pd.DataFrame({
            "repeated": ["A", "A", "B", None],
            "distinct": [1, 2, 3, 4],
            "empty": [None, None, None, None],
        }))
        self.assertEqual(result["unique_values"], {"repeated": 2, "distinct": 4, "empty": 0})
        self.assertNotIn("unique_counts", result)
        self.assertEqual(result["missing_values"], {"repeated": 1, "distinct": 0, "empty": 4})

    def test_clean_rule_insights(self):
        insight = generate_insights(analyze_dataframe(pd.DataFrame({"value": [1, 2, 3]})))
        self.assertEqual(insight["warnings"], ["当前未发现明显的数据质量问题。"])
        self.assertEqual(insight["recommendations"], ["当前数据质量较好，可以继续进行后续的数据分析。"])


if __name__ == "__main__":
    unittest.main()
