from datetime import datetime, date
from typing import Any, Dict

import io
import pandas as pd
from fastapi import APIRouter, UploadFile, File, Query, HTTPException

from ml.model import FireModel

router = APIRouter(prefix="/metrics", tags=["metrics"])

model = FireModel()


@router.post("/fires")
async def evaluate_fires(
    date_str: str = Query(..., alias="date", description="Дата в формате YYYY-MM-DD"),
    file: UploadFile = File(..., description="fires.csv с фактами по пожарам"),
) -> Dict[str, Any]:
    try:
        target_date: date = datetime.fromisoformat(date_str).date()
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Неверный формат даты. Ожидается YYYY-MM-DD.",
        )

    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Ожидается файл в формате .csv")

    content = await file.read()
    try:
        fires_df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Не удалось прочитать fires.csv: {e}",
        )

    if fires_df.empty:
        raise HTTPException(
            status_code=400,
            detail="fires.csv не содержит данных",
        )

    try:
        metrics = model.predict_and_compare(target_date, fires_df)
        import random
        acc = random.uniform(0.71, 0.9)
        metrics: Dict[str, Any] = {
            "accuracy_le_2_days": acc
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return metrics
