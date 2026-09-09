import pandas as pd


def safe_float(value):
    """
    将 Pandas 数值安全转换成 Python float。
    如果结果是 NaN 或无穷大，则返回 None。
    """
    if pd.isna(value):
        return None

    return float(value)


def analyze_dataframe(df: pd.DataFrame) -> dict:
    """
    分析 DataFrame，返回数据概览信息：

    - 行数
    - 列数
    - 列名
    - 数据类型
    - 缺失值
    - 唯一值数量
    - 数值列统计
    - 前5行数据
    """

    # =========================
    # 1. 数值列统计
    # =========================

    numeric_summary = {}

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns

    for column in numeric_columns:
        series = df[column]

        numeric_summary[column] = {
            "sum": safe_float(series.sum()),
            "mean": safe_float(series.mean()),
            "min": safe_float(series.min()),
            "max": safe_float(series.max()),
            "std": safe_float(series.std()),
        }

    # =========================
    # 2. 数据预览
    # =========================

    preview_df = (
        df.head(5)
        .astype(object)
        .where(pd.notna(df.head(5)), None)
    )

    # =========================
    # 3. 返回分析结果
    # =========================
    # =========================
    # 3. 数据质量分析
    # =========================
        

    total_rows = len(df)

    missing_rate = {}

    for column in df.columns:
        missing_count = int(df[column].isnull().sum())

        if total_rows > 0:
            rate = missing_count / total_rows * 100
        else:
            rate = 0

        missing_rate[column] = round(rate, 2)
        # 重复行数量
        duplicate_rows = int(df.duplicated().sum())

            # =========================
    # 4. IQR 异常值检测
    # =========================

    outliers = {}

    for column in numeric_columns:
        series = df[column].dropna()

        # 数据太少时，不进行异常值判断
        if len(series) < 4:
            outliers[column] = {
                "count": 0,
                "values": [],
            }
            continue

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)

        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outlier_series = series[
            (series < lower_bound)
            | (series > upper_bound)
        ]

        outliers[column] = {
            "count": int(len(outlier_series)),
            "values": [
                safe_float(value)
                for value in outlier_series.tolist()
            ],
            "lower_bound": safe_float(lower_bound),
            "upper_bound": safe_float(upper_bound),
        }
                # =========================
    # 5. 数据质量评分
    # =========================

    quality_score = 100

    # 缺失值扣分
    for column, rate in missing_rate.items():
        if rate > 0:
            quality_score -= 10

        if rate >= 20:
            quality_score -= 10

    # 重复数据扣分
    quality_score -= duplicate_rows * 2

    # 异常值扣分
    for column, result in outliers.items():
        quality_score -= result["count"] * 2

    # 保证分数不会低于 0
    quality_score = max(0, quality_score)




    return {
        "rows": int(df.shape[0]),

        "columns": int(df.shape[1]),

        "column_names": df.columns.tolist(),

        "data_types": {
            column: str(dtype)
            for column, dtype in df.dtypes.items()
        },

        "missing_values": {
            column: int(count)
            for column, count in df.isnull().sum().items()
        },
                "missing_rate": missing_rate,

                "duplicate_rows": duplicate_rows,

                "outliers": outliers,

                "quality_score": quality_score,

        "unique_values": {
            column: int(df[column].nunique())
            for column in df.columns
        },

        "numeric_summary": numeric_summary,

        "preview": preview_df.to_dict(
            orient="records"
        ),
    }