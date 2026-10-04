from io import StringIO

import pandas as pd
from fastapi import HTTPException, UploadFile


MAX_FILE_SIZE = 20 * 1024 * 1024


async def read_csv_file(file: UploadFile) -> pd.DataFrame:
    """
    读取并校验上传的 CSV 文件。
    """

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

        # 4. 检查文件大小
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="上传的 CSV 文件不能超过 20MB",
            )

        # 5. 检查文件是否为空
        if not content:
            raise HTTPException(
                status_code=400,
                detail="上传的 CSV 文件为空",
            )

        # 6. 使用 Pandas 读取 CSV
        df = pd.read_csv(
            StringIO(content.decode("utf-8"))
        )

        return df

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
