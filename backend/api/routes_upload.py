import io
from enum import Enum

import pandas as pd
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from data.repository import repo

from core.config import get_db
from data.repository import DataRepository

router = APIRouter(prefix="/upload", tags=["upload"])


class DataType(str, Enum):
    supplies = "supplies"
    weather = "weather"
    temperature = "temperature"


@router.post("/{data_type}")
async def upload_csv(
    data_type: DataType,
    file: UploadFile = File(...),
):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Ожидается файл в формате .csv")

    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Не удалось прочитать CSV: {e}")

    if df.empty:
        raise HTTPException(status_code=400, detail="Файл не содержит данных")

    if data_type == DataType.supplies:
        n_rows = repo.upload_supplies(df)
    elif data_type == DataType.weather:
        n_rows = repo.upload_weather(df)
    elif data_type == DataType.temperature:
        n_rows = repo.upload_temperature(df)
    else:
        raise HTTPException(status_code=400, detail="Неизвестный тип данных")

    return {
        "status": "ok",
        "data_type": data_type,
        "rows_added": n_rows,
    }
