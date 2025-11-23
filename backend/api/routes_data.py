# backend/api/routes_data.py

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
from typing import Literal, List, Optional
from datetime import date, datetime

from data.repository import repo

router = APIRouter()


class CalendarEvent(BaseModel):
    date: date
    stack_id: str
    kind: Literal["prediction", "actual"]


@router.get("/stacks")
async def get_stacks():
    """
    Возвращает «сырую» таблицу supplies в виде списка объектов.
    Для фронта этого обычно достаточно для первого приближения.
    """
    if repo.supplies is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Данные supplies не загружены",
        )

    # Просто отдаём DataFrame как список словарей
    return repo.supplies.to_dict(orient="records")


@router.get("/calendar", response_model=List[CalendarEvent])
async def get_calendar(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
):
    """
    Объединяет фактические пожары (fires) и прогнозы (predictions)
    в единую ленту событий для календаря.
    """
    events: list[CalendarEvent] = []

    # Фактические возгорания
    if repo.fires is not None:
        fires_df = repo.fires.copy()
        # Предполагаем, что в fires.csv есть колонки с датой и stack_id.
        # Названия колонок ты подставишь реальными.
        # Пример: 'stack_id', 'fire_start_date'
        if {"stack_id", "fire_start_date"}.issubset(fires_df.columns):
            fires_df["fire_start_date"] = pd.to_datetime(
                fires_df["fire_start_date"]
            ).dt.date

            for _, row in fires_df.iterrows():
                d = row["fire_start_date"]
                if start_date and d < start_date:
                    continue
                if end_date and d > end_date:
                    continue
                events.append(
                    CalendarEvent(
                        date=d,
                        stack_id=str(row["stack_id"]),
                        kind="actual",
                    )
                )

    # Прогнозы
    if repo.predictions is not None:
        preds_df = repo.predictions.copy()
        if {"stack_id", "predicted_fire_date"}.issubset(preds_df.columns):
            preds_df["predicted_fire_date"] = pd.to_datetime(
                preds_df["predicted_fire_date"]
            ).dt.date

            for _, row in preds_df.iterrows():
                d = row["predicted_fire_date"]
                if start_date and d < start_date:
                    continue
                if end_date and d > end_date:
                    continue
                events.append(
                    CalendarEvent(
                        date=d,
                        stack_id=str(row["stack_id"]),
                        kind="prediction",
                    )
                )

    return events
