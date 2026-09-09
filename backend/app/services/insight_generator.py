def generate_insights(analysis: dict) -> dict:
    """
    根据数据分析结果生成结构化的数据洞察。
    """

    # =========================
    # 1. 基础信息
    # =========================

    rows = analysis.get("rows", 0)
    columns = analysis.get("columns", 0)

    summary = (
        f"数据集共有 {rows} 行、{columns} 列。"
    )

    # =========================
    # 2. 数据质量
    # =========================

    quality_score = analysis.get("quality_score", 100)

    if quality_score >= 90:
        quality_message = "整体数据质量较好。"
    elif quality_score >= 70:
        quality_message = "整体数据质量一般，建议进一步检查数据。"
    else:
        quality_message = "整体数据质量较差，建议优先进行数据清洗。"

    quality = (
        f"数据质量评分为 {quality_score} 分，"
        f"{quality_message}"
    )

    # =========================
    # 3. 问题发现
    # =========================

    warnings = []

    # ---- 缺失值 ----

    missing_rate = analysis.get("missing_rate", {})

    for column, rate in missing_rate.items():
        if rate >= 20:
            warnings.append(
                f"字段「{column}」存在较严重的缺失问题，"
                f"缺失率为 {rate}%。"
            )

        elif rate > 0:
            warnings.append(
                f"字段「{column}」存在少量缺失数据，"
                f"缺失率为 {rate}%。"
            )

    # ---- 重复数据 ----

    duplicate_rows = analysis.get("duplicate_rows", 0)

    if duplicate_rows > 0:
        warnings.append(
            f"数据中检测到 {duplicate_rows} 条重复记录。"
        )

    # ---- 异常值 ----

    outliers = analysis.get("outliers", {})

    for column, result in outliers.items():
        count = result.get("count", 0)
        values = result.get("values", [])

        if count > 0:
            warnings.append(
                f"字段「{column}」检测到 {count} 个异常值，"
                f"异常值包括：{values}。"
            )

    # 如果没有发现问题
    if not warnings:
        warnings.append(
            "当前未发现明显的数据质量问题。"
        )

    # =========================
    # 4. 建议
    # =========================

    recommendations = []

    # 缺失值建议
    for column, rate in missing_rate.items():
        if rate > 0:
            recommendations.append(
                f"建议检查字段「{column}」的缺失记录，"
                f"根据业务情况进行填充或删除。"
            )

    # 重复数据建议
    if duplicate_rows > 0:
        recommendations.append(
            "建议检查重复记录，并根据业务规则决定是否去重。"
        )

    # 异常值建议
    for column, result in outliers.items():
        if result.get("count", 0) > 0:
            recommendations.append(
                f"建议检查字段「{column}」中的异常值，"
                f"确认是否属于录入错误或真实业务情况。"
            )

    # 没有问题时给出通用建议
    if not recommendations:
        recommendations.append(
            "当前数据质量较好，可以继续进行后续的数据分析。"
        )

    # =========================
    # 5. 返回结构化洞察
    # =========================

    return {
        "summary": summary,
        "quality": quality,
        "warnings": warnings,
        "recommendations": recommendations,
    }